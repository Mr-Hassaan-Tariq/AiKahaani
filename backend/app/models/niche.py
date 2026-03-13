"""
Niches domain models.

Tables:
- niches        — pre-defined content niches (writing style injected into AI prompts)
- niche_tones   — individual tone records per niche (richer than the tones lookup table)
- niche_pacings — pacing style records per niche
"""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.script import ScriptOutline


# ── Enums ────────────────────────────────────────────────────────────────────


class NicheStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


# ── Models ───────────────────────────────────────────────────────────────────


class Niche(Base, TimestampMixin):
    __tablename__ = "niches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script_structure: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    tone: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    pacing: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    top_channels: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    best_for: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[NicheStatus] = mapped_column(
        Enum(NicheStatus, name="niche_status"),
        nullable=False,
        server_default=NicheStatus.active.value,
    )

    # Relationships
    niche_tones: Mapped[list["NicheTone"]] = relationship(
        "NicheTone", back_populates="niche", cascade="all, delete-orphan"
    )
    niche_pacings: Mapped[list["NichePacing"]] = relationship(
        "NichePacing", back_populates="niche", cascade="all, delete-orphan"
    )
    script_outlines: Mapped[list["ScriptOutline"]] = relationship(
        "ScriptOutline", back_populates="niche"
    )

    __table_args__ = (Index("ix_niches_status", "status"),)

    def __repr__(self) -> str:
        return f"<Niche id={self.id} title={self.title!r} status={self.status}>"


class NicheTone(Base, TimestampMixin):
    """Niche-specific tone descriptors — richer/contextual vs. the global tones lookup."""

    __tablename__ = "niche_tones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    niche_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("niches.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    niche: Mapped["Niche"] = relationship("Niche", back_populates="niche_tones")

    __table_args__ = (Index("ix_niche_tones_niche_id", "niche_id"),)

    def __repr__(self) -> str:
        return f"<NicheTone niche_id={self.niche_id} name={self.name!r}>"


class NichePacing(Base, TimestampMixin):
    """Pacing style descriptors for a niche."""

    __tablename__ = "niche_pacings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    niche_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("niches.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    niche: Mapped["Niche"] = relationship("Niche", back_populates="niche_pacings")

    __table_args__ = (Index("ix_niche_pacings_niche_id", "niche_id"),)

    def __repr__(self) -> str:
        return f"<NichePacing niche_id={self.niche_id} name={self.name!r}>"
