"""
Metrics aggregation service.

All metrics are computed from raw Supabase data. This service is the
single source of truth for dashboard numbers and the free analyst brief.
"""
from datetime import date, timedelta
from typing import Any

from supabase import Client


INDUSTRY_BENCHMARKS: dict[str, dict[str, float | str]] = {
    "hvac": {"conversion": 28.0, "margin": 32.0, "repeat": 24.0, "note": "HVAC operators usually win by tightening follow-up speed and seasonal repeat work."},
    "plumbing": {"conversion": 30.0, "margin": 34.0, "repeat": 26.0, "note": "Strong plumbing shops usually defend margin through pricing discipline and repeat service calls."},
    "electrician": {"conversion": 27.0, "margin": 33.0, "repeat": 22.0, "note": "Electricians usually improve profit by separating emergency jobs from scheduled work and protecting labor margin."},
    "landscaping": {"conversion": 25.0, "margin": 29.0, "repeat": 44.0, "note": "Landscaping businesses usually win on recurring contracts, route efficiency, and seasonal upsells."},
    "cleaning_service": {"conversion": 31.0, "margin": 27.0, "repeat": 52.0, "note": "Cleaning businesses usually perform best when repeat schedules and crew utilization are tightly managed."},
    "gig_worker": {"conversion": 36.0, "margin": 41.0, "repeat": 34.0, "note": "Solo operators usually grow fastest by protecting take-home margin and doubling down on the highest-paying service mix."},
    "salon_spa": {"conversion": 34.0, "margin": 30.0, "repeat": 58.0, "note": "Salon and spa operators usually rely on rebooking rate, service mix, and recurring client value."},
    "restaurant": {"conversion": 0.0, "margin": 14.0, "repeat": 38.0, "note": "Restaurants typically rely on retention, table turns, and tight cost control more than lead conversion."},
    "gym": {"conversion": 24.0, "margin": 26.0, "repeat": 55.0, "note": "Fitness businesses win on retention, recurring revenue, and member reactivation."},
    "real_estate": {"conversion": 18.0, "margin": 42.0, "repeat": 12.0, "note": "Real estate teams usually care most about lead quality, close rate, and referral momentum."},
}


def _sum(rows: list[dict], key: str) -> float:
    return round(sum(float(r.get(key) or 0) for r in rows), 2)


def _pct_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None if current == 0 else 100.0
    return round(((current - previous) / previous) * 100, 1)


def _label_change(current: float, previous: float, unit: str = "%") -> str:
    delta = round(current - previous, 1)
    if unit == "%":
        direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
        return f"{direction} {abs(delta):.1f} pts" if delta else "flat"
    direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
    return f"{direction} {abs(delta):,.0f}{unit}" if delta else "flat"


def _health_label(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Stable"
    if score >= 40:
        return "Needs Attention"
    return "At Risk"


def _window_metrics(db: Client, org_id: str, start_day: date, end_day: date) -> dict[str, Any]:
    start_iso = start_day.isoformat()
    end_iso = end_day.isoformat()

    sales_resp = (
        db.table("sales")
        .select("amount, cost, profit, source, payment_status, sold_at")
        .eq("org_id", org_id)
        .gte("sold_at", start_iso)
        .lt("sold_at", end_iso)
        .execute()
    )
    sales = sales_resp.data or []
    paid_sales = [s for s in sales if s.get("payment_status") == "paid"]

    leads_resp = (
        db.table("leads")
        .select("status, source, created_at, follow_up_at, contacted_at")
        .eq("org_id", org_id)
        .gte("created_at", start_iso)
        .lt("created_at", end_iso)
        .execute()
    )
    leads = leads_resp.data or []

    expenses_resp = (
        db.table("expenses")
        .select("amount, category, expense_date")
        .eq("org_id", org_id)
        .gte("expense_date", start_iso)
        .lt("expense_date", end_iso)
        .execute()
    )
    expenses = expenses_resp.data or []

    customers_resp = (
        db.table("customers")
        .select("id, total_orders, created_at")
        .eq("org_id", org_id)
        .gte("created_at", start_iso)
        .lt("created_at", end_iso)
        .execute()
    )
    customers = customers_resp.data or []

    revenue_by_source: dict[str, float] = {}
    for sale in paid_sales:
        src = sale.get("source") or "unknown"
        revenue_by_source[src] = revenue_by_source.get(src, 0) + float(sale.get("amount") or 0)

    leads_by_source: dict[str, int] = {}
    for lead in leads:
        src = lead.get("source") or "unknown"
        leads_by_source[src] = leads_by_source.get(src, 0) + 1

    expenses_by_category: dict[str, float] = {}
    for expense in expenses:
        cat = expense.get("category") or "uncategorized"
        expenses_by_category[cat] = expenses_by_category.get(cat, 0) + float(expense.get("amount") or 0)

    won = [l for l in leads if l.get("status") == "won"]
    lost = [l for l in leads if l.get("status") == "lost"]
    missed_follow_ups = [
        l for l in leads
        if l.get("follow_up_at") and not l.get("contacted_at") and l.get("status") not in ("won", "lost")
    ]

    total_revenue = _sum(paid_sales, "amount")
    total_cost = _sum(paid_sales, "cost")
    total_profit = _sum(paid_sales, "profit")
    total_expenses = _sum(expenses, "amount")
    conversion_rate = (len(won) / len(leads) * 100) if leads else 0

    return {
        "revenue_total": total_revenue,
        "cost_total": total_cost,
        "profit_total": total_profit,
        "margin_pct": round((total_profit / total_revenue * 100), 1) if total_revenue else 0,
        "expense_total": total_expenses,
        "lead_total": len(leads),
        "won_total": len(won),
        "lost_total": len(lost),
        "conversion_rate_pct": round(conversion_rate, 1),
        "missed_follow_ups": len(missed_follow_ups),
        "new_customers": len(customers),
        "revenue_by_source": {k: round(v, 2) for k, v in revenue_by_source.items()},
        "leads_by_source": leads_by_source,
        "expenses_by_category": {k: round(v, 2) for k, v in expenses_by_category.items()},
    }


def get_dashboard_metrics(db: Client, org_id: str, days: int = 30) -> dict[str, Any]:
    """Return all dashboard metrics for an org over the last N days."""
    since = (date.today() - timedelta(days=days)).isoformat()

    sales_resp = (
        db.table("sales")
        .select("amount, cost, profit, source, payment_status, sold_at, customer_id")
        .eq("org_id", org_id)
        .gte("sold_at", since)
        .execute()
    )
    sales = sales_resp.data or []

    paid_sales = [s for s in sales if s["payment_status"] == "paid"]
    total_revenue = _sum(paid_sales, "amount")
    total_cost = _sum(paid_sales, "cost")
    total_profit = _sum(paid_sales, "profit")
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    revenue_by_source: dict[str, float] = {}
    for s in paid_sales:
        src = s.get("source") or "unknown"
        revenue_by_source[src] = revenue_by_source.get(src, 0) + float(s.get("amount") or 0)

    leads_resp = (
        db.table("leads")
        .select("status, source, created_at, follow_up_at, contacted_at")
        .eq("org_id", org_id)
        .gte("created_at", since)
        .execute()
    )
    leads = leads_resp.data or []

    total_leads = len(leads)
    won_leads = [l for l in leads if l["status"] == "won"]
    lost_leads = [l for l in leads if l["status"] == "lost"]
    conversion_rate = (len(won_leads) / total_leads * 100) if total_leads else 0
    missed_follow_ups = [
        l for l in leads
        if l.get("follow_up_at") and not l.get("contacted_at") and l["status"] not in ("won", "lost")
    ]

    leads_by_source: dict[str, int] = {}
    for l in leads:
        src = l.get("source") or "unknown"
        leads_by_source[src] = leads_by_source.get(src, 0) + 1

    customers_resp = (
        db.table("customers")
        .select("id, total_orders, last_purchase_at, created_at")
        .eq("org_id", org_id)
        .execute()
    )
    customers = customers_resp.data or []
    total_customers = len(customers)
    repeat_customers = [c for c in customers if c["total_orders"] > 1]
    repeat_pct = (len(repeat_customers) / total_customers * 100) if total_customers else 0

    expenses_resp = (
        db.table("expenses")
        .select("amount, category, expense_date")
        .eq("org_id", org_id)
        .gte("expense_date", since)
        .execute()
    )
    expenses = expenses_resp.data or []
    total_expenses = _sum(expenses, "amount")

    expenses_by_category: dict[str, float] = {}
    for e in expenses:
        cat = e["category"]
        expenses_by_category[cat] = expenses_by_category.get(cat, 0) + float(e.get("amount") or 0)

    metrics = {
        "period_days": days,
        "revenue": {
            "total": round(total_revenue, 2),
            "cost": round(total_cost, 2),
            "profit": round(total_profit, 2),
            "margin_pct": round(profit_margin, 1),
            "by_source": {k: round(v, 2) for k, v in revenue_by_source.items()},
        },
        "leads": {
            "total": total_leads,
            "won": len(won_leads),
            "lost": len(lost_leads),
            "conversion_rate_pct": round(conversion_rate, 1),
            "missed_follow_ups": len(missed_follow_ups),
            "by_source": leads_by_source,
        },
        "customers": {
            "total": total_customers,
            "repeat": len(repeat_customers),
            "repeat_pct": round(repeat_pct, 1),
        },
        "expenses": {
            "total": round(total_expenses, 2),
            "by_category": {k: round(v, 2) for k, v in expenses_by_category.items()},
        },
    }

    metrics["analyst_brief"] = get_analyst_brief(db, org_id, metrics=metrics, days=days)
    return metrics


def get_analyst_brief(
    db: Client,
    org_id: str,
    metrics: dict[str, Any] | None = None,
    days: int = 30,
) -> dict[str, Any]:
    metrics = metrics or get_dashboard_metrics(db, org_id, days=days)
    org = (
        db.table("organizations")
        .select("name, industry, plan")
        .eq("id", org_id)
        .single()
        .execute()
    )
    org_data = org.data or {}
    industry = org_data.get("industry") or "general"
    benchmark = INDUSTRY_BENCHMARKS.get(industry, {"conversion": 22.0, "margin": 24.0, "repeat": 18.0, "note": "Healthy local operators usually balance lead volume, margin discipline, and repeat business."})

    today = date.today()
    current_start = today - timedelta(days=days)
    previous_start = current_start - timedelta(days=days)

    current_window = _window_metrics(db, org_id, current_start, today + timedelta(days=1))
    previous_window = _window_metrics(db, org_id, previous_start, current_start)

    revenue_total = metrics["revenue"]["total"]
    profit_total = metrics["revenue"]["profit"]
    margin_pct = metrics["revenue"]["margin_pct"]
    lead_total = metrics["leads"]["total"]
    conversion_pct = metrics["leads"]["conversion_rate_pct"]
    missed_follow_ups = metrics["leads"]["missed_follow_ups"]
    repeat_pct = metrics["customers"]["repeat_pct"]
    expense_total = metrics["expenses"]["total"]

    score = 100
    if revenue_total == 0:
        score -= 18
    if lead_total == 0:
        score -= 18
    elif conversion_pct < float(benchmark["conversion"]) * 0.6:
        score -= 16
    elif conversion_pct < float(benchmark["conversion"]):
        score -= 8
    if margin_pct < float(benchmark["margin"]) * 0.6:
        score -= 16
    elif margin_pct < float(benchmark["margin"]):
        score -= 8
    if missed_follow_ups > 0:
        score -= min(18, missed_follow_ups * 3)
    if repeat_pct < float(benchmark["repeat"]) and metrics["customers"]["total"] >= 5:
        score -= 10
    if expense_total > revenue_total and revenue_total > 0:
        score -= 10
    score = max(18, min(98, score))

    top_risks: list[dict[str, Any]] = []
    if missed_follow_ups > 0:
        top_risks.append({
            "title": "Follow-up queue is leaking revenue",
            "detail": f"{missed_follow_ups} lead{'s' if missed_follow_ups != 1 else ''} already have follow-up dates but still have no contact logged. That usually means warm demand is stalling before a quote or close.",
            "severity": "high" if missed_follow_ups >= 4 else "medium",
        })
    if lead_total >= 5 and conversion_pct < float(benchmark["conversion"]):
        top_risks.append({
            "title": "Lead conversion is below a healthy operating range",
            "detail": f"Conversion is {conversion_pct:.1f}% against a working benchmark near {float(benchmark['conversion']):.0f}% for this business type. The pipeline is producing interest, but too little of it is becoming won work.",
            "severity": "high" if conversion_pct < float(benchmark["conversion"]) * 0.6 else "medium",
        })
    if revenue_total > 0 and margin_pct < float(benchmark["margin"]):
        top_risks.append({
            "title": "Margin is too thin for comfortable growth",
            "detail": f"Gross margin is {margin_pct:.1f}% while the business should be defending something closer to {float(benchmark['margin']):.0f}%. Revenue is coming in, but too much of it is being eaten by cost or pricing leakage.",
            "severity": "high" if margin_pct < float(benchmark["margin"]) * 0.6 else "medium",
        })
    if metrics["customers"]["total"] >= 5 and repeat_pct < float(benchmark["repeat"]):
        top_risks.append({
            "title": "Retention is not compounding yet",
            "detail": f"Repeat customer rate is {repeat_pct:.1f}%, below the working benchmark near {float(benchmark['repeat']):.0f}%. The business is not capturing enough follow-on value from customers it already paid to acquire.",
            "severity": "medium",
        })
    if revenue_total == 0 and lead_total == 0:
        top_risks.append({
            "title": "The pipeline is too quiet to audit deeply",
            "detail": "There is not enough lead or revenue activity in the current window to spot true operating patterns. Right now the business needs motion more than optimization.",
            "severity": "medium",
        })

    best_revenue_source = None
    if metrics["revenue"]["by_source"]:
        best_revenue_source = max(metrics["revenue"]["by_source"].items(), key=lambda item: item[1])

    top_expense_category = None
    if metrics["expenses"]["by_category"]:
        top_expense_category = max(metrics["expenses"]["by_category"].items(), key=lambda item: item[1])

    top_opportunities: list[dict[str, Any]] = []
    if best_revenue_source and best_revenue_source[0] != "unknown":
        top_opportunities.append({
            "title": f"{best_revenue_source[0].replace('_', ' ').title()} is already your strongest source",
            "detail": f"It generated {best_revenue_source[1]:,.0f} in tracked revenue this period. Doubling down on a channel that is already converting into cash is usually safer than experimenting with cold channels.",
            "impact_hint": "High-leverage",
        })
    if missed_follow_ups > 0:
        top_opportunities.append({
            "title": "Overdue follow-ups are the fastest recoverable win",
            "detail": "These leads already raised their hands. Cleaning up that queue is usually the quickest path to more quotes, more closed work, and better conversion.",
            "impact_hint": "This week",
        })
    if metrics["customers"]["total"] >= 3 and repeat_pct < 35:
        top_opportunities.append({
            "title": "Existing customers are the cheapest growth channel",
            "detail": "A simple reactivation or maintenance offer can often lift repeat revenue faster than acquiring brand-new leads from scratch.",
            "impact_hint": "Retention",
        })
    if top_expense_category:
        top_opportunities.append({
            "title": f"{top_expense_category[0].replace('_', ' ').title()} is the first cost bucket to inspect",
            "detail": f"It represents {top_expense_category[1]:,.0f} in spend this period. Tightening the largest cost center tends to improve margin faster than broad cost-cutting.",
            "impact_hint": "Margin",
        })
    if margin_pct >= float(benchmark["margin"]):
        top_opportunities.append({
            "title": "Unit economics are strong enough to press growth",
            "detail": "Margin is already holding at a healthy level, which means new demand should add profit rather than just workload.",
            "impact_hint": "Scale",
        })

    what_changed = [
        {
            "label": "Revenue",
            "value": _pct_change(current_window["revenue_total"], previous_window["revenue_total"]),
            "direction": "up" if current_window["revenue_total"] > previous_window["revenue_total"] else "down" if current_window["revenue_total"] < previous_window["revenue_total"] else "flat",
            "detail": f"{current_window['revenue_total']:,.0f} this period vs {previous_window['revenue_total']:,.0f} previously",
        },
        {
            "label": "Lead volume",
            "value": _pct_change(current_window["lead_total"], previous_window["lead_total"]),
            "direction": "up" if current_window["lead_total"] > previous_window["lead_total"] else "down" if current_window["lead_total"] < previous_window["lead_total"] else "flat",
            "detail": f"{current_window['lead_total']} leads this period vs {previous_window['lead_total']} previously",
        },
        {
            "label": "Profit margin",
            "value": round(current_window["margin_pct"] - previous_window["margin_pct"], 1),
            "direction": "up" if current_window["margin_pct"] > previous_window["margin_pct"] else "down" if current_window["margin_pct"] < previous_window["margin_pct"] else "flat",
            "detail": f"{_label_change(current_window['margin_pct'], previous_window['margin_pct'])} from the prior period",
        },
    ]

    focus_this_week: list[dict[str, Any]] = []
    if missed_follow_ups > 0:
        focus_this_week.append({
            "priority": 1,
            "title": f"Clear the {missed_follow_ups}-lead follow-up queue",
            "detail": "Start with the oldest overdue leads and push each one to contacted, won, or lost so the pipeline becomes truthful again.",
        })
    if top_expense_category:
        focus_this_week.append({
            "priority": len(focus_this_week) + 1,
            "title": f"Review {top_expense_category[0].replace('_', ' ')} spend",
            "detail": "Check whether this cost bucket is supporting closed revenue or simply dragging margin down.",
        })
    if best_revenue_source and best_revenue_source[0] != "unknown":
        focus_this_week.append({
            "priority": len(focus_this_week) + 1,
            "title": f"Feed more demand into {best_revenue_source[0].replace('_', ' ')}",
            "detail": "The best current source has already shown it can turn into paid work. Put this week’s effort where the business is already seeing traction.",
        })
    if not focus_this_week:
        focus_this_week.append({
            "priority": 1,
            "title": "Start logging leads, sales, and expenses consistently",
            "detail": "Once the operating data is flowing, the dashboard can identify where growth is real and where margin is leaking.",
        })

    revenue_change = _pct_change(current_window["revenue_total"], previous_window["revenue_total"])
    revenue_change_text = "holding flat"
    if revenue_change is not None:
        revenue_change_text = "up sharply" if revenue_change >= 15 else "up modestly" if revenue_change > 0 else "down" if revenue_change < 0 else "holding flat"

    if revenue_total == 0 and lead_total == 0:
        executive_summary = "The business does not have enough current activity for a deep operating read yet. The immediate priority is creating consistent pipeline and transaction visibility so the dashboard can separate demand problems from execution problems."
    else:
        executive_summary = (
            f"Revenue is {revenue_change_text}, with gross margin at {margin_pct:.1f}% and lead conversion at {conversion_pct:.1f}%. "
            f"The biggest operating pressure right now is {'follow-up discipline' if missed_follow_ups > 0 else 'turning activity into cleaner profit'}, "
            f"while the clearest upside is {'capturing overdue demand and doubling down on the best current source' if best_revenue_source else 'tightening execution around the existing pipeline'}."
        )

    return {
        "health_score": score,
        "health_label": _health_label(score),
        "executive_summary": executive_summary,
        "top_risks": top_risks[:3],
        "top_opportunities": top_opportunities[:3],
        "what_changed": what_changed,
        "focus_this_week": focus_this_week[:3],
        "benchmark_note": str(benchmark["note"]),
        "pro_positioning": {
            "headline": "Pro gives you an analyst team on demand",
            "detail": "Free gives you the operating brief. Pro adds deeper AI drill-down, forecasting, recurring board reports, and continuous monitoring.",
            "features": [
                "Root-cause analysis across revenue, margin, and retention",
                "30/60/90 day forecasting and scenario modeling",
                "Deeper segmentation by source, service, and customer behavior",
            ],
        },
    }


def get_revenue_trend(db: Client, org_id: str, weeks: int = 12) -> list[dict]:
    """Weekly revenue trend for the last N weeks (for chart)."""
    since = (date.today() - timedelta(weeks=weeks)).isoformat()
    sales_resp = (
        db.table("sales")
        .select("amount, sold_at")
        .eq("org_id", org_id)
        .eq("payment_status", "paid")
        .gte("sold_at", since)
        .order("sold_at")
        .execute()
    )
    sales = sales_resp.data or []

    weekly: dict[str, float] = {}
    for s in sales:
        week_label = s["sold_at"][:10]
        weekly[week_label] = weekly.get(week_label, 0) + float(s.get("amount") or 0)

    return [{"date": k, "revenue": round(v, 2)} for k, v in sorted(weekly.items())]
