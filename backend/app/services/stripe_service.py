"""
Stripe integration service.

Handles:
  - Creating Stripe customers for organizations
  - Creating checkout sessions for subscription upgrades
  - Processing webhooks to sync subscription state
"""
import stripe
from supabase import Client

from ..config import settings, PLAN_PRICE_MAP

stripe.api_key = settings.stripe_secret_key


def get_or_create_stripe_customer(db: Client, org_id: str, org_name: str, email: str) -> str:
    """Return existing Stripe customer ID or create a new one."""
    org = db.table("organizations").select("stripe_customer_id").eq("id", org_id).single().execute()

    if org.data.get("stripe_customer_id"):
        return org.data["stripe_customer_id"]

    customer = stripe.Customer.create(
        name=org_name,
        email=email,
        metadata={"lbt_org_id": org_id},
    )

    db.table("organizations").update({"stripe_customer_id": customer.id}).eq("id", org_id).execute()
    return customer.id


def create_checkout_session(
    db: Client,
    org_id: str,
    org_name: str,
    user_email: str,
    plan: str,
    success_url: str,
    cancel_url: str,
) -> str:
    """Create a Stripe Checkout session and return the URL."""
    price_id = PLAN_PRICE_MAP.get(plan)
    if not price_id:
        raise ValueError(f"Unknown plan: {plan}")

    customer_id = get_or_create_stripe_customer(db, org_id, org_name, user_email)

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"lbt_org_id": org_id, "plan": plan},
        subscription_data={"metadata": {"lbt_org_id": org_id, "plan": plan}},
    )
    return session.url


def create_portal_session(db: Client, org_id: str, return_url: str) -> str:
    """Return a Stripe billing portal URL for the org."""
    org = db.table("organizations").select("stripe_customer_id").eq("id", org_id).single().execute()
    customer_id = org.data.get("stripe_customer_id")
    if not customer_id:
        raise ValueError("No Stripe customer on file. Subscribe first.")

    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Verify and parse a Stripe webhook. Returns the event."""
    event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    return event


def sync_subscription(db: Client, subscription: stripe.Subscription) -> None:
    """
    Sync a Stripe subscription to the organizations table.
    Called from the webhook handler.
    """
    org_id = subscription.metadata.get("lbt_org_id")
    plan   = subscription.metadata.get("plan", "basic")

    if not org_id:
        return  # subscription not tied to an org (shouldn't happen)

    status_map = {
        "active":            "active",
        "trialing":          "active",
        "past_due":          "past_due",
        "canceled":          "inactive",
        "unpaid":            "past_due",
        "incomplete":        "inactive",
        "incomplete_expired":"inactive",
    }

    db.table("organizations").update({
        "stripe_subscription_id": subscription.id,
        "subscription_status":    status_map.get(subscription.status, "inactive"),
        "plan":                   plan,
    }).eq("id", org_id).execute()
