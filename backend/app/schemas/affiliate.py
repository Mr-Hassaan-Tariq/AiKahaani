"""
Affiliate domain Pydantic schemas.

Request/response models for Tolt affiliate tracking endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TrackClickRequest(BaseModel):
    referral_code: str = Field(..., min_length=1, max_length=100)
    page_url: str = Field(..., min_length=1, max_length=2000)
    device_type: str = Field("desktop", pattern="^(desktop|mobile|tablet)$")
    param_name: str = Field("via", max_length=50)


class TrackClickResponse(BaseModel):
    partner_id: Optional[str] = None
    referral_code: str
    message: str
