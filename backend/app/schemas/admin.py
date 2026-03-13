"""
Admin domain Pydantic schemas.

Request/response models for all admin-only endpoints:
  - User management (list, detail, update, activate/deactivate, role change)
  - Platform & user statistics
  - Niche CRUD
  - Usage reports & conversion funnel
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ── User Management ───────────────────────────────────────────────────────────


class AdminUserListOut(BaseModel):
    id: int
    email: str
    username: str
    fullname: str
    role: str
    plan: str
    is_active: bool
    is_email_verified: bool
    plan_expires_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserDetailOut(BaseModel):
    id: int
    email: str
    username: str
    fullname: str
    preferred_language: str
    profile_picture_url: Optional[str] = None
    role: str
    plan: str
    plan_expires_at: Optional[datetime] = None
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserUpdateRequest(BaseModel):
    """Partial update — only provided fields are changed."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, max_length=150)
    fullname: Optional[str] = Field(None, max_length=255)
    preferred_language: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None


class AdminRoleUpdateRequest(BaseModel):
    role: str = Field(..., pattern="^(user|admin|super_admin)$")


# ── Stats ─────────────────────────────────────────────────────────────────────


class UserStatsOut(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    verified_users: int
    admin_count: int
    user_count: int
    new_this_week: int
    pro_users: int
    free_users: int


class FeatureUsageOut(BaseModel):
    script_generator: int
    title_generator: int
    niche_vault: int


class PlatformStatsOut(BaseModel):
    total_users: int
    new_users_this_week: int
    feature_usage: FeatureUsageOut


# ── Niche Management ──────────────────────────────────────────────────────────


class AdminNicheCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    prompt: str = Field(..., min_length=1)
    thumbnail_url: Optional[str] = Field(None, max_length=2000)
    script_structure: Dict[str, Any] = {}
    tone: List[str] = []
    pacing: List[str] = []
    top_channels: Optional[str] = None
    best_for: Optional[str] = None
    status: str = Field("active", pattern="^(active|inactive)$")


class AdminNicheUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    tagline: Optional[str] = Field(None, max_length=500)
    prompt: Optional[str] = Field(None, min_length=1)
    thumbnail_url: Optional[str] = Field(None, max_length=2000)
    script_structure: Optional[Dict[str, Any]] = None
    tone: Optional[List[str]] = None
    pacing: Optional[List[str]] = None
    top_channels: Optional[str] = None
    best_for: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class AdminNicheOut(BaseModel):
    id: int
    title: str
    tagline: Optional[str] = None
    prompt: str
    thumbnail_url: Optional[str] = None
    script_structure: Dict[str, Any] = {}
    tone: List[Any] = []
    pacing: List[Any] = []
    top_channels: Optional[str] = None
    best_for: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Reports ───────────────────────────────────────────────────────────────────


class UserReportItemOut(BaseModel):
    name: str
    email: str
    total_titles_generated: int
    total_short_scripts: int
    total_medium_scripts: int
    total_long_scripts: int


class ConversionFunnelItemOut(BaseModel):
    name: str
    email: str
    plan: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
