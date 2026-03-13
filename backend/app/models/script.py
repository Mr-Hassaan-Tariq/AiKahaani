"""
Scripts domain models.

Tables:
- tones               — lookup: tone names with scope (script / title / both)
- template_styles     — lookup: video length presets
- script_outlines     — AI-generated outline (primary generation step)
- outline_tones       — M2M: outlines ↔ tones
- full_scripts        — AI-generated script produced from an outline
- title_generations   — AI-generated title sets (merged script_titles + user_titles)
- openai_run_logs     — operational audit log for every OpenAI call
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    UUID,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.niche import Niche
    from app.models.user import User


# ── Enums ────────────────────────────────────────────────────────────────────


class ToneScope(str, enum.Enum):
    script = "script"
    title = "title"
    both = "both"


class OutlineStatus(str, enum.Enum):
    draft = "draft"
    generated = "generated"
    saved = "saved"


class ScriptStatus(str, enum.Enum):
    draft = "draft"
    generated = "generated"
    saved = "saved"


class TitleGenerationType(str, enum.Enum):
    from_script = "from_script"
    from_idea = "from_idea"
    optimized = "optimized"


class OpenAIRunType(str, enum.Enum):
    outline_generation = "outline_generation"
    script_generation = "script_generation"
    title_generation = "title_generation"
    image_analysis = "image_analysis"


class OpenAIRunStatus(str, enum.Enum):
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# ── Models ───────────────────────────────────────────────────────────────────


class Tone(Base, TimestampMixin):
    __tablename__ = "tones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    scope: Mapped[ToneScope] = mapped_column(
        Enum(ToneScope, name="tone_scope"),
        nullable=False,
        server_default=ToneScope.both.value,
    )

    # Relationships
    outline_tones: Mapped[list["OutlineTone"]] = relationship(
        "OutlineTone", back_populates="tone", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("name", "scope", name="uq_tones_name_scope"),
        Index("ix_tones_scope", "scope"),
    )

    def __repr__(self) -> str:
        return f"<Tone name={self.name!r} scope={self.scope}>"


class TemplateStyle(Base, TimestampMixin):
    __tablename__ = "template_styles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    min_length: Mapped[int] = mapped_column(Integer, nullable=False)
    max_length: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    outline_sections: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")

    # Relationships
    script_outlines: Mapped[list["ScriptOutline"]] = relationship(
        "ScriptOutline", back_populates="template_style"
    )

    def __repr__(self) -> str:
        return f"<TemplateStyle name={self.name!r} sections={self.outline_sections}>"


class ScriptOutline(Base, TimestampMixin):
    __tablename__ = "script_outlines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    niche_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("niches.id", ondelete="SET NULL"), nullable=True
    )
    template_style_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("template_styles.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False, server_default="")
    outline_data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    outline_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    section_order: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    status: Mapped[OutlineStatus] = mapped_column(
        Enum(OutlineStatus, name="outline_status"),
        nullable=False,
        server_default=OutlineStatus.draft.value,
    )
    version: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    original_outline: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    openai_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    generation_time: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="script_outlines")
    niche: Mapped[Optional["Niche"]] = relationship("Niche", back_populates="script_outlines")
    template_style: Mapped[Optional["TemplateStyle"]] = relationship(
        "TemplateStyle", back_populates="script_outlines"
    )
    outline_tones: Mapped[list["OutlineTone"]] = relationship(
        "OutlineTone", back_populates="outline", cascade="all, delete-orphan"
    )
    full_scripts: Mapped[list["FullScript"]] = relationship(
        "FullScript", back_populates="outline", cascade="all, delete-orphan"
    )
    openai_run_logs: Mapped[list["OpenAIRunLog"]] = relationship(
        "OpenAIRunLog", back_populates="script_outline"
    )

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_script_outlines_version"),
        Index("ix_script_outlines_user_id", "user_id"),
        Index("ix_script_outlines_niche_id", "niche_id"),
        Index("ix_script_outlines_template_style_id", "template_style_id"),
        Index("ix_script_outlines_status", "status"),
        Index("ix_script_outlines_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ScriptOutline id={self.id} title={self.title!r} status={self.status}>"


class OutlineTone(Base):
    """Many-to-many: script_outlines ↔ tones."""

    __tablename__ = "outline_tones"

    outline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("script_outlines.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tone_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tones.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    outline: Mapped["ScriptOutline"] = relationship("ScriptOutline", back_populates="outline_tones")
    tone: Mapped["Tone"] = relationship("Tone", back_populates="outline_tones")

    __table_args__ = (Index("ix_outline_tones_tone_id", "tone_id"),)

    def __repr__(self) -> str:
        return f"<OutlineTone outline_id={self.outline_id} tone_id={self.tone_id}>"


class FullScript(Base, TimestampMixin):
    __tablename__ = "full_scripts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    outline_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("script_outlines.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sections: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    estimated_duration: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    status: Mapped[ScriptStatus] = mapped_column(
        Enum(ScriptStatus, name="script_status"),
        nullable=False,
        server_default=ScriptStatus.draft.value,
    )
    version: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    openai_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    generation_time: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="full_scripts")
    outline: Mapped["ScriptOutline"] = relationship("ScriptOutline", back_populates="full_scripts")
    title_generations: Mapped[list["TitleGeneration"]] = relationship(
        "TitleGeneration", back_populates="script"
    )
    openai_run_logs: Mapped[list["OpenAIRunLog"]] = relationship(
        "OpenAIRunLog", back_populates="full_script"
    )

    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_full_scripts_version"),
        CheckConstraint("word_count >= 0", name="ck_full_scripts_word_count"),
        CheckConstraint("estimated_duration >= 0.0", name="ck_full_scripts_estimated_duration"),
        Index("ix_full_scripts_user_id", "user_id"),
        Index("ix_full_scripts_outline_id", "outline_id"),
        Index("ix_full_scripts_status", "status"),
        Index("ix_full_scripts_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<FullScript id={self.id} title={self.title!r} status={self.status}>"


class TitleGeneration(Base, TimestampMixin):
    __tablename__ = "title_generations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    script_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("full_scripts.id", ondelete="SET NULL"),
        nullable=True,
    )
    generation_type: Mapped[TitleGenerationType] = mapped_column(
        Enum(TitleGenerationType, name="title_generation_type"), nullable=False
    )
    input_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tones: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    titles: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    titles_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="0")

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="title_generations")
    script: Mapped[Optional["FullScript"]] = relationship(
        "FullScript", back_populates="title_generations"
    )
    openai_run_logs: Mapped[list["OpenAIRunLog"]] = relationship(
        "OpenAIRunLog", back_populates="title_generation"
    )

    __table_args__ = (
        Index("ix_title_generations_user_id", "user_id"),
        Index("ix_title_generations_script_id", "script_id"),
        Index("ix_title_generations_generation_type", "generation_type"),
        Index("ix_title_generations_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<TitleGeneration id={self.id} type={self.generation_type} count={self.titles_count}>"


class OpenAIRunLog(Base, TimestampMixin):
    """
    Operational audit log for every OpenAI API call.
    Intentionally append-only — never update a log row.
    """

    __tablename__ = "openai_run_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    run_type: Mapped[OpenAIRunType] = mapped_column(
        Enum(OpenAIRunType, name="openai_run_type"), nullable=False
    )
    status: Mapped[OpenAIRunStatus] = mapped_column(
        Enum(OpenAIRunStatus, name="openai_run_status"),
        nullable=False,
        server_default=OpenAIRunStatus.completed.value,
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    generation_time: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.0")
    thread_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    run_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    assistant_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_search_used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    file_search_snippets: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script_outline_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("script_outlines.id", ondelete="SET NULL"),
        nullable=True,
    )
    full_script_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("full_scripts.id", ondelete="SET NULL"),
        nullable=True,
    )
    title_generation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("title_generations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="openai_run_logs")
    script_outline: Mapped[Optional["ScriptOutline"]] = relationship(
        "ScriptOutline", back_populates="openai_run_logs"
    )
    full_script: Mapped[Optional["FullScript"]] = relationship(
        "FullScript", back_populates="openai_run_logs"
    )
    title_generation: Mapped[Optional["TitleGeneration"]] = relationship(
        "TitleGeneration", back_populates="openai_run_logs"
    )

    __table_args__ = (
        Index("ix_openai_run_logs_user_id", "user_id"),
        Index("ix_openai_run_logs_run_type", "run_type"),
        Index("ix_openai_run_logs_status", "status"),
        Index("ix_openai_run_logs_thread_id", "thread_id"),
        Index("ix_openai_run_logs_run_id", "run_id"),
        Index("ix_openai_run_logs_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<OpenAIRunLog id={self.id} type={self.run_type} status={self.status}>"
