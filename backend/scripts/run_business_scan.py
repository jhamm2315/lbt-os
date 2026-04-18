#!/usr/bin/env python
"""
Run a sync + audit scan for one org or every org.

Examples:
  source .venv/bin/activate
  python scripts/run_business_scan.py --org-id <uuid> --sync --ai --json
  python scripts/run_business_scan.py --sync
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import get_db  # noqa: E402
from app.services.ai_audit import run_audit  # noqa: E402
from app.services.integrations import sync_all_connections_for_org  # noqa: E402
from app.services.metrics import get_dashboard_metrics  # noqa: E402


def scan_org(org: dict, *, sync: bool, ai: bool) -> dict:
    db = get_db()
    sync_runs = sync_all_connections_for_org(db, org["id"], trigger_source="script") if sync else []
    metrics = get_dashboard_metrics(db, org["id"], days=30)
    result = {
        "org_id": org["id"],
        "org_name": org["name"],
        "plan": org.get("plan"),
        "sync_runs": sync_runs,
        "health_score": metrics["analyst_brief"]["health_score"],
        "health_label": metrics["analyst_brief"]["health_label"],
        "executive_summary": metrics["analyst_brief"]["executive_summary"],
        "top_risks": metrics["analyst_brief"]["top_risks"],
        "top_opportunities": metrics["analyst_brief"]["top_opportunities"],
    }

    if ai and org.get("plan") in {"pro", "premium"}:
        result["ai_audit"] = run_audit(
            db=db,
            org_id=org["id"],
            org_name=org["name"],
            industry=org.get("industry"),
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync integrations and run business scans.")
    parser.add_argument("--org-id", help="Only scan a single organization UUID.")
    parser.add_argument("--sync", action="store_true", help="Run integration syncs before scanning.")
    parser.add_argument("--ai", action="store_true", help="Run the paid AI audit for pro/premium orgs.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a readable summary.")
    args = parser.parse_args()

    db = get_db()
    query = db.table("organizations").select("id, name, industry, plan")
    if args.org_id:
        query = query.eq("id", args.org_id)
    orgs = query.execute().data or []

    reports = [scan_org(org, sync=args.sync, ai=args.ai) for org in orgs]

    if args.json:
        print(json.dumps(reports, indent=2, default=str))
        return 0

    for report in reports:
        print(f"\n{report['org_name']} ({report['org_id']})")
        print(f"Plan: {report['plan']}")
        print(f"Health: {report['health_score']} - {report['health_label']}")
        print(report["executive_summary"])
        if report["top_risks"]:
            print("Top risk:")
            print(f"  - {report['top_risks'][0]['title']}")
        if report["top_opportunities"]:
            print("Top opportunity:")
            print(f"  - {report['top_opportunities'][0]['title']}")
        if args.sync:
            print(f"Sync runs: {len(report['sync_runs'])}")
        if args.ai and report.get("ai_audit"):
            print(f"AI audit stored: {report['ai_audit']['id']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
