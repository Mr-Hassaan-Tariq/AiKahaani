"""
User domain models.

Tables:
- users                — core user record
- user_settings        — JSONB preferences (notification + privacy)
- user_refresh_tokens  — active refresh tokens (session management)
- user_one_time_tokens — magic link + email verification tokens
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    UUID,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
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
    from app.models.notification import Notification
    from app.models.script import FullScript, OpenAIRunLog, ScriptOutline, TitleGeneration


# ── Enums ────────────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    super_admin = "super_admin"


class UserPlan(str, enum.Enum):
    free = "free"
    pro = "pro"


class OneTimeTokenType(str, enum.Enum):
    magic_link = "magic_link"
    email_verification = "email_verification"


# ── Models ───────────────────────────────────────────────────────────────────


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False, server_default="")
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), nullable=False, server_default="en")
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        server_default=UserRole.user.value,
    )
    plan: Mapped[UserPlan] = mapped_column(
        Enum(UserPlan, name="user_plan"),
        nullable=False,
        server_default=UserPlan.free.value,
    )
    plan_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["UserRefreshToken"]] = relationship(
        "UserRefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    auth_tokens: Mapped[list["UserOneTimeToken"]] = relationship(
        "UserOneTimeToken", back_populates="user", cascade="all, delete-orphan"
    )
    script_outlines: Mapped[list["ScriptOutline"]] = relationship(
        "ScriptOutline", back_populates="user", cascade="all, delete-orphan"
    )
    full_scripts: Mapped[list["FullScript"]] = relationship(
        "FullScript", back_populates="user", cascade="all, delete-orphan"
    )
    title_generations: Mapped[list["TitleGeneration"]] = relationship(
        "TitleGeneration", back_populates="user", cascade="all, delete-orphan"
    )
    openai_run_logs: Mapped[list["OpenAIRunLog"]] = relationship(
        "OpenAIRunLog", back_populates="user"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    notification_preferences: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    privacy_preferences: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id}>"


class UserRefreshToken(Base):
    """
    One row per active session. Created on login, deleted on logout.
    Only the SHA-256 hash of the raw refresh token is stored.
    """

    __tablename__ = "user_refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("ix_user_refresh_tokens_user_id", "user_id"),
        Index("ix_user_refresh_tokens_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<UserRefreshToken user_id={self.user_id} expires_at={self.expires_at}>"


class UserOneTimeToken(Base):
    """
    Short-lived tokens for magic links and email verification.
    No updated_at — tokens are write-once, then either consumed (is_used=True) or expired.
    """

    __tablename__ = "user_one_time_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_type: Mapped[OneTimeTokenType] = mapped_column(
        Enum(OneTimeTokenType, name="one_time_token_type"), nullable=False
    )
    token: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        server_default=func.gen_random_uuid(),
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="auth_tokens")

    __table_args__ = (
        Index("ix_user_one_time_tokens_user_id_token_type", "user_id", "token_type"),
        Index("ix_user_one_time_tokens_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<UserOneTimeToken user_id={self.user_id} type={self.token_type} used={self.is_used}>"
