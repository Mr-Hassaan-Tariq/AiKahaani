"""
Security utilities: JWT encoding/decoding, password hashing, token hashing.

JWT strategy:
- Access tokens: short-lived (15 min by default, configurable)
- Refresh tokens: long-lived (7 days), stored as SHA-256 hash in user_refresh_tokens
- Logout = delete refresh token row → client can no longer get new access tokens
- is_active check in get_current_user catches deactivated accounts immediately
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    return _pwd_context.verify(plain, hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: int) -> str:
    """
    Create a short-lived JWT access token.

    Claims:
    - sub: str(user_id)
    - type: "access"
    - exp: now + ACCESS_TOKEN_EXPIRE_MINUTES
    """
    expire = _now_utc() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """
    Create a long-lived JWT refresh token.

    Claims:
    - sub: str(user_id)
    - type: "refresh"
    - jti: random hex (makes every refresh token unique)
    - exp: now + REFRESH_TOKEN_EXPIRE_DAYS
    """
    expire = _now_utc() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": secrets.token_hex(16),
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT. Raises JWTError on failure.
    Callers should catch JWTError and convert to HTTP 401.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def decode_token_unverified(token: str) -> dict:
    """
    Decode JWT without signature verification.
    Used only for extracting user_id for logging — NOT for auth decisions.
    """
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_signature": False},
        )
    except Exception:
        return {}


def get_refresh_token_expiry() -> datetime:
    """Return the expiry datetime for a new refresh token."""
    return _now_utc() + timedelta(days=settings.refresh_token_expire_days)


# ── Refresh token hashing ─────────────────────────────────────────────────────

def hash_refresh_token(raw_token: str) -> str:
    """
    SHA-256 hash of a raw refresh token string.
    Only the hash is stored in user_refresh_tokens — never the raw JWT.
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()
