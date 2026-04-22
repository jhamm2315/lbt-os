"""
Shared rate-limiter instance — imported by main.py (attaches to app.state)
and by routers that apply @limiter.limit() decorators.

Key function: prefer Clerk user_id (from unverified JWT sub claim) over IP so
that rate limits are per-user rather than per-IP.  Signature verification still
happens in the get_auth dependency; we only read the claim here for key
derivation, which is safe.
"""
from fastapi import Request
from jose import jwt as _jose_jwt
from slowapi import Limiter
from slowapi.util import get_remote_address


def _rate_limit_key(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            claims = _jose_jwt.get_unverified_claims(auth[7:])
            sub = claims.get("sub")
            if sub:
                return sub
        except Exception:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)
