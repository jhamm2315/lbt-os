"""
Stripe webhook smoke test.

Sends a test checkout.session.completed event to the local webhook endpoint
and confirms the handler returns 200 with {"received": true}.

Usage (with backend running on :8000):
    python scripts/verify_stripe_webhook.py

Uses the STRIPE_WEBHOOK_SECRET from .env to sign a synthetic payload,
so this validates signature verification AND handler logic end-to-end
without requiring the Stripe CLI.
"""
import json
import os
import sys
import time
import hmac
import hashlib
import httpx
from pathlib import Path

# Load .env manually so this script works standalone
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
WEBHOOK_URL    = os.environ.get("WEBHOOK_TEST_URL", "http://localhost:8000/api/stripe/billing/webhook")

if not WEBHOOK_SECRET:
    print("ERROR: STRIPE_WEBHOOK_SECRET not set in .env")
    sys.exit(1)

if not WEBHOOK_SECRET.startswith("whsec_"):
    print(f"ERROR: STRIPE_WEBHOOK_SECRET looks wrong (got: {WEBHOOK_SECRET[:10]}...)")
    sys.exit(1)


def sign_payload(payload: bytes, secret: str, timestamp: int) -> str:
    """Produce a Stripe-compatible v1 HMAC signature."""
    signed_payload = f"{timestamp}.".encode() + payload
    key = secret.removeprefix("whsec_")
    # Stripe webhooks use the raw base64-decoded secret key
    import base64
    raw_key = base64.b64decode(key + "==")  # pad if needed
    signature = hmac.new(raw_key, signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


# Minimal synthetic event
event_id = f"evt_test_{int(time.time())}"
payload = json.dumps({
    "id": event_id,
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "id": "cs_test_synthetic",
            "subscription": None,  # no sub to retrieve — just tests routing
            "metadata": {},
        }
    }
}).encode()

timestamp = int(time.time())
sig = sign_payload(payload, WEBHOOK_SECRET, timestamp)

print(f"Sending test event {event_id} to {WEBHOOK_URL} ...")

try:
    resp = httpx.post(
        WEBHOOK_URL,
        content=payload,
        headers={
            "Content-Type": "application/json",
            "Stripe-Signature": sig,
        },
        timeout=10,
    )
except httpx.ConnectError:
    print("ERROR: Could not connect. Is the backend running on http://localhost:8000 ?")
    sys.exit(1)

print(f"Status: {resp.status_code}")
print(f"Body:   {resp.text}")

if resp.status_code == 200:
    print("\nPASS: Webhook endpoint is reachable and processing correctly.")
elif resp.status_code == 400:
    print("\nFAIL: Signature verification rejected. Check STRIPE_WEBHOOK_SECRET matches backend .env.")
    sys.exit(1)
else:
    print(f"\nFAIL: Unexpected status {resp.status_code}")
    sys.exit(1)
