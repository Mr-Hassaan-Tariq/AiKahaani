"""
Shared test fixtures.

Environment variables are set BEFORE any app module is imported so that
pydantic-settings picks them up. This avoids the need for a real .env file
during CI or local test runs.
"""

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

# ── Test environment ──────────────────────────────────────────────────────────
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-32chars!")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/video_scripts_test")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("DEBUG", "true")

# ── App imports (after env is set) ────────────────────────────────────────────
import pytest
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_current_admin, get_current_user
from app.core.security import create_access_token
from app.database import get_db
from app.main import app
from app.models.user import User, UserPlan, UserRole


# ── User factories ────────────────────────────────────────────────────────────


def make_mock_user(
    user_id: int = 1,
    role: UserRole = UserRole.user,
    plan: UserPlan = UserPlan.free,
    **kwargs,
) -> MagicMock:
    """Build a MagicMock that quacks like a User ORM object."""
    user = MagicMock(spec=User)
    user.id = user_id
    user.email = kwargs.get("email", f"user{user_id}@example.com")
    user.username = kwargs.get("username", f"user{user_id}")
    user.fullname = kwargs.get("fullname", "Test User")
    user.preferred_language = "en"
    user.profile_picture_url = None
    user.is_email_verified = True
    user.is_active = True
    user.role = role
    user.plan = plan
    user.plan_expires_at = None
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    user.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def regular_user() -> MagicMock:
    return make_mock_user(user_id=1)


@pytest.fixture
def admin_user() -> MagicMock:
    return make_mock_user(user_id=2, role=UserRole.admin)


@pytest.fixture
def mock_db() -> AsyncMock:
    """
    AsyncMock mimicking an AsyncSession.

    SQLAlchemy pattern:
      result = await session.execute(...)   ← async
      value   = result.scalar_one()         ← sync (regular method on CursorResult)

    So db.execute must be async (AsyncMock), but its return_value must be a
    plain MagicMock so that .scalar_one(), .scalars().all(), etc. return
    real values instead of coroutines.
    """
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one.return_value = 0
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result
    return db


@pytest.fixture
async def client(mock_db: AsyncMock, regular_user: MagicMock) -> AsyncClient:
    """Authenticated AsyncClient — user has regular role."""

    async def _db():
        yield mock_db

    async def _user():
        return regular_user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def admin_client(mock_db: AsyncMock, admin_user: MagicMock) -> AsyncClient:
    """Authenticated AsyncClient — user has admin role."""

    async def _db():
        yield mock_db

    async def _user():
        return admin_user

    async def _admin():
        return admin_user

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    app.dependency_overrides[get_current_admin] = _admin

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def anon_client() -> AsyncClient:
    """Unauthenticated AsyncClient — no dependency overrides."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
