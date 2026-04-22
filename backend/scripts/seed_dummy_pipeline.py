#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import get_db  # noqa: E402
from app.services.demo_data import seed_org_data  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed dummy pipeline data into an existing org.")
    parser.add_argument("--org-id", required=True, help="Organization UUID to seed.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatable data.")
    parser.add_argument("--industry", help="Override org industry for template-driven test data.")
    args = parser.parse_args()

    db = get_db()
    org = db.table("organizations").select("id,name,industry").eq("id", args.org_id).maybe_single().execute()
    if org is None or not org.data:
        raise SystemExit(f"Organization not found: {args.org_id}")

    industry = args.industry or org.data.get("industry")
    summary = seed_org_data(db, args.org_id, industry, seed=args.seed)

    print(f"Seeded org: {org.data['name']} ({args.org_id})")
    print(f"Industry template: {summary['industry']}")
    for key, value in summary["counts"].items():
        print(f"{key.title()}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
