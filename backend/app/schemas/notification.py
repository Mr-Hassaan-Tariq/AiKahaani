"""
Notification domain Pydantic schemas.

Request/response models for notification listing and read-status endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    extra_data: Dict[str, Any] = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    notifications: List[NotificationOut]
    total: int
    unread_count: int
