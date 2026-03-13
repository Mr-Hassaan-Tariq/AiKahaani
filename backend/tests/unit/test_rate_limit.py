"""
Unit tests for app/core/rate_limit.py

Tests the key function used for rate limiting:
  - authenticated requests → "user:<id>"
  - unauthenticated / bad token → client IP
"""

from unittest.mock import MagicMock

import pytest

from app.config import settings
from app.core.rate_limit import _key_by_user_or_ip
from app.core.security import create_access_token


def _make_request(auth_header: str | None = None, client_host: str = "1.2.3.4") -> MagicMock:
    """Build a minimal mock Starlette Request."""
    request = MagicMock()
    request.client.host = client_host
    headers = {}
    if auth_header is not None:
        headers["authorization"] = auth_header
    request.headers.get = lambda key, default=None: headers.get(key, default)
    return request


def test_valid_jwt_returns_user_key():
    token = create_access_token(user_id=99)
    request = _make_request(auth_header=f"Bearer {token}")
    key = _key_by_user_or_ip(request)
    assert key == "user:99"


def test_invalid_jwt_falls_back_to_ip():
    request = _make_request(auth_header="Bearer not.a.real.token", client_host="5.6.7.8")
    key = _key_by_user_or_ip(request)
    assert key == "5.6.7.8"


def test_no_auth_header_falls_back_to_ip():
    request = _make_request(auth_header=None, client_host="9.9.9.9")
    key = _key_by_user_or_ip(request)
    assert key == "9.9.9.9"


def test_malformed_bearer_falls_back_to_ip():
    request = _make_request(auth_header="Token xyz", client_host="10.0.0.1")
    key = _key_by_user_or_ip(request)
    assert key == "10.0.0.1"


def test_refresh_token_still_extracts_user_id():
    """Refresh tokens also have a 'sub' claim — key function should work."""
    from app.core.security import create_refresh_token
    token = create_refresh_token(user_id=42)
    request = _make_request(auth_header=f"Bearer {token}")
    key = _key_by_user_or_ip(request)
    assert key == "user:42"
