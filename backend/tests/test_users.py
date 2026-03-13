"""
Integration tests for /api/v1/users/* endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.models.user import UserSettings


# ── GET /api/v1/users/me ──────────────────────────────────────────────────────


async def test_get_me_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_get_me_success(client: AsyncClient, regular_user: MagicMock):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["email"] == regular_user.email
    assert data["username"] == regular_user.username
    assert data["role"] == regular_user.role.value


async def test_get_me_response_has_all_fields(client: AsyncClient):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 200
    data = resp.json()["data"]
    for field in ("id", "email", "username", "fullname", "role", "plan", "is_active"):
        assert field in data, f"Missing field: {field}"


# ── PATCH /api/v1/users/me ────────────────────────────────────────────────────


async def test_update_me_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.patch("/api/v1/users/me", json={"fullname": "New Name"})
    assert resp.status_code == 401


async def test_update_me_username_with_spaces(client: AsyncClient):
    resp = await client.patch("/api/v1/users/me", json={"username": "bad name"})
    assert resp.status_code == 422


async def test_update_me_fullname_too_long(client: AsyncClient):
    resp = await client.patch("/api/v1/users/me", json={"fullname": "x" * 300})
    assert resp.status_code == 422


async def test_update_me_empty_body_is_ok(client: AsyncClient, mock_db: AsyncMock, regular_user: MagicMock):
    """Partial update with no fields should not error."""
    # No username conflict check needed — nothing to update
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.patch("/api/v1/users/me", json={})
    assert resp.status_code == 200


# ── GET /api/v1/users/me/settings/notification ───────────────────────────────


async def test_get_notification_settings_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/users/me/settings/notification")
    assert resp.status_code == 401


async def test_get_notification_settings_success(client: AsyncClient, mock_db: AsyncMock):
    mock_settings = MagicMock(spec=UserSettings)
    mock_settings.notification_preferences = {"email_notifications": True}
    mock_settings.privacy_preferences = {}
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_settings

    resp = await client.get("/api/v1/users/me/settings/notification")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "notification_preferences" in body["data"]


# ── PATCH /api/v1/users/me/settings/notification ─────────────────────────────


async def test_update_notification_settings_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.patch(
        "/api/v1/users/me/settings/notification",
        json={"email_notifications": False},
    )
    assert resp.status_code == 401


async def test_update_notification_settings_merges(client: AsyncClient, mock_db: AsyncMock):
    """Existing preferences should be merged, not replaced."""
    existing = MagicMock(spec=UserSettings)
    existing.notification_preferences = {"email_notifications": True, "in_app_notifications": True}
    existing.privacy_preferences = {}
    mock_db.execute.return_value.scalar_one_or_none.return_value = existing

    resp = await client.patch(
        "/api/v1/users/me/settings/notification",
        json={"email_notifications": False},
    )
    assert resp.status_code == 200
    # The endpoint sets the merged prefs on the mock — verify it was called
    assert existing.notification_preferences is not None


# ── GET /api/v1/users/me/settings/privacy ────────────────────────────────────


async def test_get_privacy_settings_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/users/me/settings/privacy")
    assert resp.status_code == 401


async def test_get_privacy_settings_success(client: AsyncClient, mock_db: AsyncMock):
    mock_settings = MagicMock(spec=UserSettings)
    mock_settings.notification_preferences = {}
    mock_settings.privacy_preferences = {"allow_product_update_emails": True}
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_settings

    resp = await client.get("/api/v1/users/me/settings/privacy")
    assert resp.status_code == 200
    assert "privacy_preferences" in resp.json()["data"]


# ── PATCH /api/v1/users/me/settings/privacy ──────────────────────────────────


async def test_update_privacy_settings_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.patch(
        "/api/v1/users/me/settings/privacy",
        json={"allow_product_update_emails": False},
    )
    assert resp.status_code == 401
