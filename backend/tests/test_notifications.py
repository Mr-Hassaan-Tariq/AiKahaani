"""
Integration tests for /api/v1/notifications/* endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.notification import Notification, NotificationType


def make_mock_notification(notif_id: int = 1, is_read: bool = False) -> MagicMock:
    n = MagicMock(spec=Notification)
    n.id = notif_id
    n.user_id = 1
    n.notification_type = NotificationType.script
    n.title = "Your script is ready"
    n.message = "Your latest script has been generated."
    n.is_read = is_read
    n.extra_data = {}
    n.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return n


# ── GET /api/v1/notifications ────────────────────────────────────────────────


async def test_list_notifications_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/notifications")
    assert resp.status_code == 401


async def test_list_notifications_empty(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["meta"]["total"] == 0


async def test_list_notifications_returns_items(client: AsyncClient, mock_db: AsyncMock):
    notifications = [make_mock_notification(1), make_mock_notification(2, is_read=True)]
    mock_db.execute.return_value.scalar_one.return_value = 2
    mock_db.execute.return_value.scalars.return_value.all.return_value = notifications

    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["total"] == 2
    assert len(body["data"]) == 2


async def test_list_notifications_invalid_type_filter(client: AsyncClient):
    resp = await client.get("/api/v1/notifications?notification_type=invalid_type")
    assert resp.status_code == 400


async def test_list_notifications_valid_type_filter(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/notifications?notification_type=script")
    assert resp.status_code == 200


async def test_list_notifications_is_read_filter(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/notifications?is_read=false")
    assert resp.status_code == 200


# ── POST /api/v1/notifications/{id}/read ─────────────────────────────────────


async def test_mark_read_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.post("/api/v1/notifications/1/read")
    assert resp.status_code == 401


async def test_mark_read_not_found(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.post("/api/v1/notifications/999/read")
    assert resp.status_code == 404


async def test_mark_read_success(client: AsyncClient, mock_db: AsyncMock):
    notif = make_mock_notification(1, is_read=False)
    mock_db.execute.return_value.scalar_one_or_none.return_value = notif

    resp = await client.post("/api/v1/notifications/1/read")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    # Verify is_read was set to True
    assert notif.is_read is True


# ── POST /api/v1/notifications/read-all ──────────────────────────────────────


async def test_mark_all_read_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.post("/api/v1/notifications/read-all")
    assert resp.status_code == 401


async def test_mark_all_read_success(client: AsyncClient, mock_db: AsyncMock):
    resp = await client.post("/api/v1/notifications/read-all")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "read" in body["message"].lower()
