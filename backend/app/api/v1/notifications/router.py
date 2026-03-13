"""
Notifications router — /api/v1/notifications/*

Endpoints:
  GET  /                     — list user's notifications (filterable, paginated)
  POST /{notification_id}/read  — mark single notification as read
  POST /read-all             — mark all user notifications as read
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.responses import responses
from app.database import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.notification import NotificationOut

logger = logging.getLogger(__name__)

notifications_router = APIRouter(tags=["Notifications"])


@notifications_router.get("", response_model=PaginatedResponse[NotificationOut])
async def list_notifications(
    is_read: bool | None = Query(None, description="Filter by read status"),
    notification_type: str | None = Query(None, description="Filter by type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's notifications."""
    base = select(Notification).where(Notification.user_id == user.id)

    if is_read is not None:
        base = base.where(Notification.is_read == is_read)

    if notification_type:
        try:
            nt = NotificationType(notification_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification_type. Valid values: {[e.value for e in NotificationType]}",
            )
        base = base.where(Notification.notification_type == nt)

    count_result = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total = count_result.scalar_one()

    result = await db.execute(
        base.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    )
    notifications = result.scalars().all()

    return responses.paginated(
        data=[NotificationOut.model_validate(n) for n in notifications],
        total=total,
        limit=limit,
        offset=offset,
        message="Notifications retrieved",
    )


@notifications_router.post(
    "/{notification_id}/read", response_model=ApiResponse[NotificationOut]
)
async def mark_notification_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return responses.ok(
        data=NotificationOut.model_validate(notification),
        message="Notification marked as read",
    )


@notifications_router.post("/read-all", response_model=ApiResponse[None])
async def mark_all_notifications_read(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all of the current user's unread notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    await db.commit()
    logger.info("[NOTIFICATIONS] All notifications marked read for user_id=%d", user.id)
    return responses.no_data(message="All notifications marked as read")
