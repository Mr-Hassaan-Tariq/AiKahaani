"""
FastAPI dependencies for authentication and authorization.

Usage in route handlers:
    async def my_route(user: User = Depends(get_current_user)): ...
    async def admin_route(user: User = Depends(get_current_admin)): ...
    async def super_route(user: User = Depends(get_current_super_admin)): ...
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

_bearer = HTTPBearer(auto_error=False)

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)
_403_inactive = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Account disabled. Contact support.",
)
_403_admin = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied. Admin role required.",
)
_403_super = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied. Super admin role required.",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate the Bearer JWT and return the authenticated User.

    Checks:
    1. Token is present and parseable
    2. Token type is "access" (not a refresh token used as access)
    3. User exists in the database
    4. User is_active == True
    """
    if not credentials:
        raise _401

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise _401

    if payload.get("type") != "access":
        raise _401

    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError):
        raise _401

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise _401

    if not user.is_active:
        raise _403_inactive

    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require admin or super_admin role."""
    if user.role not in (UserRole.admin, UserRole.super_admin):
        raise _403_admin
    return user


async def get_current_super_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require super_admin role only."""
    if user.role != UserRole.super_admin:
        raise _403_super
    return user
