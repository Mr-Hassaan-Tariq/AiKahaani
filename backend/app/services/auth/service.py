"""
Authentication service — all business logic for auth flows.

Responsibilities:
- Signup (email + password)
- Google OAuth (auth code or ID token)
- Magic link (send + verify)
- Admin login (email + password, admin/super_admin only)
- Token refresh
- Logout (delete refresh token row)
"""

import asyncio
import logging
import uuid
from datetime import timedelta, timezone
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.notification import Notification, NotificationType
from app.models.user import OneTimeTokenType, User, UserOneTimeToken, UserRefreshToken, UserRole
from app.services.email.service import send_magic_link_email

logger = logging.getLogger(__name__)

# Holds strong references to fire-and-forget background tasks so they aren't
# garbage-collected before they complete.
_background_tasks: set[asyncio.Task] = set()


# ── Internal helpers ──────────────────────────────────────────────────────────


async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def _get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def _create_token_pair(db: AsyncSession, user: User) -> tuple[str, str]:
    """Issue access + refresh tokens and persist the refresh token hash."""
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_row = UserRefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh),
        expires_at=get_refresh_token_expiry(),
    )
    db.add(token_row)
    await db.commit()

    return access, refresh


async def _create_welcome_notification(db: AsyncSession, user: User, is_new: bool) -> None:
    """Fire-and-forget welcome / welcome-back notification. Never raises."""
    try:
        title = "Welcome to Video Scripts!" if is_new else "Welcome back to Video Scripts!"
        name = user.fullname or user.username
        message = (
            f"Welcome to Video Scripts, {name}! Start exploring viral niches and create amazing scripts."
            if is_new
            else f"Welcome back to Video Scripts, {name}!"
        )
        notif = Notification(
            user_id=user.id,
            notification_type=NotificationType.account,
            title=title,
            message=message,
        )
        db.add(notif)
        await db.commit()
    except Exception as exc:
        logger.warning("Failed to create notification for user %s: %s", user.id, exc)
        await db.rollback()


# ── Signup ────────────────────────────────────────────────────────────────────


async def signup(
    db: AsyncSession,
    *,
    email: str,
    username: str,
    fullname: str,
    password: str,
) -> User:
    """
    Create a new user account.
    Raises ValueError with a human-readable message on validation failures.
    """
    # Check email uniqueness
    existing = await _get_user_by_email(db, email)
    if existing:
        raise ValueError("A user with this email already exists.")

    # Check username uniqueness
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none():
        raise ValueError("This username is already taken.")

    user = User(
        email=email,
        username=username,
        fullname=fullname,
        hashed_password=hash_password(password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await _create_welcome_notification(db, user, is_new=True)
    logger.info("New user signed up: %s", email)
    return user


# ── Google OAuth ──────────────────────────────────────────────────────────────


async def _exchange_google_auth_code(auth_code: str) -> str:
    """Exchange a Google authorization code for an ID token."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_oauth2_client_id,
                "client_secret": settings.google_oauth2_client_secret,
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": f"{settings.frontend_url.rstrip('/')}/signup",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if "id_token" not in data:
            raise ValueError("No ID token received from Google")
        return data["id_token"]


async def _verify_google_id_token(id_token: str) -> dict:
    """Verify a Google ID token via Google's tokeninfo endpoint."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
        if resp.status_code != 200:
            raise ValueError("Invalid Google ID token")
        data = resp.json()
        # Verify audience matches our client ID
        if data.get("aud") != settings.google_oauth2_client_id:
            raise ValueError("Google token audience mismatch")
        return data


async def google_auth(
    db: AsyncSession,
    *,
    id_token: str,
) -> tuple[str, str, User, bool]:
    """
    Authenticate via Google ID token or authorization code.

    Returns (access_token, refresh_token, user, created).
    Raises ValueError on invalid token, httpx.HTTPError on network issues.
    """
    if not settings.google_oauth2_client_id or not settings.google_oauth2_client_secret:
        raise RuntimeError("Google OAuth credentials not configured")

    # Handle authorization code (starts with "4/") vs ID token
    raw_token = id_token
    if id_token.startswith("4/"):
        logger.info("Exchanging Google authorization code")
        raw_token = await _exchange_google_auth_code(id_token)

    idinfo = await _verify_google_id_token(raw_token)

    if not idinfo.get("email_verified") in (True, "true"):
        raise ValueError("Email not verified by Google")

    email = idinfo["email"]
    fullname = f"{idinfo.get('given_name', '')} {idinfo.get('family_name', '')}".strip()[:255]
    username = email.split("@")[0]

    # get_or_create user
    user = await _get_user_by_email(db, email)
    created = False
    if not user:
        # Ensure username uniqueness
        base_username = username
        counter = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base_username}{counter}"
            counter += 1

        user = User(email=email, username=username, fullname=fullname, is_email_verified=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        created = True
        logger.info("New user created via Google OAuth: %s", email)
    else:
        logger.info("Existing user authenticated via Google: %s", email)

    if not user.is_active:
        raise PermissionError("Account disabled. Contact support.")

    access, refresh = await _create_token_pair(db, user)
    await _create_welcome_notification(db, user, is_new=created)
    return access, refresh, user, created


# ── Magic link ────────────────────────────────────────────────────────────────


async def send_magic_link(db: AsyncSession, *, email: str) -> bool:
    """
    Get-or-create user, generate a 30-minute magic link token, send email.
    Returns True if email was sent successfully.
    Raises PermissionError for inactive users.
    """
    username = email.split("@")[0]
    user = await _get_user_by_email(db, email)
    created = False

    if not user:
        # Auto-create user — passwordless signup
        base = username
        counter = 1
        while True:
            result = await db.execute(select(User).where(User.username == username))
            if not result.scalar_one_or_none():
                break
            username = f"{base}{counter}"
            counter += 1

        user = User(email=email, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        created = True
        logger.info("New user created via magic link: %s", email)

    if not user.is_active:
        raise PermissionError("Account disabled. Contact support.")

    # Create auth token (30 min expiry)
    now = datetime.now(timezone.utc)
    auth_token = UserOneTimeToken(
        user_id=user.id,
        token_type=OneTimeTokenType.magic_link,
        token=uuid.uuid4(),
        expires_at=now + timedelta(minutes=30),
    )
    db.add(auth_token)
    await db.commit()
    await db.refresh(auth_token)

    magic_link = f"{settings.frontend_url.rstrip('/')}/magic-link?token={auth_token.token}"

    # Fire email in the background — never block the API response on email delivery.
    task = asyncio.create_task(
        send_magic_link_email(
            to_email=email,
            user_name=user.fullname or user.username,
            magic_link=magic_link,
            is_new_user=created,
        )
    )
    # Keep a strong reference so the task isn't garbage-collected before it finishes.
    task.add_done_callback(lambda t: _background_tasks.discard(t))
    _background_tasks.add(task)

    return True


async def verify_magic_link(
    db: AsyncSession,
    *,
    token: str,
) -> tuple[str, str, User]:
    """
    Verify the magic link token and issue JWT tokens.

    Returns (access_token, refresh_token, user).
    Raises ValueError on invalid/expired token, PermissionError for inactive users.
    Token is single-use — marked as used after successful verification.
    """
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(UserOneTimeToken).where(
            UserOneTimeToken.token == uuid.UUID(token),
            UserOneTimeToken.token_type == OneTimeTokenType.magic_link,
            UserOneTimeToken.is_used == False,  # noqa: E712
            UserOneTimeToken.expires_at > now,
        )
    )
    auth_token = result.scalar_one_or_none()

    if not auth_token:
        raise ValueError("Invalid or expired magic link.")

    user = await _get_user_by_id(db, auth_token.user_id)

    if not user or not user.is_active:
        # Invalidate token even for inactive users
        auth_token.is_used = True
        await db.commit()
        raise PermissionError("Account disabled. Contact support.")

    # Mark token as used (single-use)
    auth_token.is_used = True
    await db.commit()

    access, refresh = await _create_token_pair(db, user)
    await _create_welcome_notification(db, user, is_new=False)

    logger.info("Magic link verified for user: %s", user.email)
    return access, refresh, user


# ── Admin login ───────────────────────────────────────────────────────────────


async def admin_login(
    db: AsyncSession,
    *,
    email: str,
    password: str,
) -> tuple[str, str, User]:
    """
    Authenticate an admin user with email + password.

    Returns (access_token, refresh_token, user).
    Raises ValueError on invalid credentials, PermissionError on access denied.
    """
    user = await _get_user_by_email(db, email)

    if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise PermissionError("Account disabled. Contact support.")

    if user.role not in (UserRole.admin, UserRole.super_admin):
        raise PermissionError("Access denied. Admin role required.")

    access, refresh = await _create_token_pair(db, user)

    await _create_welcome_notification(db, user, is_new=False)
    logger.info("Admin user logged in: %s", user.email)
    return access, refresh, user


# ── Token refresh ─────────────────────────────────────────────────────────────


async def refresh_tokens(
    db: AsyncSession,
    *,
    refresh_token: str,
) -> tuple[str, str]:
    """
    Validate the refresh token against the DB, check user is active,
    delete the old refresh token row, issue new token pair.

    Returns (new_access_token, new_refresh_token).
    Raises ValueError on invalid/expired token, PermissionError for inactive user.
    """
    from jose import JWTError
    from app.core.security import decode_token

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise ValueError("Invalid or expired refresh token.")

    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type.")

    user_id = int(payload["sub"])
    token_hash = hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UserRefreshToken).where(
            UserRefreshToken.user_id == user_id,
            UserRefreshToken.token_hash == token_hash,
            UserRefreshToken.expires_at > now,
        )
    )
    token_row = result.scalar_one_or_none()
    if not token_row:
        raise ValueError("Invalid or expired refresh token.")

    user = await _get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise PermissionError("Account disabled. Contact support.")

    # Rotate: delete old, issue new
    await db.delete(token_row)
    await db.commit()

    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    new_row = UserRefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=get_refresh_token_expiry(),
    )
    db.add(new_row)
    await db.commit()

    logger.debug("Tokens refreshed for user %s", user.id)
    return new_access, new_refresh


# ── Logout ────────────────────────────────────────────────────────────────────


async def logout(
    db: AsyncSession,
    *,
    user_id: int,
    refresh_token: str,
) -> None:
    """
    Delete the matching refresh token row.
    After this, the client can no longer get new access tokens.
    The current access token expires naturally within 15 minutes.
    """
    token_hash = hash_refresh_token(refresh_token)
    result = await db.execute(
        select(UserRefreshToken).where(
            UserRefreshToken.user_id == user_id,
            UserRefreshToken.token_hash == token_hash,
        )
    )
    token_row = result.scalar_one_or_none()
    if token_row:
        await db.delete(token_row)
        await db.commit()
        logger.info("User %s logged out, refresh token deleted", user_id)
    else:
        # Token not found — already logged out or expired. Not an error.
        logger.debug("Logout: no matching refresh token found for user %s", user_id)
