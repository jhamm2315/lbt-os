#!/usr/bin/env python
from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import get_db  # noqa: E402
from app.services.templates import get_template  # noqa: E402


DEFAULT_LEAD_SOURCES = ["referral", "website", "google", "social", "yelp", "other"]
LEAD_STATUSES = ["new", "contacted", "qualified", "proposal", "won", "lost"]
DEFAULT_SERVICES = [
    "Custom molded bio-composite parts",
    "Prototype material run",
    "Sustainable packaging consultation",
    "Small-batch composite fabrication",
    "Manufacturing feasibility review",
    "Industrial material sourcing",
]
DEFAULT_EXPENSE_CATEGORIES = ["materials", "marketing", "equipment", "software", "insurance", "utilities", "misc", "payroll"]
DEFAULT_CUSTOMER_NAMES = [
    "Frontier Outdoor Goods",
    "Mesa Labs",
    "Alpine Industrial",
    "Peak Packaging Co",
    "Terra Build Systems",
    "Blue Pine Manufacturing",
    "Range Supply Group",
    "Summit AgTech",
    "Evergreen Fabrication",
    "Canyon Process Works",
]
DEFAULT_VENDOR_NAMES = ["Acme Supply", "Denver Utilities", "Material Depot", "BrandForge", "CloudOps"]
LEAD_NAMES = [
    "Jordan Lee",
    "Taylor Morgan",
    "Chris Patel",
    "Morgan Rivera",
    "Jamie Brooks",
    "Skyler Evans",
    "Avery Kim",
    "Cameron Diaz",
    "Riley Parker",
    "Alex Chen",
    "Dakota Young",
    "Parker Scott",
    "Reese Bennett",
    "Hayden Foster",
    "Quinn Adams",
    "Emerson Ward",
    "Finley Cooper",
    "Harper Reed",
    "Rowan Ellis",
    "Blake Turner",
]


def build_seed_profile(industry: str | None) -> dict[str, list[str]]:
    template = get_template(industry)
    if not template:
        return {
            "services": DEFAULT_SERVICES,
            "lead_sources": DEFAULT_LEAD_SOURCES,
            "expense_categories": DEFAULT_EXPENSE_CATEGORIES,
            "customer_names": DEFAULT_CUSTOMER_NAMES,
            "vendor_names": DEFAULT_VENDOR_NAMES,
        }

    return {
        "services": template.get("services") or DEFAULT_SERVICES,
        "lead_sources": template.get("lead_sources") or DEFAULT_LEAD_SOURCES,
        "expense_categories": template.get("expense_categories") or DEFAULT_EXPENSE_CATEGORIES,
        "customer_names": template.get("sample_customers") or DEFAULT_CUSTOMER_NAMES,
        "vendor_names": template.get("sample_vendors") or DEFAULT_VENDOR_NAMES,
    }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def recent_datetime(days_back: int) -> datetime:
    base = utc_now() - timedelta(days=random.randint(1, days_back))
    return base.replace(hour=random.randint(8, 17), minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)


def recent_date(days_back: int) -> date:
    return (date.today() - timedelta(days=random.randint(1, days_back)))


def create_leads(db, org_id: str, count: int, profile: dict[str, list[str]]) -> list[dict]:
    leads = []
    lead_sources = profile["lead_sources"]
    services = profile["services"]
    for idx in range(count):
        status = random.choices(
            LEAD_STATUSES,
            weights=[4, 4, 4, 3, 3, 2],
            k=1,
        )[0]
        created_at = recent_datetime(90)
        follow_up_at = None
        contacted_at = None
        converted_at = None
        lost_reason = None
        if status in {"contacted", "qualified", "proposal", "won", "lost"}:
            contacted_at = created_at + timedelta(days=random.randint(1, 6))
        if status in {"qualified", "proposal"}:
            follow_up_at = created_at + timedelta(days=random.randint(3, 10))
        if status == "won":
            converted_at = created_at + timedelta(days=random.randint(7, 18))
        if status == "lost":
            lost_reason = random.choice(["Budget", "Went with competitor", "Timing", "Project paused"])
        if idx % 6 == 0:
            follow_up_at = created_at + timedelta(days=random.randint(2, 8))
            contacted_at = None
            if status not in {"won", "lost"}:
                status = random.choice(["new", "contacted", "qualified"])

        lead = {
            "org_id": org_id,
            "name": LEAD_NAMES[idx % len(LEAD_NAMES)],
            "email": f"lead{idx+1}@example.com",
            "phone": f"303-555-{1000 + idx}",
            "source": random.choice(lead_sources),
            "status": status,
            "service_interest": random.choice(services),
            "estimated_value": round(random.uniform(2500, 18000), 2),
            "notes": "Seeded pipeline record for dashboard testing.",
            "assigned_to": "seed-user",
            "follow_up_at": follow_up_at.isoformat() if follow_up_at else None,
            "contacted_at": contacted_at.isoformat() if contacted_at else None,
            "converted_at": converted_at.isoformat() if converted_at else None,
            "lost_reason": lost_reason,
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
        }
        result = db.table("leads").insert(lead).execute()
        leads.append(result.data[0])
    return leads


def create_customers(db, org_id: str, leads: list[dict], count: int, profile: dict[str, list[str]]) -> list[dict]:
    customers = []
    won_leads = [lead for lead in leads if lead["status"] == "won"]
    customer_names = profile["customer_names"]
    for idx in range(count):
        linked_lead = won_leads[idx] if idx < len(won_leads) else None
        created_at = recent_datetime(120)
        customer = {
            "org_id": org_id,
            "lead_id": linked_lead["id"] if linked_lead else None,
            "name": customer_names[idx % len(customer_names)],
            "email": f"customer{idx+1}@example.com",
            "phone": f"720-555-{2000 + idx}",
            "address": f"{100 + idx} Market St, Denver, CO",
            "tags": random.sample(["vip", "loyal", "at_risk", "inactive"], k=random.randint(0, 2)),
            "notes": "Seeded customer for pipeline testing.",
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
        }
        result = db.table("customers").insert(customer).execute()
        customers.append(result.data[0])
    return customers


def create_sales(db, org_id: str, leads: list[dict], customers: list[dict], count: int, profile: dict[str, list[str]]) -> list[dict]:
    sales = []
    won_leads = [lead for lead in leads if lead["status"] == "won"]
    services = profile["services"]
    lead_sources = profile["lead_sources"]
    for idx in range(count):
        customer = random.choice(customers)
        linked_lead = random.choice(won_leads) if won_leads and idx < len(won_leads) else None
        sold_at = recent_datetime(90)
        amount = round(random.uniform(4800, 28000), 2)
        cost = round(amount * random.uniform(0.38, 0.72), 2)
        sale = {
            "org_id": org_id,
            "customer_id": customer["id"],
            "lead_id": linked_lead["id"] if linked_lead else None,
            "service": random.choice(services),
            "amount": amount,
            "cost": cost,
            "payment_method": random.choice(["card", "bank_transfer", "check"]),
            "payment_status": random.choices(["paid", "pending"], weights=[5, 1], k=1)[0],
            "source": linked_lead["source"] if linked_lead else random.choice(lead_sources),
            "invoice_number": f"INV-SEED-{1000 + idx}",
            "notes": "Seeded revenue record for analytics testing.",
            "sold_at": sold_at.isoformat(),
            "created_at": sold_at.isoformat(),
            "updated_at": sold_at.isoformat(),
        }
        result = db.table("sales").insert(sale).execute()
        sales.append(result.data[0])
    return sales


def create_expenses(db, org_id: str, count: int, profile: dict[str, list[str]]) -> list[dict]:
    expenses = []
    expense_categories = profile["expense_categories"]
    vendor_names = profile["vendor_names"]
    for idx in range(count):
        expense_date = recent_date(90)
        category = random.choice(expense_categories)
        amount = round(random.uniform(120, 6400), 2)
        expense = {
            "org_id": org_id,
            "category": category,
            "description": f"Seeded {category} expense #{idx+1}",
            "amount": amount,
            "vendor": random.choice(vendor_names),
            "is_recurring": category in {"software", "insurance", "utilities", "rent", "phone"},
            "recurrence_period": "monthly" if category in {"software", "insurance", "utilities", "rent", "phone"} else None,
            "expense_date": expense_date.isoformat(),
            "created_at": datetime.combine(expense_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
            "updated_at": datetime.combine(expense_date, datetime.min.time(), tzinfo=timezone.utc).isoformat(),
        }
        result = db.table("expenses").insert(expense).execute()
        expenses.append(result.data[0])
    return expenses


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed dummy pipeline data into an existing org.")
    parser.add_argument("--org-id", required=True, help="Organization UUID to seed.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatable data.")
    parser.add_argument("--industry", help="Override org industry for template-driven test data.")
    args = parser.parse_args()

    random.seed(args.seed)
    db = get_db()

    org = db.table("organizations").select("id,name,industry").eq("id", args.org_id).maybe_single().execute()
    if org is None or not org.data:
        raise SystemExit(f"Organization not found: {args.org_id}")

    industry = args.industry or org.data.get("industry")
    profile = build_seed_profile(industry)

    lead_count = 20
    customer_count = 10
    sale_count = 12
    expense_count = 8

    leads = create_leads(db, args.org_id, lead_count, profile)
    customers = create_customers(db, args.org_id, leads, customer_count, profile)
    sales = create_sales(db, args.org_id, leads, customers, sale_count, profile)
    expenses = create_expenses(db, args.org_id, expense_count, profile)

    print(f"Seeded org: {org.data['name']} ({args.org_id})")
    print(f"Industry template: {industry or 'general'}")
    print(f"Leads: {len(leads)}")
    print(f"Customers: {len(customers)}")
    print(f"Sales: {len(sales)}")
    print(f"Expenses: {len(expenses)}")
    print(f"Total records: {len(leads) + len(customers) + len(sales) + len(expenses)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
