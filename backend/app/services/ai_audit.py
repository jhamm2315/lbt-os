"""
AI Audit Engine — core intelligence layer of LBT OS.

Design:
  1. Pull raw metrics via the metrics service (structured, not raw SQL).
  2. Build a rich prompt with business context.
  3. Call OpenAI and request a structured JSON response.
  4. Persist the audit report to Supabase.
  5. Return the report.

The engine is stateless — every run is independent and idempotent.
Results are cached in the audit_reports table.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

from openai import OpenAI
from supabase import Client
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings
from .metrics import get_dashboard_metrics

_llm_client: OpenAI | None = None


def _get_llm_client() -> OpenAI:
    """
    Returns an OpenAI-compatible client pointed at either:
      - OpenAI's API  (llm_provider=openai)
      - Ollama local  (llm_provider=ollama)

    Ollama exposes an OpenAI-compatible endpoint at /v1,
    so the same SDK works for both — just different base_url + api_key.
    """
    global _llm_client
    if _llm_client is None:
        if settings.llm_provider == "ollama":
            _llm_client = OpenAI(
                base_url=f"{settings.ollama_base_url}/v1",
                api_key="ollama",   # Ollama ignores the key but the SDK requires one
            )
        else:
            _llm_client = OpenAI(api_key=settings.openai_api_key)
    return _llm_client


def _active_model() -> str:
    return settings.ollama_model if settings.llm_provider == "ollama" else settings.openai_model


AUDIT_SYSTEM_PROMPT = """
You are a sharp business analyst specializing in small and medium local businesses.
You are given 30-day operational metrics for a business and must:

1. Identify the top 3-5 specific problems hurting revenue, growth, or efficiency.
2. Give concrete, actionable recommendations — not generic advice.
3. Calculate or estimate the dollar impact where possible.
4. Output a health score from 0 (critical) to 100 (excellent).

Respond ONLY with valid JSON in this exact structure:
{
  "health_score": <0-100>,
  "insights": [
    {
      "type": "revenue_leak" | "missed_opportunity" | "inefficiency" | "strength",
      "title": "<short title>",
      "detail": "<plain English explanation, 1-2 sentences>",
      "estimated_impact": "<dollar amount or % if calculable, else null>",
      "severity": "high" | "medium" | "low"
    }
  ],
  "recommendations": [
    {
      "priority": 1,
      "action": "<specific action to take>",
      "why": "<why this will move the needle>",
      "timeframe": "<this week | this month | next quarter>"
    }
  ]
}
""".strip()


def _build_metrics_prompt(metrics: dict, org_name: str, industry: str | None) -> str:
    industry_label = industry or "general service business"
    m = metrics

    return f"""
Business: {org_name}
Industry: {industry_label}
Analysis period: last {m['period_days']} days

=== REVENUE ===
Total Revenue:  ${m['revenue']['total']:,.2f}
Total Cost:     ${m['revenue']['cost']:,.2f}
Gross Profit:   ${m['revenue']['profit']:,.2f}
Profit Margin:  {m['revenue']['margin_pct']}%
Revenue by source: {json.dumps(m['revenue']['by_source'])}

=== LEADS ===
Total Leads:        {m['leads']['total']}
Won (converted):    {m['leads']['won']}
Lost:               {m['leads']['lost']}
Conversion Rate:    {m['leads']['conversion_rate_pct']}%
Missed Follow-Ups:  {m['leads']['missed_follow_ups']} leads have a follow-up scheduled but were never contacted
Leads by source:    {json.dumps(m['leads']['by_source'])}

=== CUSTOMERS ===
Total Customers:    {m['customers']['total']}
Repeat Customers:   {m['customers']['repeat']} ({m['customers']['repeat_pct']}%)

=== EXPENSES ===
Total Expenses:     ${m['expenses']['total']:,.2f}
By category:        {json.dumps(m['expenses']['by_category'])}

=== CONTEXT ===
Net Operating Income (estimated): ${m['revenue']['profit'] - m['expenses']['total']:,.2f}
""".strip()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def _call_llm(prompt: str) -> dict:
    client = _get_llm_client()
    model  = _active_model()

    kwargs: dict = dict(
        model=model,
        messages=[
            {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    # json_object response format is supported by OpenAI and most Ollama models.
    # Ollama models that don't support it will still return JSON because the
    # system prompt explicitly instructs it — so this is safe either way.
    if settings.llm_provider == "openai":
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    content  = response.choices[0].message.content

    # Ollama sometimes wraps JSON in a markdown code block — strip it
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    return json.loads(content)


def run_audit(db: Client, org_id: str, org_name: str, industry: str | None) -> dict:
    """
    Run a full AI audit for an organization.

    Returns the saved audit_report record.
    """
    period_end   = date.today()
    period_start = period_end - timedelta(days=30)

    metrics = get_dashboard_metrics(db, org_id, days=30)
    prompt  = _build_metrics_prompt(metrics, org_name, industry)

    ai_result = _call_llm(prompt)

    insights        = ai_result.get("insights", [])
    recommendations = ai_result.get("recommendations", [])
    health_score    = ai_result.get("health_score", 50)

    report = {
        "org_id":          org_id,
        "period_start":    period_start.isoformat(),
        "period_end":      period_end.isoformat(),
        "insights":        insights,
        "recommendations": recommendations,
        "raw_metrics":     metrics,
        "health_score":    health_score,
        "model_used":      _active_model(),
    }

    result = db.table("audit_reports").insert(report).execute()
    return result.data[0]


def get_latest_audit(db: Client, org_id: str) -> dict | None:
    """Return the most recent audit report for an org."""
    result = (
        db.table("audit_reports")
        .select("*")
        .eq("org_id", org_id)
        .order("generated_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None
