"""
User domain Pydantic schemas.

Request/response models for user profile and settings endpoints.
"""

from typing import Any, Dict, Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Profile ───────────────────────────────────────────────────────────────────


class UserProfileOut(BaseModel):
    id: int
    email: str
    username: str
    fullname: str
    preferred_language: str
    profile_picture_url: Optional[str] = None
    is_email_verified: bool
    is_active: bool
    role: str
    plan: str
    plan_expires_at: Optional[datetime] = None
    tolt_customer_id: Optional[str] = None
    tolt_partner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    fullname: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=150)
    preferred_language: Optional[str] = Field(None, max_length=10)
    profile_picture_url: Optional[str] = Field(None, max_length=2000)

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and " " in v:
            raise ValueError("Username cannot contain spaces")
        return v.strip() if v else v


# ── Settings ──────────────────────────────────────────────────────────────────


class UserSettingsOut(BaseModel):
    notification_preferences: Dict[str, Any]
    privacy_preferences: Dict[str, Any]

    model_config = {"from_attributes": True}


class UpdateNotificationSettingsRequest(BaseModel):
    """Partial update — only provided keys are changed."""
    in_app_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    web_push_notifications: Optional[bool] = None
    new_script_generated: Optional[bool] = None
    account_or_plan_changes: Optional[bool] = None
    tips_content_inspiration: Optional[bool] = None
    feature_updates: Optional[bool] = None
    community_affiliate_updates: Optional[bool] = None


class UpdatePrivacySettingsRequest(BaseModel):
    """Partial update — only provided keys are changed."""
    allow_product_update_emails: Optional[bool] = None
    allow_anonymized_data_usage: Optional[bool] = None
