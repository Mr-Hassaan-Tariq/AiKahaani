"""
Integration tests for /api/v1/admin/* endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.niche import Niche, NicheStatus
from app.models.user import User, UserPlan, UserRole


def make_mock_user_orm(user_id: int = 10, role: UserRole = UserRole.user) -> MagicMock:
    u = MagicMock(spec=User)
    u.id = user_id
    u.email = f"user{user_id}@example.com"
    u.username = f"user{user_id}"
    u.fullname = "Some User"
    u.preferred_language = "en"
    u.profile_picture_url = None
    u.role = role
    u.plan = UserPlan.free
    u.is_active = True
    u.is_email_verified = True
    u.plan_expires_at = None
    u.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    u.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return u


def make_mock_niche_orm(niche_id: int = 1) -> MagicMock:
    n = MagicMock(spec=Niche)
    n.id = niche_id
    n.title = f"Niche {niche_id}"
    n.tagline = "A tagline"
    n.prompt = "Write like this"
    n.thumbnail_url = None
    n.script_structure = {}
    n.tone = ["informative"]
    n.pacing = ["fast"]
    n.top_channels = None
    n.best_for = None
    n.status = NicheStatus.active
    n.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    n.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return n


# ── Auth guards — all admin endpoints require admin role ──────────────────────


async def test_stats_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/admin/stats")
    assert resp.status_code == 401


async def test_stats_requires_admin(client: AsyncClient):
    """Regular user (non-admin) should get 403."""
    resp = await client.get("/api/v1/admin/stats")
    assert resp.status_code == 403


async def test_user_stats_requires_admin(client: AsyncClient):
    resp = await client.get("/api/v1/admin/user-stats")
    assert resp.status_code == 403


async def test_list_users_requires_admin(client: AsyncClient):
    resp = await client.get("/api/v1/admin/users")
    assert resp.status_code == 403


async def test_get_user_requires_admin(client: AsyncClient):
    resp = await client.get("/api/v1/admin/users/1")
    assert resp.status_code == 403


async def test_admin_niches_requires_admin(client: AsyncClient):
    resp = await client.get("/api/v1/admin/niches")
    assert resp.status_code == 403


# ── GET /api/v1/admin/stats ───────────────────────────────────────────────────


async def test_stats_success(admin_client: AsyncClient, mock_db: AsyncMock):
    # Each scalar_one call returns 0 by default (set in conftest mock_db)
    resp = await admin_client.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "total_users" in data
    assert "new_users_this_week" in data
    assert "feature_usage" in data
    fu = data["feature_usage"]
    assert "script_generator" in fu
    assert "title_generator" in fu
    assert "niche_vault" in fu


# ── GET /api/v1/admin/user-stats ──────────────────────────────────────────────


async def test_user_stats_success(admin_client: AsyncClient, mock_db: AsyncMock):
    resp = await admin_client.get("/api/v1/admin/user-stats")
    assert resp.status_code == 200
    data = resp.json()["data"]
    for field in (
        "total_users", "active_users", "inactive_users",
        "verified_users", "admin_count", "user_count",
        "new_this_week", "pro_users", "free_users",
    ):
        assert field in data, f"Missing field: {field}"


# ── GET /api/v1/admin/users ───────────────────────────────────────────────────


async def test_list_users_success(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/users")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "meta" in body


async def test_list_users_with_search(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/users?search=alice")
    assert resp.status_code == 200


async def test_list_users_invalid_role_filter(admin_client: AsyncClient):
    resp = await admin_client.get("/api/v1/admin/users?role=superpower")
    assert resp.status_code == 400


async def test_list_users_invalid_plan_filter(admin_client: AsyncClient):
    resp = await admin_client.get("/api/v1/admin/users?plan=diamond")
    assert resp.status_code == 400


# ── GET /api/v1/admin/users/{id} ──────────────────────────────────────────────


async def test_get_user_not_found(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await admin_client.get("/api/v1/admin/users/9999")
    assert resp.status_code == 404


async def test_get_user_success(admin_client: AsyncClient, mock_db: AsyncMock):
    user = make_mock_user_orm(user_id=5)
    mock_db.execute.return_value.scalar_one_or_none.return_value = user

    resp = await admin_client.get("/api/v1/admin/users/5")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == 5
    assert data["email"] == "user5@example.com"


# ── POST /api/v1/admin/users/{id}/activate ───────────────────────────────────


async def test_activate_own_account_rejected(admin_client: AsyncClient, mock_db: AsyncMock, admin_user: MagicMock):
    """Admin cannot activate/deactivate their own account."""
    resp = await admin_client.post(f"/api/v1/admin/users/{admin_user.id}/activate")
    assert resp.status_code == 400


async def test_deactivate_own_account_rejected(admin_client: AsyncClient, mock_db: AsyncMock, admin_user: MagicMock):
    resp = await admin_client.post(f"/api/v1/admin/users/{admin_user.id}/deactivate")
    assert resp.status_code == 400


# ── PATCH /api/v1/admin/users/{id}/role ──────────────────────────────────────


async def test_change_own_role_rejected(admin_client: AsyncClient, admin_user: MagicMock):
    resp = await admin_client.patch(
        f"/api/v1/admin/users/{admin_user.id}/role",
        json={"role": "user"},
    )
    assert resp.status_code == 400


async def test_change_role_invalid_value(admin_client: AsyncClient):
    resp = await admin_client.patch(
        "/api/v1/admin/users/99/role",
        json={"role": "god"},
    )
    assert resp.status_code == 422


# ── GET /api/v1/admin/niches ──────────────────────────────────────────────────


async def test_admin_list_niches_success(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/niches")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_admin_list_niches_returns_items(admin_client: AsyncClient, mock_db: AsyncMock):
    niches = [make_mock_niche_orm(1), make_mock_niche_orm(2)]
    mock_db.execute.return_value.scalar_one.return_value = 2
    mock_db.execute.return_value.scalars.return_value.all.return_value = niches

    resp = await admin_client.get("/api/v1/admin/niches")
    assert resp.status_code == 200
    assert resp.json()["meta"]["total"] == 2


async def test_admin_list_niches_invalid_status(admin_client: AsyncClient):
    resp = await admin_client.get("/api/v1/admin/niches?status=deleted")
    assert resp.status_code == 400


# ── POST /api/v1/admin/niches ─────────────────────────────────────────────────


async def test_admin_create_niche_missing_required(admin_client: AsyncClient):
    resp = await admin_client.post("/api/v1/admin/niches", json={"title": "Tech"})
    assert resp.status_code == 422


async def test_admin_create_niche_invalid_status(admin_client: AsyncClient):
    resp = await admin_client.post(
        "/api/v1/admin/niches",
        json={"title": "Tech", "prompt": "Write tech content", "status": "deleted"},
    )
    assert resp.status_code == 422


# ── GET /api/v1/admin/niches/{id} ────────────────────────────────────────────


async def test_admin_get_niche_not_found(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await admin_client.get("/api/v1/admin/niches/999")
    assert resp.status_code == 404


# ── DELETE /api/v1/admin/niches/{id} ─────────────────────────────────────────


async def test_admin_delete_niche_not_found(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await admin_client.delete("/api/v1/admin/niches/999")
    assert resp.status_code == 404


# ── Reports ───────────────────────────────────────────────────────────────────


async def test_user_report_requires_admin(client: AsyncClient):
    resp = await client.get("/api/v1/admin/reports/users")
    assert resp.status_code == 403


async def test_user_report_success(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/reports/users")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_user_report_invalid_date(admin_client: AsyncClient, mock_db: AsyncMock):
    resp = await admin_client.get("/api/v1/admin/reports/users?start_date=not-a-date")
    assert resp.status_code == 400


async def test_conversion_funnel_success(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/reports/conversion-funnel")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_csv_export_content_type(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/reports/users/export")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]


async def test_funnel_csv_export_content_type(admin_client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await admin_client.get("/api/v1/admin/reports/conversion-funnel/export")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
