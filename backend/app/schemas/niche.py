"""
Niche domain Pydantic schemas.

Request/response models for niches listing and detail endpoints.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel


class NicheToneOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class NichePacingOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class NicheOut(BaseModel):
    id: int
    title: str
    tagline: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tone: List[Any] = []
    pacing: List[Any] = []
    best_for: Optional[str] = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NicheDetailOut(NicheOut):
    """Full niche detail including structure and channels."""
    prompt: str
    script_structure: Dict[str, Any] = {}
    top_channels: Optional[str] = None
    niche_tones: List[NicheToneOut] = []
    niche_pacings: List[NichePacingOut] = []
    updated_at: datetime

    model_config = {"from_attributes": True}


class NicheListResponse(BaseModel):
    niches: List[NicheOut]
    total: int
