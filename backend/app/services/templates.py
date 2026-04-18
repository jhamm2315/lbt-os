"""
LBT Template Engine

Industry-specific presets for:
  - Services offered (populates service_interest dropdown for leads)
  - Lead sources (most relevant per industry)
  - Expense categories (most common per industry)
  - Default dashboard KPI focus
  - Seed data profiles for realistic pipeline testing

Templates are data-driven — no separate code paths per industry.
"""
from typing import NotRequired, TypedDict


class IndustryTemplate(TypedDict):
    label: str
    services: list[str]
    lead_sources: list[str]
    expense_categories: list[str]
    key_metrics: list[str]   # which dashboard metrics matter most
    quick_wins: list[str]    # pre-seeded AI tip hints
    sample_customers: NotRequired[list[str]]
    sample_vendors: NotRequired[list[str]]
    sample_org_names: NotRequired[list[str]]


TEMPLATES: dict[str, IndustryTemplate] = {
    "hvac": {
        "label": "HVAC",
        "services": [
            "AC Installation",
            "Furnace Installation",
            "AC Repair",
            "Furnace Repair",
            "Duct Cleaning",
            "Tune-Up / Maintenance",
            "Emergency Service",
            "Smart Thermostat Install",
        ],
        "lead_sources": ["google", "referral", "yelp", "social", "home_advisor", "nextdoor"],
        "expense_categories": ["payroll", "materials", "equipment", "marketing", "vehicle", "insurance", "misc"],
        "key_metrics": ["conversion_rate", "revenue_by_service", "repeat_customer_pct", "avg_job_value"],
        "quick_wins": [
            "Follow up within 24 hours — HVAC customers compare 3+ quotes",
            "Offer maintenance plans to convert one-time customers to recurring revenue",
            "Track cost-per-lead by source to cut low-ROI ad spend",
        ],
        "sample_customers": [
            "Front Range Property Group",
            "Mesa Family Dental",
            "Cherry Creek Retail Center",
            "High Plains Logistics",
            "Boulder Office Suites",
        ],
        "sample_vendors": ["Carrier Supply", "Trane Parts Depot", "Rocky Mountain Fleet", "ServiceTitan", "Xcel Energy"],
        "sample_org_names": ["Mile High HVAC", "Blue Peak Heating & Air", "Summit Comfort Systems"],
    },
    "plumbing": {
        "label": "Plumbing",
        "services": [
            "Emergency Repair",
            "Drain Cleaning",
            "Water Heater Install",
            "Pipe Repair / Replace",
            "Sewer Line",
            "Fixture Install",
            "Leak Detection",
            "Remodel Plumbing",
        ],
        "lead_sources": ["google", "referral", "yelp", "social", "nextdoor", "walk_in"],
        "expense_categories": ["payroll", "materials", "equipment", "marketing", "vehicle", "insurance", "misc"],
        "key_metrics": ["emergency_vs_scheduled", "conversion_rate", "avg_job_value", "repeat_pct"],
        "quick_wins": [
            "Emergency jobs have 3x higher close rates — make sure your after-hours line is live",
            "Upsell water heater flush / inspection on every job",
        ],
        "sample_customers": [
            "Riverstone Apartments",
            "Aurora Family Clinic",
            "Downtown Lofts HOA",
            "Copper State Warehouse",
            "Parkside Childcare",
        ],
        "sample_vendors": ["Ferguson", "Reece Supply", "Drain Pros Wholesale", "Ford Fleet", "Colorado Water"],
        "sample_org_names": ["Rapid Rooter Co.", "Metro Plumbing Pros", "Frontier Pipe & Drain"],
    },
    "restaurant": {
        "label": "Restaurant",
        "services": [
            "Dine-In",
            "Takeout",
            "Delivery",
            "Catering",
            "Private Events",
            "Happy Hour",
        ],
        "lead_sources": ["google", "yelp", "social", "walk_in", "referral", "door_dash", "uber_eats"],
        "expense_categories": ["payroll", "food_cost", "rent", "utilities", "marketing", "equipment", "misc"],
        "key_metrics": ["revenue_per_cover", "food_cost_pct", "repeat_customer_pct", "avg_ticket"],
        "quick_wins": [
            "Track food cost % weekly — should stay under 30% of revenue",
            "Loyalty programs increase repeat visits by 20-30% on average",
        ],
        "sample_customers": [
            "Downtown Lunch Crowd",
            "Local Families",
            "Office Catering Accounts",
            "Weekend Brunch Guests",
            "Event Bookers",
        ],
        "sample_vendors": ["Sysco", "US Foods", "Square", "Linen Hero", "Mile High Produce"],
        "sample_org_names": ["Copper Fork Kitchen", "Juniper Social House", "Highline Eatery"],
    },
    "gym": {
        "label": "Gym / Fitness",
        "services": [
            "Monthly Membership",
            "Annual Membership",
            "Day Pass",
            "Personal Training",
            "Group Classes",
            "Nutrition Coaching",
            "Corporate Wellness",
        ],
        "lead_sources": ["google", "referral", "social", "walk_in", "instagram", "facebook"],
        "expense_categories": ["payroll", "rent", "equipment", "marketing", "utilities", "insurance", "misc"],
        "key_metrics": ["churn_rate", "ltv", "conversion_rate", "monthly_recurring_revenue"],
        "quick_wins": [
            "Members who attend 3+ times/week churn 4x less — track attendance",
            "Follow up with members who haven't visited in 2 weeks before they cancel",
        ],
        "sample_customers": [
            "Young Professionals",
            "Strength Training Members",
            "Corporate Wellness Groups",
            "Weekend Class Pass Users",
            "Personal Training Clients",
        ],
        "sample_vendors": ["Mindbody", "Rogue Fitness", "ABC Fitness", "Core Hydration", "Local Utility Co"],
        "sample_org_names": ["Pulse Lab Fitness", "Altitude Strength Club", "Peak Motion Studio"],
    },
    "real_estate": {
        "label": "Real Estate",
        "services": [
            "Buyer Representation",
            "Seller Representation",
            "Property Management",
            "Investment Consulting",
            "Leasing",
            "Commercial",
        ],
        "lead_sources": ["referral", "google", "zillow", "realtor_com", "social", "cold_call", "open_house"],
        "expense_categories": ["marketing", "mls_fees", "payroll", "software", "vehicle", "insurance", "misc"],
        "key_metrics": ["pipeline_value", "conversion_rate", "avg_commission", "days_to_close"],
        "quick_wins": [
            "Leads contacted within 5 minutes are 100x more likely to convert",
            "Past clients are your cheapest leads — referral programs have 3-5x ROI vs. ads",
        ],
        "sample_customers": [
            "First-Time Homebuyers",
            "Move-Up Sellers",
            "Investor Buyers",
            "Rental Owners",
            "Relocation Families",
        ],
        "sample_vendors": ["Zillow Premier Agent", "Open House Media", "MLS Board", "Dotloop", "Denver Sign Pros"],
        "sample_org_names": ["Aspen Key Realty", "Crestline Property Group", "Front Range Home Advisors"],
    },
    "electrician": {
        "label": "Electrician",
        "services": [
            "Panel Upgrade",
            "Wiring Repair",
            "Lighting Install",
            "EV Charger Install",
            "Generator Install",
            "Emergency Electrical",
            "Commercial Troubleshooting",
        ],
        "lead_sources": ["google", "referral", "nextdoor", "yelp", "social", "home_advisor"],
        "expense_categories": ["payroll", "materials", "vehicle", "equipment", "insurance", "marketing", "misc"],
        "key_metrics": ["conversion_rate", "avg_job_value", "repeat_customer_pct", "revenue_by_service"],
        "quick_wins": [
            "EV charger installs can raise average ticket value quickly when quoted proactively",
            "Track emergency jobs separately so you can protect margin on rush work",
        ],
        "sample_customers": [
            "Park Hill Homes",
            "South Metro Offices",
            "Red Rocks Storage",
            "Foothills Retail Plaza",
            "Lakewood Family Homes",
        ],
        "sample_vendors": ["Graybar", "Platt Electric", "Milwaukee Tool", "Ford Fleet", "Colorado Utility"],
        "sample_org_names": ["BrightLine Electric", "Peak Power Solutions", "Mile High Electrical Co."],
    },
    "landscaping": {
        "label": "Landscaping",
        "services": [
            "Lawn Maintenance",
            "Spring Cleanup",
            "Irrigation Repair",
            "Hardscape Install",
            "Snow Removal",
            "Tree Trimming",
            "Commercial Grounds Care",
        ],
        "lead_sources": ["referral", "google", "nextdoor", "facebook", "yard_sign", "walk_in"],
        "expense_categories": ["payroll", "materials", "vehicle", "equipment", "fuel", "insurance", "marketing"],
        "key_metrics": ["recurring_revenue", "route_density", "avg_job_value", "repeat_customer_pct"],
        "quick_wins": [
            "Recurring maintenance contracts usually stabilize cash flow better than one-off installs",
            "Group jobs by route density to cut fuel and labor waste",
        ],
        "sample_customers": [
            "Maple Grove HOA",
            "Suburban Homeowners",
            "Office Park Management",
            "Church Property Teams",
            "Local Retail Centers",
        ],
        "sample_vendors": ["SiteOne", "John Deere Dealer", "Home Depot Pro", "Chevron Fleet", "Irrigation World"],
        "sample_org_names": ["GreenGrid Outdoor", "Summit Lawn & Snow", "Rangeview Landscape Co."],
    },
    "cleaning_service": {
        "label": "Cleaning Service",
        "services": [
            "Residential Cleaning",
            "Deep Cleaning",
            "Move-Out Cleaning",
            "Commercial Janitorial",
            "Airbnb Turnover",
            "Post-Construction Cleaning",
        ],
        "lead_sources": ["google", "referral", "thumbtack", "facebook", "nextdoor", "yelp"],
        "expense_categories": ["payroll", "supplies", "vehicle", "software", "insurance", "marketing", "misc"],
        "key_metrics": ["repeat_customer_pct", "recurring_revenue", "close_rate", "crew_utilization"],
        "quick_wins": [
            "Recurring clients are the fastest path to stable profit in cleaning businesses",
            "Move-out and Airbnb turnovers should be tracked separately because they price differently",
        ],
        "sample_customers": [
            "Airbnb Hosts",
            "Busy Families",
            "Dental Offices",
            "Property Managers",
            "Move-Out Clients",
        ],
        "sample_vendors": ["Costco Business", "Janitorial Depot", "Jobber", "Local Car Wash", "State Farm"],
        "sample_org_names": ["FreshStart Cleaning", "CityShine Services", "Blue Door Clean Co."],
    },
    "gig_worker": {
        "label": "Gig Worker / Solo Operator",
        "services": [
            "Ride Share",
            "Food Delivery",
            "Freelance Design",
            "Handyman Jobs",
            "Photography Session",
            "Virtual Assistance",
            "On-Demand Errands",
        ],
        "lead_sources": ["platform", "referral", "instagram", "tiktok", "direct_message", "repeat_customer"],
        "expense_categories": ["fuel", "software", "equipment", "phone", "marketing", "insurance", "misc"],
        "key_metrics": ["net_income", "repeat_customer_pct", "top_service_mix", "expense_ratio"],
        "quick_wins": [
            "Solo operators usually grow fastest by identifying their top-paying service and dropping low-margin work",
            "Separating platform fees, fuel, and equipment costs makes take-home profit much clearer",
        ],
        "sample_customers": [
            "Repeat Local Clients",
            "Platform Orders",
            "Small Business Owners",
            "Event Bookers",
            "Neighborhood Referrals",
        ],
        "sample_vendors": ["Uber", "DoorDash", "Canva", "Adobe", "T-Mobile"],
        "sample_org_names": ["SideQuest Studio", "Everyday Hustle Co.", "City Sprint Services"],
    },
    "salon_spa": {
        "label": "Salon / Spa",
        "services": [
            "Haircut",
            "Color Service",
            "Braids / Styling",
            "Facial",
            "Waxing",
            "Massage",
            "Membership Package",
        ],
        "lead_sources": ["instagram", "referral", "google", "walk_in", "facebook", "repeat_customer"],
        "expense_categories": ["payroll", "rent", "supplies", "software", "marketing", "insurance", "misc"],
        "key_metrics": ["repeat_customer_pct", "avg_ticket", "service_mix", "rebooking_rate"],
        "quick_wins": [
            "Rebooking before checkout is one of the simplest ways to increase recurring revenue",
            "Track product upsells separately from service revenue so you can see margin clearly",
        ],
        "sample_customers": [
            "Monthly Color Clients",
            "Weekend Appointment Guests",
            "Bridal Parties",
            "Skincare Members",
            "Neighborhood Walk-Ins",
        ],
        "sample_vendors": ["SalonCentric", "Square", "GlossGenius", "Local Laundry", "Beauty Supply Hub"],
        "sample_org_names": ["Velvet Room Studio", "Glow District Spa", "Studio 38 Collective"],
    },
}


def get_template(industry: str | None) -> IndustryTemplate | None:
    if not industry:
        return None
    return TEMPLATES.get(industry.lower())


def list_templates() -> list[dict]:
    return [{"key": k, "label": v["label"]} for k, v in TEMPLATES.items()]
