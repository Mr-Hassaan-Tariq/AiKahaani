"""
Users router — /api/v1/users/*

Endpoints:
  GET   /me                          — current user profile
  PATCH /me                          — update profile
  GET   /me/settings/notification    — notification preferences
  PATCH /me/settings/notification    — update notification preferences
  GET   /me/settings/privacy         — privacy preferences
  PATCH /me/settings/privacy         — update privacy preferences
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.core.responses import responses
from app.database import get_db
from app.models.user import User, UserSettings
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UpdateNotificationSettingsRequest,
    UpdatePrivacySettingsRequest,
    UpdateProfileRequest,
    UserProfileOut,
    UserSettingsOut,
)

logger = logging.getLogger(__name__)

users_router = APIRouter(tags=["Users"])


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _get_or_create_settings(db: AsyncSession, user_id: int) -> UserSettings:
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings_obj = result.scalar_one_or_none()
    if not settings_obj:
        settings_obj = UserSettings(
            user_id=user_id,
            notification_preferences={},
            privacy_preferences={},
        )
        db.add(settings_obj)
        await db.flush()
    return settings_obj


# ── Profile ───────────────────────────────────────────────────────────────────


@users_router.get("/me", response_model=ApiResponse[UserProfileOut])
async def get_me(user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return responses.ok(
        data=UserProfileOut.model_validate(user),
        message="Profile retrieved",
    )


@users_router.patch("/me", response_model=ApiResponse[UserProfileOut])
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile fields (partial update)."""
    if body.username and body.username != user.username:
        existing = await db.execute(
            select(User).where(User.username == body.username, User.id != user.id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    logger.info("[USERS] Profile updated for user_id=%d", user.id)
    return responses.ok(
        data=UserProfileOut.model_validate(user),
        message="Profile updated",
    )


# ── Settings: Notification ────────────────────────────────────────────────────


@users_router.get(
    "/me/settings/notification", response_model=ApiResponse[UserSettingsOut]
)
async def get_notification_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings_obj = await _get_or_create_settings(db, user.id)
    await db.commit()
    return responses.ok(
        data=UserSettingsOut.model_validate(settings_obj),
        message="Notification settings retrieved",
    )


@users_router.patch(
    "/me/settings/notification", response_model=ApiResponse[UserSettingsOut]
)
async def update_notification_settings(
    body: UpdateNotificationSettingsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Merge provided keys into notification_preferences JSONB."""
    settings_obj = await _get_or_create_settings(db, user.id)
    updates = body.model_dump(exclude_none=True)
    prefs = dict(settings_obj.notification_preferences or {})
    prefs.update(updates)
    settings_obj.notification_preferences = prefs
    await db.commit()
    await db.refresh(settings_obj)
    return responses.ok(
        data=UserSettingsOut.model_validate(settings_obj),
        message="Notification settings updated",
    )


# ── Settings: Privacy ─────────────────────────────────────────────────────────


@users_router.get(
    "/me/settings/privacy", response_model=ApiResponse[UserSettingsOut]
)
async def get_privacy_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings_obj = await _get_or_create_settings(db, user.id)
    await db.commit()
    return responses.ok(
        data=UserSettingsOut.model_validate(settings_obj),
        message="Privacy settings retrieved",
    )


@users_router.patch(
    "/me/settings/privacy", response_model=ApiResponse[UserSettingsOut]
)
async def update_privacy_settings(
    body: UpdatePrivacySettingsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Merge provided keys into privacy_preferences JSONB."""
    settings_obj = await _get_or_create_settings(db, user.id)
    updates = body.model_dump(exclude_none=True)
    prefs = dict(settings_obj.privacy_preferences or {})
    prefs.update(updates)
    settings_obj.privacy_preferences = prefs
    await db.commit()
    await db.refresh(settings_obj)
    return responses.ok(
        data=UserSettingsOut.model_validate(settings_obj),
        message="Privacy settings updated",
    )
