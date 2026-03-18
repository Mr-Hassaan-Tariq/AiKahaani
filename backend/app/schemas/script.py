"""
Script domain Pydantic schemas.

Request/response models for title generation, outline generation,
and full script generation endpoints.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ── Shared ────────────────────────────────────────────────────────────────────


class ToneOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TemplateStyleOut(BaseModel):
    id: int
    name: str
    min_length: int
    max_length: int
    duration: int
    outline_sections: int
    description: str

    model_config = {"from_attributes": True}


# ── Title Generation ───────────────────────────────────────────────────────────


class GenerateTitlesRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    title_count: int = Field(6, ge=1, le=20)
    tones: Optional[List[str]] = None


class TitleItemOut(BaseModel):
    title: str
    angle: Optional[str] = None
    tension_pair: Optional[List[str]] = None
    levers: Optional[List[str]] = None
    emotion_target: Optional[str] = None
    power_words: Optional[List[str]] = None
    length_chars: Optional[int] = None
    word_count: Optional[int] = None
    truncation_safe: Optional[bool] = None
    notes: Optional[str] = None


class TitleGenerationOut(BaseModel):
    id: uuid.UUID
    generation_type: str
    titles: List[Dict[str, Any]]
    titles_count: int
    tones: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateTitlesResponse(BaseModel):
    generation: TitleGenerationOut
    titles: List[TitleItemOut]
    metadata: Dict[str, Any]


# ── Outline Generation ─────────────────────────────────────────────────────────


class GenerateOutlineRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=5000)
    tones: Optional[List[int]] = Field(
        None, description="Tone IDs (from /v1/scripts/tones)"
    )
    template_style_id: Optional[int] = Field(None, description="TemplateStyle ID")
    min_length: Optional[int] = Field(None, ge=100)
    max_length: Optional[int] = Field(None, ge=100)
    title: Optional[str] = Field(None, max_length=300)
    niche_id: Optional[int] = None
    article_url: Optional[str] = Field(None, max_length=2000)
    youtube_url: Optional[str] = Field(None, max_length=2000)

    @field_validator("tones")
    @classmethod
    def limit_tones(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v and len(v) > 5:
            raise ValueError("Maximum 5 tones allowed")
        return v


class OutlineSectionOut(BaseModel):
    title: str
    description: Optional[str] = None
    key_points: List[str] = []
    timing: Optional[str] = None
    transition: Optional[str] = None
    content: Optional[str] = None


class ScriptOutlineOut(BaseModel):
    id: uuid.UUID
    title: str
    outline_text: str
    outline_data: Dict[str, Any]
    section_order: List[int]
    status: str
    openai_model: str
    tokens_used: int
    generation_time: float
    tones: List[ToneOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerateOutlineResponse(BaseModel):
    outline: ScriptOutlineOut
    metadata: Dict[str, Any]
    is_script_allowed: bool = True


# ── Script Generation ──────────────────────────────────────────────────────────


class GenerateScriptRequest(BaseModel):
    """Body is optional — all parameters are read from the stored outline."""

    template_style_id: Optional[int] = Field(
        None, description="Override the template style stored in the outline"
    )


class ScriptSectionOut(BaseModel):
    title: str
    content: str
    word_count: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    section_type: Optional[str] = None


class FullScriptOut(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    sections: List[Dict[str, Any]]
    word_count: int
    estimated_duration: float
    status: str
    openai_model: str
    tokens_used: int
    generation_time: float
    outline_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerateScriptResponse(BaseModel):
    script: FullScriptOut
    metadata: Dict[str, Any]


# ── Lookup endpoints ───────────────────────────────────────────────────────────


class TonesListResponse(BaseModel):
    tones: List[ToneOut]


class TemplateStylesListResponse(BaseModel):
    template_styles: List[TemplateStyleOut]


# ── Script config (new-script UI) ────────────────────────────────────────────


class LengthRangeOut(BaseModel):
    min: int
    max: int
    default: int


class TemplateStyleConfigOut(BaseModel):
    """
    Template style shape expected by the web-app's `GenerationPromptType`.

    Backend DB model does not store `word_range`, so the config endpoint computes
    it from `min_length` and `max_length`.
    """

    id: int
    name: str
    min_length: int
    max_length: int
    duration: int
    description: str
    word_range: str


class ScriptConfigOut(BaseModel):
    tones: List[ToneOut]
    template_styles: List[TemplateStyleConfigOut]
    length_range: LengthRangeOut


# ── Outline/Script list/detail ─────────────────────────────────────────────────


class OutlineListResponse(BaseModel):
    outlines: List[ScriptOutlineOut]
    total: int


class ScriptListResponse(BaseModel):
    scripts: List[FullScriptOut]
    total: int


class UpdateOutlineStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(draft|generated|saved)$")


class UpdateScriptStatusRequest(BaseModel):
    status: str = Field(..., pattern="^(draft|generated|saved)$")
