"""
Clerk JWT verification.

Derives the JWKS URL from the publishable key so no secret key is needed
for token verification — uses Clerk's standard .well-known endpoint.
"""
import base64
import time
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import settings
from .database import get_db

bearer_scheme = HTTPBearer()

_jwks_cache: dict = {}
_jwks_fetched_at: float = 0
JWKS_TTL = 3600


def _clerk_jwks_url() -> str:
    """Derive the JWKS URL from the Clerk publishable key.

    Publishable key format: pk_test_<base64(instance-host)>$
    JWKS lives at: https://<instance-host>/.well-known/jwks.json
    """
    pk = settings.clerk_publishable_key
    b64 = pk.split("_", 2)[2].rstrip("$")
    padding = 4 - len(b64) % 4
    if padding != 4:
        b64 += "=" * padding
    host = base64.b64decode(b64).decode("utf-8").rstrip("$")
    return f"https://{host}/.well-known/jwks.json"


def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at
    if time.time() - _jwks_fetched_at > JWKS_TTL:
        url = _clerk_jwks_url()
        resp = httpx.get(url, timeout=5)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_fetched_at = time.time()
    return _jwks_cache


def _verify_clerk_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            _get_jwks(),
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        )


class UserContext:
    """Minimal auth — verified user only. Used for onboarding (no org yet)."""
    def __init__(self, user_id: str):
        self.user_id = user_id


class AuthContext:
    """Full auth — verified user with a resolved org UUID."""
    def __init__(self, user_id: str, org_id: str, plan: str = "basic"):
        self.user_id = user_id
        self.org_id  = org_id
        self.plan    = plan


async def get_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> UserContext:
    """Verify JWT, return user. No org required — safe for onboarding."""
    payload = _verify_clerk_jwt(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub claim.")
    return UserContext(user_id=user_id)


async def get_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> AuthContext:
    """Verify JWT and resolve the user's organization."""
    payload = _verify_clerk_jwt(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub claim.")

    db = get_db()
    result = (
        db.table("organizations")
        .select("id, plan, subscription_status")
        .eq("clerk_user_id", user_id)
        .maybe_single()
        .execute()
    )

    if result is None or not result.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization found. Complete onboarding first.",
        )

    return AuthContext(
        user_id=user_id,
        org_id=result.data["id"],
        plan=result.data.get("plan", "basic"),
    )


def require_plan(minimum_plan: str):
    """Gate a route to a minimum subscription tier."""
    PLAN_ORDER = {"basic": 0, "pro": 1, "premium": 2}

    def _check(auth: AuthContext = Depends(get_auth)) -> AuthContext:
        if PLAN_ORDER.get(auth.plan, 0) < PLAN_ORDER.get(minimum_plan, 99):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires the {minimum_plan} plan or higher.",
            )
        return auth

    return _check
