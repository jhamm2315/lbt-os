"""
Revenue Intelligence — analytical functions for CRM pipeline health.

When an org has no real data yet, each function returns a seeded demo dataset
so the dashboard is always operable and testable.  The demo flag is surfaced
in every response as  `"is_demo": True`  so the UI can show a banner.
"""
from datetime import datetime, timedelta, timezone
from typing import Any


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Demo data — shown when the org has no real records yet
# ---------------------------------------------------------------------------

def _demo_ltv() -> dict[str, Any]:
    return {
        "is_demo": True,
        "total_customers": 12,
        "avg_ltv": 3_840.0,
        "total_revenue": 46_080.0,
        "top_customers": [
            {"id": "demo-1", "name": "Frontier Outdoor Goods",    "lifetime_value": 9_200.0, "total_orders": 7, "last_purchase_at": None},
            {"id": "demo-2", "name": "Mesa Labs",                  "lifetime_value": 7_100.0, "total_orders": 5, "last_purchase_at": None},
            {"id": "demo-3", "name": "Alpine Industrial",          "lifetime_value": 5_400.0, "total_orders": 4, "last_purchase_at": None},
            {"id": "demo-4", "name": "Peak Packaging Co",          "lifetime_value": 4_800.0, "total_orders": 6, "last_purchase_at": None},
            {"id": "demo-5", "name": "Terra Build Systems",        "lifetime_value": 3_950.0, "total_orders": 3, "last_purchase_at": None},
            {"id": "demo-6", "name": "Blue Pine Manufacturing",    "lifetime_value": 3_200.0, "total_orders": 3, "last_purchase_at": None},
            {"id": "demo-7", "name": "Range Supply Group",         "lifetime_value": 2_900.0, "total_orders": 2, "last_purchase_at": None},
            {"id": "demo-8", "name": "Summit AgTech",              "lifetime_value": 2_650.0, "total_orders": 4, "last_purchase_at": None},
            {"id": "demo-9", "name": "Evergreen Fabrication",      "lifetime_value": 2_480.0, "total_orders": 2, "last_purchase_at": None},
            {"id": "demo-10","name": "Canyon Process Works",        "lifetime_value": 1_920.0, "total_orders": 2, "last_purchase_at": None},
        ],
    }


def _demo_stage_velocity() -> dict[str, Any]:
    return {
        "is_demo": True,
        "days_analyzed": 90,
        "stages": [
            {"stage": "new",       "avg_hours": 18.4, "avg_days": 0.8,  "sample_size": 24},
            {"stage": "contacted", "avg_hours": 52.1, "avg_days": 2.2,  "sample_size": 19},
            {"stage": "qualified", "avg_hours": 89.6, "avg_days": 3.7,  "sample_size": 14},
            {"stage": "proposal",  "avg_hours": 148.3,"avg_days": 6.2,  "sample_size": 9},
        ],
    }


def _demo_win_loss() -> dict[str, Any]:
    return {
        "is_demo": True,
        "days_analyzed": 90,
        "cohorts": [
            {"source": "referral", "won": 11, "lost": 3,  "total": 14, "win_rate": 78.6},
            {"source": "google",   "won": 8,  "lost": 5,  "total": 13, "win_rate": 61.5},
            {"source": "website",  "won": 6,  "lost": 6,  "total": 12, "win_rate": 50.0},
            {"source": "social",   "won": 3,  "lost": 7,  "total": 10, "win_rate": 30.0},
            {"source": "yelp",     "won": 2,  "lost": 5,  "total": 7,  "win_rate": 28.6},
        ],
    }


def _demo_data_quality() -> dict[str, Any]:
    return {
        "is_demo": True,
        "overall_score": 67.4,
        "grade": "B",
        "lead_count": 38,
        "customer_count": 12,
        "sale_count": 29,
        "fields": [
            {"entity": "leads",     "field": "email",           "pct": 71.1},
            {"entity": "leads",     "field": "phone",           "pct": 84.2},
            {"entity": "leads",     "field": "source",          "pct": 92.1},
            {"entity": "leads",     "field": "estimated_value", "pct": 55.3},
            {"entity": "leads",     "field": "assigned_to",     "pct": 60.5},
            {"entity": "customers", "field": "email",           "pct": 83.3},
            {"entity": "customers", "field": "phone",           "pct": 75.0},
            {"entity": "customers", "field": "city",            "pct": 66.7},
            {"entity": "customers", "field": "lifetime_value",  "pct": 100.0},
            {"entity": "sales",     "field": "customer_id",     "pct": 89.7},
            {"entity": "sales",     "field": "product_name",    "pct": 96.6},
        ],
    }


def _demo_expansion_signals() -> dict[str, Any]:
    return {
        "is_demo": True,
        "count": 4,
        "signals": [
            {"id": "demo-1", "name": "Frontier Outdoor Goods", "email": "accounts@frontier.example",  "lifetime_value": 9200.0, "total_orders": 7, "days_inactive": 97,  "last_purchase_at": None},
            {"id": "demo-3", "name": "Alpine Industrial",       "email": "orders@alpine.example",     "lifetime_value": 5400.0, "total_orders": 4, "days_inactive": 112, "last_purchase_at": None},
            {"id": "demo-6", "name": "Blue Pine Manufacturing", "email": "billing@bluepine.example",  "lifetime_value": 3200.0, "total_orders": 3, "days_inactive": 134, "last_purchase_at": None},
            {"id": "demo-8", "name": "Summit AgTech",           "email": "ap@summitagtech.example",   "lifetime_value": 2650.0, "total_orders": 4, "days_inactive": 108, "last_purchase_at": None},
        ],
    }


def _demo_speed_to_lead() -> dict[str, Any]:
    return {
        "is_demo": True,
        "days_analyzed": 30,
        "overall_avg_hours": 6.3,
        "by_source": [
            {"source": "referral", "avg_hours": 2.1, "sample_size": 8},
            {"source": "google",   "avg_hours": 4.8, "sample_size": 11},
            {"source": "website",  "avg_hours": 7.2, "sample_size": 7},
            {"source": "social",   "avg_hours": 14.6,"sample_size": 5},
            {"source": "yelp",     "avg_hours": 19.3,"sample_size": 3},
        ],
    }


def _demo_stage_aging() -> dict[str, Any]:
    return {
        "is_demo": True,
        "total_open": 21,
        "stages": [
            {"stage": "new",       "count": 7, "avg_days_in_stage": 3.1, "stale_count": 1},
            {"stage": "contacted", "count": 6, "avg_days_in_stage": 8.4, "stale_count": 2},
            {"stage": "qualified", "count": 5, "avg_days_in_stage": 12.7,"stale_count": 3},
            {"stage": "proposal",  "count": 3, "avg_days_in_stage": 21.0,"stale_count": 3},
        ],
    }


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def get_ltv_metrics(db, org_id: str) -> dict[str, Any]:
    customers = (
        db.table("customers")
        .select("id, name, lifetime_value, total_orders, last_purchase_at")
        .eq("org_id", org_id)
        .order("lifetime_value", desc=True)
        .limit(200)
        .execute()
        .data or []
    )
    if not customers:
        return _demo_ltv()

    total_revenue = sum(float(c.get("lifetime_value") or 0) for c in customers)
    avg_ltv = total_revenue / len(customers)
    return {
        "total_customers": len(customers),
        "avg_ltv": round(avg_ltv, 2),
        "total_revenue": round(total_revenue, 2),
        "top_customers": [
            {
                "id": c["id"],
                "name": c["name"],
                "lifetime_value": float(c.get("lifetime_value") or 0),
                "total_orders": int(c.get("total_orders") or 0),
                "last_purchase_at": c.get("last_purchase_at"),
            }
            for c in customers[:10]
        ],
    }


def get_stage_velocity(db, org_id: str, days: int = 90) -> dict[str, Any]:
    cutoff = (_now() - timedelta(days=days)).isoformat()
    history = (
        db.table("lead_stage_history")
        .select("lead_id, from_status, to_status, changed_at")
        .eq("org_id", org_id)
        .gte("changed_at", cutoff)
        .order("lead_id")
        .order("changed_at")
        .execute()
        .data or []
    )

    lead_events: dict[str, list] = {}
    for h in history:
        lead_events.setdefault(h["lead_id"], []).append(h)

    stage_hours: dict[str, list[float]] = {}
    for events in lead_events.values():
        for i in range(1, len(events)):
            stage = events[i - 1]["to_status"]
            t0 = _parse_dt(events[i - 1]["changed_at"])
            t1 = _parse_dt(events[i]["changed_at"])
            if t0 and t1:
                hours = (t1 - t0).total_seconds() / 3600
                if 0 < hours < 720:
                    stage_hours.setdefault(stage, []).append(hours)

    order = ["new", "contacted", "qualified", "proposal", "won", "lost"]
    velocity = []
    for stage, hours_list in stage_hours.items():
        avg = sum(hours_list) / len(hours_list)
        velocity.append({
            "stage": stage,
            "avg_hours": round(avg, 1),
            "avg_days": round(avg / 24, 1),
            "sample_size": len(hours_list),
        })
    velocity.sort(key=lambda x: order.index(x["stage"]) if x["stage"] in order else 99)
    if not velocity:
        return _demo_stage_velocity()
    return {"days_analyzed": days, "stages": velocity}


def get_win_loss_cohort(db, org_id: str, days: int = 90) -> dict[str, Any]:
    cutoff = (_now() - timedelta(days=days)).isoformat()
    leads = (
        db.table("leads")
        .select("source, status")
        .eq("org_id", org_id)
        .gte("created_at", cutoff)
        .in_("status", ["won", "lost"])
        .execute()
        .data or []
    )

    cohorts: dict[str, dict[str, int]] = {}
    for lead in leads:
        src = lead.get("source") or "unknown"
        cohorts.setdefault(src, {"won": 0, "lost": 0})
        cohorts[src][lead["status"]] = cohorts[src].get(lead["status"], 0) + 1

    result = []
    for source, counts in cohorts.items():
        won = counts.get("won", 0)
        lost = counts.get("lost", 0)
        total = won + lost
        result.append({
            "source": source,
            "won": won,
            "lost": lost,
            "total": total,
            "win_rate": round(won / total * 100, 1) if total else 0,
        })
    result.sort(key=lambda x: x["win_rate"], reverse=True)
    if not result:
        return _demo_win_loss()
    return {"days_analyzed": days, "cohorts": result}


def get_data_quality_scorecard(db, org_id: str) -> dict[str, Any]:
    leads = (
        db.table("leads")
        .select("email, phone, source, estimated_value, assigned_to")
        .eq("org_id", org_id)
        .limit(500)
        .execute()
        .data or []
    )
    customers = (
        db.table("customers")
        .select("email, phone, city, lifetime_value")
        .eq("org_id", org_id)
        .limit(500)
        .execute()
        .data or []
    )
    sales = (
        db.table("sales")
        .select("customer_id, lead_id, product_name")
        .eq("org_id", org_id)
        .limit(500)
        .execute()
        .data or []
    )

    def pct(rows: list, field: str) -> float:
        if not rows:
            return 0.0
        filled = sum(1 for r in rows if r.get(field) not in (None, ""))
        return round(filled / len(rows) * 100, 1)

    fields = []
    if leads:
        fields += [
            {"entity": "leads", "field": "email",           "pct": pct(leads, "email")},
            {"entity": "leads", "field": "phone",           "pct": pct(leads, "phone")},
            {"entity": "leads", "field": "source",          "pct": pct(leads, "source")},
            {"entity": "leads", "field": "estimated_value", "pct": pct(leads, "estimated_value")},
            {"entity": "leads", "field": "assigned_to",     "pct": pct(leads, "assigned_to")},
        ]
    if customers:
        fields += [
            {"entity": "customers", "field": "email",          "pct": pct(customers, "email")},
            {"entity": "customers", "field": "phone",          "pct": pct(customers, "phone")},
            {"entity": "customers", "field": "city",           "pct": pct(customers, "city")},
            {"entity": "customers", "field": "lifetime_value", "pct": pct(customers, "lifetime_value")},
        ]
    if sales:
        fields += [
            {"entity": "sales", "field": "customer_id",  "pct": pct(sales, "customer_id")},
            {"entity": "sales", "field": "product_name", "pct": pct(sales, "product_name")},
        ]

    if not fields:
        return _demo_data_quality()
    overall = round(sum(f["pct"] for f in fields) / len(fields), 1)
    grade = "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D"
    return {
        "overall_score": overall,
        "grade": grade,
        "lead_count": len(leads),
        "customer_count": len(customers),
        "sale_count": len(sales),
        "fields": fields,
    }


def get_expansion_signals(db, org_id: str) -> dict[str, Any]:
    cutoff = (_now() - timedelta(days=90)).isoformat()
    customers = (
        db.table("customers")
        .select("id, name, email, lifetime_value, total_orders, last_purchase_at")
        .eq("org_id", org_id)
        .lt("last_purchase_at", cutoff)
        .order("lifetime_value", desc=True)
        .limit(20)
        .execute()
        .data or []
    )

    now = _now()
    signals = []
    for c in customers:
        lp = _parse_dt(c.get("last_purchase_at"))
        signals.append({
            "id": c["id"],
            "name": c["name"],
            "email": c.get("email"),
            "lifetime_value": float(c.get("lifetime_value") or 0),
            "total_orders": int(c.get("total_orders") or 0),
            "days_inactive": (now - lp).days if lp else None,
            "last_purchase_at": c.get("last_purchase_at"),
        })
    if not signals:
        return _demo_expansion_signals()
    return {"signals": signals, "count": len(signals)}


def get_speed_to_lead(db, org_id: str, days: int = 30) -> dict[str, Any]:
    cutoff = (_now() - timedelta(days=days)).isoformat()
    leads = (
        db.table("leads")
        .select("source, created_at, contacted_at")
        .eq("org_id", org_id)
        .gte("created_at", cutoff)
        .not_.is_("contacted_at", "null")
        .execute()
        .data or []
    )

    source_times: dict[str, list[float]] = {}
    for lead in leads:
        t0 = _parse_dt(lead.get("created_at"))
        t1 = _parse_dt(lead.get("contacted_at"))
        if t0 and t1:
            hours = (t1 - t0).total_seconds() / 3600
            if hours >= 0:
                source_times.setdefault(lead.get("source") or "unknown", []).append(hours)

    result = []
    for source, times in source_times.items():
        avg = sum(times) / len(times)
        result.append({"source": source, "avg_hours": round(avg, 1), "sample_size": len(times)})
    result.sort(key=lambda x: x["avg_hours"])

    total_sample = sum(r["sample_size"] for r in result)
    overall_avg = (
        sum(r["avg_hours"] * r["sample_size"] for r in result) / total_sample
        if total_sample else None
    )
    if not result:
        return _demo_speed_to_lead()
    return {
        "days_analyzed": days,
        "overall_avg_hours": round(overall_avg, 1) if overall_avg is not None else None,
        "by_source": result,
    }


def get_stage_aging(db, org_id: str) -> dict[str, Any]:
    open_statuses = ["new", "contacted", "qualified", "proposal"]
    leads = (
        db.table("leads")
        .select("status, stage_changed_at, created_at")
        .eq("org_id", org_id)
        .in_("status", open_statuses)
        .execute()
        .data or []
    )

    now = _now()
    stage_data: dict[str, list[float]] = {}
    for lead in leads:
        ref = _parse_dt(lead.get("stage_changed_at") or lead.get("created_at"))
        if ref:
            stage_data.setdefault(lead["status"], []).append((now - ref).days)

    result = []
    for stage in open_statuses:
        days_list = stage_data.get(stage, [])
        result.append({
            "stage": stage,
            "count": len(days_list),
            "avg_days_in_stage": round(sum(days_list) / len(days_list), 1) if days_list else 0,
            "stale_count": sum(1 for d in days_list if d > 14),
        })
    total_open = sum(r["count"] for r in result)
    if total_open == 0:
        return _demo_stage_aging()
    return {"stages": result, "total_open": total_open}
