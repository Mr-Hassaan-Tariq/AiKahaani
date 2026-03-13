"""
SQLAlchemy model registry.

Import all models here so that:
1. Alembic autogenerate can detect every table via Base.metadata
2. Relationship back-references resolve correctly (all models in the same
   mapper configuration before the first query)

Usage:
    from app.models import User, Niche, ...
    from app.models.base import Base  # for metadata
"""

from app.models.base import Base, TimestampMixin
from app.models.notification import Notification, NotificationType
from app.models.niche import Niche, NichePacing, NicheStatus, NicheTone
from app.models.script import (
    FullScript,
    OpenAIRunLog,
    OpenAIRunStatus,
    OpenAIRunType,
    OutlineTone,
    ScriptOutline,
    ScriptStatus,
    TemplateStyle,
    TitleGeneration,
    TitleGenerationType,
    Tone,
    ToneScope,
    OutlineStatus,
)
from app.models.user import (
    AuthTokenType,
    User,
    UserAuthToken,
    UserPlan,
    UserRefreshToken,
    UserRole,
    UserSettings,
)

__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    # User domain
    "User",
    "UserRole",
    "UserPlan",
    "UserSettings",
    "UserRefreshToken",
    "UserAuthToken",
    "AuthTokenType",
    # Script domain
    "Tone",
    "ToneScope",
    "TemplateStyle",
    "ScriptOutline",
    "OutlineStatus",
    "OutlineTone",
    "FullScript",
    "ScriptStatus",
    "TitleGeneration",
    "TitleGenerationType",
    "OpenAIRunLog",
    "OpenAIRunType",
    "OpenAIRunStatus",
    # Niche domain
    "Niche",
    "NicheStatus",
    "NicheTone",
    "NichePacing",
    # Notification domain
    "Notification",
    "NotificationType",
]
