"""
Integration tests for /api/auth/* endpoints.

These tests focus on:
  - Input validation (422 for bad payloads)
  - Auth guards (401 when token is missing)
  - Response shapes (success envelope keys)

We mock the auth service and DB so no real database is needed.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


# ── POST /api/auth/signup ─────────────────────────────────────────────────────


async def test_signup_missing_email(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={"username": "bob", "password": "secret12", "password_confirm": "secret12"},
    )
    assert resp.status_code == 422


async def test_signup_missing_password(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={"email": "bob@example.com", "username": "bob"},
    )
    assert resp.status_code == 422


async def test_signup_password_too_short(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "short",
            "password_confirm": "short",
        },
    )
    assert resp.status_code == 422


async def test_signup_passwords_do_not_match(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "password123",
            "password_confirm": "different456",
        },
    )
    assert resp.status_code in (400, 422)


async def test_signup_username_with_spaces(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={
            "email": "bob@example.com",
            "username": "bob smith",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert resp.status_code == 422


async def test_signup_invalid_email(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/signup",
        json={
            "email": "not-an-email",
            "username": "bob",
            "password": "password123",
            "password_confirm": "password123",
        },
    )
    assert resp.status_code == 422


# ── POST /api/auth/google ─────────────────────────────────────────────────────


async def test_google_missing_id_token(anon_client: AsyncClient):
    resp = await anon_client.post("/api/auth/google", json={})
    assert resp.status_code == 422


# ── POST /api/auth/magic-link ─────────────────────────────────────────────────


async def test_magic_link_missing_email(anon_client: AsyncClient):
    resp = await anon_client.post("/api/auth/magic-link", json={})
    assert resp.status_code == 422


async def test_magic_link_invalid_email(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/magic-link", json={"email": "not-an-email"}
    )
    assert resp.status_code == 422


# ── POST /api/auth/magic-link/verify ─────────────────────────────────────────


async def test_magic_link_verify_missing_token(anon_client: AsyncClient):
    resp = await anon_client.post("/api/auth/magic-link/verify", json={})
    assert resp.status_code == 422


async def test_magic_link_verify_non_uuid_token(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/auth/magic-link/verify", json={"token": "not-a-uuid"}
    )
    assert resp.status_code == 422


async def test_magic_link_verify_valid_uuid_format(anon_client: AsyncClient):
    """A properly formatted UUID should pass validation (may fail at service level)."""
    import uuid

    with patch(
        "app.api.auth.router.auth_service.verify_magic_link",
        side_effect=ValueError("Token expired"),
    ):
        resp = await anon_client.post(
            "/api/auth/magic-link/verify", json={"token": str(uuid.uuid4())}
        )
    # Either 400 (service error) or 200 — NOT 422 (validation passed)
    assert resp.status_code != 422


# ── POST /api/auth/refresh ────────────────────────────────────────────────────


async def test_refresh_missing_token(anon_client: AsyncClient):
    resp = await anon_client.post("/api/auth/refresh", json={})
    assert resp.status_code == 422


# ── POST /api/auth/logout ─────────────────────────────────────────────────────


async def test_logout_requires_auth(anon_client: AsyncClient):
    """Logout without a Bearer token should return 401."""
    resp = await anon_client.post(
        "/api/auth/logout", json={"refresh_token": "some_token"}
    )
    assert resp.status_code == 401


# ── Error response shape ──────────────────────────────────────────────────────


async def test_422_has_standard_error_envelope(anon_client: AsyncClient):
    resp = await anon_client.post("/api/auth/signup", json={})
    assert resp.status_code == 422
    body = resp.json()
    assert "success" in body
    assert body["success"] is False
    assert "message" in body
