"""
Full workspace data export.

Produces a ZIP archive containing one CSV per entity type (leads, customers,
sales, expenses).  Used for data portability — customers migrating away from
QuickBooks / HubSpot to LBT OS as their primary system.
"""
from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime, timezone
from typing import Any

from supabase import Client


def _now_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _rows_to_csv(rows: list[dict[str, Any]], fields: list[str]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: (row.get(k) or "") for k in fields})
    return buf.getvalue().encode("utf-8")


_LEAD_FIELDS = [
    "name", "email", "phone", "source", "status", "service_interest",
    "estimated_value", "notes", "assigned_to",
    "follow_up_at", "contacted_at", "converted_at", "lost_reason",
    "created_at", "updated_at",
]
_CUSTOMER_FIELDS = [
    "name", "email", "phone", "address", "tags",
    "lifetime_value", "total_orders", "last_purchase_at", "notes",
    "created_at", "updated_at",
]
_SALE_FIELDS = [
    "service", "amount", "cost", "profit",
    "payment_method", "payment_status", "source",
    "invoice_number", "notes", "sold_at", "created_at",
]
_EXPENSE_FIELDS = [
    "category", "description", "amount", "vendor",
    "is_recurring", "recurrence_period", "expense_date", "created_at",
]


def build_workspace_zip(db: Client, org_id: str) -> bytes:
    """Return the raw bytes of a ZIP archive containing all org data as CSVs."""

    def _fetch(table: str, order_col: str) -> list[dict[str, Any]]:
        result = (
            db.table(table)
            .select("*")
            .eq("org_id", org_id)
            .order(order_col, desc=False)
            .execute()
        )
        return result.data or []

    leads     = _fetch("leads",     "created_at")
    customers = _fetch("customers", "created_at")
    sales     = _fetch("sales",     "sold_at")
    expenses  = _fetch("expenses",  "expense_date")

    # Flatten tags array for CSV
    for c in customers:
        tags = c.get("tags") or []
        c["tags"] = ", ".join(tags) if isinstance(tags, list) else (tags or "")

    label = _now_label()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"leads-{label}.csv",     _rows_to_csv(leads,     _LEAD_FIELDS))
        zf.writestr(f"customers-{label}.csv", _rows_to_csv(customers, _CUSTOMER_FIELDS))
        zf.writestr(f"sales-{label}.csv",     _rows_to_csv(sales,     _SALE_FIELDS))
        zf.writestr(f"expenses-{label}.csv",  _rows_to_csv(expenses,  _EXPENSE_FIELDS))
        zf.writestr("README.txt", _readme(label, leads, customers, sales, expenses))
    buf.seek(0)
    return buf.read()


def _readme(
    label: str,
    leads: list, customers: list, sales: list, expenses: list,
) -> str:
    return f"""LBT OS — Workspace Data Export
Generated: {label}

Files in this archive:
  leads-{label}.csv     — {len(leads)} leads
  customers-{label}.csv — {len(customers)} customers
  sales-{label}.csv     — {len(sales)} sales / revenue records
  expenses-{label}.csv  — {len(expenses)} expense records

These CSVs can be re-imported into any LBT OS workspace using the
Manual CSV Import feature on the Connections page.

Column reference: https://docs.lbt-os.com/data-export
"""
