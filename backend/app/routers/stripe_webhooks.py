"""
Stripe webhook router.

IMPORTANT: This endpoint must receive the raw request body (bytes),
not the parsed JSON body. FastAPI's dependency injection handles this correctly
using Request.body() directly.

Webhook events handled:
  - customer.subscription.created
  - customer.subscription.updated
  - customer.subscription.deleted
  - checkout.session.completed
"""
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Annotated

from ..auth import AuthContext, get_auth
from ..config import settings
from ..database import get_db
from ..services.stripe_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook,
    sync_subscription,
)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout")
def start_checkout(
    plan: str,
    auth: Annotated[AuthContext, Depends(get_auth)],
):
    """Create a Stripe Checkout session for a plan upgrade."""
    db = get_db()
    org = db.table("organizations").select("name").eq("id", auth.org_id).single().execute()

    url = create_checkout_session(
        db=db,
        org_id=auth.org_id,
        org_name=org.data["name"],
        user_email=f"{auth.user_id}@clerk.placeholder",  # replace with real email from Clerk API if needed
        plan=plan,
        success_url=f"{settings.frontend_url}/billing/success?plan={plan}",
        cancel_url=f"{settings.frontend_url}/billing",
    )
    return {"checkout_url": url}


@router.post("/portal")
def billing_portal(auth: Annotated[AuthContext, Depends(get_auth)]):
    """Return a Stripe Customer Portal URL for managing subscription."""
    db = get_db()
    url = create_portal_session(db, auth.org_id, return_url=f"{settings.frontend_url}/billing")
    return {"portal_url": url}


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    """
    Raw Stripe webhook receiver.
    Must be excluded from auth middleware — Stripe signs it differently.
    """
    payload    = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = handle_webhook(payload, sig_header)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature.")

    db = get_db()
    event_type = event["type"]

    if event_type in ("customer.subscription.created", "customer.subscription.updated"):
        sync_subscription(db, event["data"]["object"])

    elif event_type == "customer.subscription.deleted":
        sub = event["data"]["object"]
        org_id = sub.metadata.get("lbt_org_id")
        if org_id:
            db.table("organizations").update({
                "subscription_status": "inactive",
                "plan": "basic",
            }).eq("id", org_id).execute()

    elif event_type == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("subscription"):
            sub = stripe.Subscription.retrieve(session["subscription"])
            sync_subscription(db, sub)

    return JSONResponse({"received": True})
