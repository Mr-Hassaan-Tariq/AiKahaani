"""
SQLAlchemy declarative base and shared mixins.

All models inherit from Base. TimestampMixin adds created_at / updated_at
with server-side defaults and an onupdate trigger so the application never
has to set these manually.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at to any model.

    Both use server-side defaults (PostgreSQL now()) so they are set even
    when rows are inserted outside of the application (e.g., migrations,
    seed scripts). updated_at is also set on every UPDATE via onupdate.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
