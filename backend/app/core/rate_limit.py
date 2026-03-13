"""
Rate limiting configuration (slowapi).

Strategy:
  - Authenticated endpoints key by user ID so different users on the same
    office/proxy IP don't block each other.
  - Unauthenticated endpoints (signup, magic-link) key by IP address.
  - Limits are intentionally tight on AI generation endpoints (expensive) and
    looser on read-only endpoints.

Limits applied:
  Auth (IP-keyed):
    POST /auth/signup              5/hour
    POST /auth/magic-link          5/10minutes
    POST /auth/magic-link/verify   10/minute
    POST /auth/google              20/minute
    POST /auth/refresh             30/minute

  AI generation (user-keyed):
    POST /scripts/titles/generate              10/minute
    POST /scripts/outlines/generate            5/minute
    POST /scripts/outlines/{id}/script         3/minute
"""

from fastapi import Request
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def _key_by_user_or_ip(request: Request) -> str:
    """
    Rate-limit key function:
      - If request carries a valid Bearer JWT, returns "user:<id>"
      - Otherwise returns the client IP (X-Forwarded-For → direct IP)

    No exception is raised on bad tokens — we fall through to IP silently.
    Auth validity is separately enforced by get_current_user().
    """
    try:
        auth = request.headers.get("authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            if sub := payload.get("sub"):
                return f"user:{sub}"
    except (JWTError, Exception):
        pass
    return get_remote_address(request)


# Module-level singleton — import `limiter` everywhere rate limits are needed.
limiter = Limiter(key_func=_key_by_user_or_ip, default_limits=[])
