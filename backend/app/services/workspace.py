from __future__ import annotations

from typing import Any

from supabase import Client

from .templates import get_template


def _safe_optional_select(query, default):
    try:
        result = query.execute()
        return result.data or default
    except Exception as exc:
        if "Could not find the table" in str(exc):
            return default
        raise


def get_workspace_status_payload(db: Client, org_id: str) -> dict[str, Any] | None:
    org = (
        db.table("organizations")
        .select("id, name, industry, plan, onboarding_complete")
        .eq("id", org_id)
        .single()
        .execute()
    )
    if not org.data:
        return None

    counts = {
        "leads": len(db.table("leads").select("id").eq("org_id", org_id).limit(1).execute().data or []),
        "customers": len(db.table("customers").select("id").eq("org_id", org_id).limit(1).execute().data or []),
        "sales": len(db.table("sales").select("id").eq("org_id", org_id).limit(1).execute().data or []),
        "expenses": len(db.table("expenses").select("id").eq("org_id", org_id).limit(1).execute().data or []),
    }
    total_record_types = sum(counts.values())

    connection_rows = _safe_optional_select(
        db.table("integration_connections")
        .select("id, provider, last_synced_at, status")
        .eq("org_id", org_id)
        .neq("status", "disconnected")
        .limit(10),
        [],
    )
    connection_count = len(connection_rows)

    latest_sync_rows = _safe_optional_select(
        db.table("integration_sync_runs")
        .select("id, provider, status, started_at, finished_at, stats, error, trigger_source")
        .eq("org_id", org_id)
        .order("started_at", desc=True)
        .limit(1),
        [],
    )
    latest_audit = (
        db.table("audit_reports")
        .select("id, health_score, generated_at, period_start, period_end, model_used")
        .eq("org_id", org_id)
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )
    template = get_template(org.data.get("industry"))

    if connection_count > 0 and total_record_types > 0:
        workspace_mode = "live"
    elif connection_count == 0 and total_record_types > 0:
        workspace_mode = "demo"
    else:
        workspace_mode = "blank"

    return {
        "organization": org.data,
        "template": template,
        "latest_sync": latest_sync_rows[0] if latest_sync_rows else None,
        "latest_audit": latest_audit.data[0] if latest_audit.data else None,
        "workspace_mode": workspace_mode,
        "has_connections": connection_count > 0,
        "record_type_counts": counts,
    }
