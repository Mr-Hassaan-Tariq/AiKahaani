"""
Unit tests for app/core/security.py

Pure functions — no I/O, no database, no HTTP.
"""

import pytest
from jose import JWTError, jwt

# env is set in conftest before this import
from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


# ── Password hashing ──────────────────────────────────────────────────────────


def test_hash_password_is_not_plaintext():
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert len(hashed) > 20


def test_verify_password_correct():
    hashed = hash_password("correcthorse")
    assert verify_password("correcthorse", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("correcthorse")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_empty_wrong():
    hashed = hash_password("secret")
    assert verify_password("", hashed) is False


# ── JWT — access token ────────────────────────────────────────────────────────


def test_create_access_token_contains_sub():
    token = create_access_token(user_id=42)
    payload = decode_token(token)
    assert payload["sub"] == "42"


def test_create_access_token_type_is_access():
    token = create_access_token(user_id=1)
    payload = decode_token(token)
    assert payload["type"] == "access"


def test_create_access_token_has_exp():
    token = create_access_token(user_id=1)
    payload = decode_token(token)
    assert "exp" in payload


# ── JWT — refresh token ───────────────────────────────────────────────────────


def test_create_refresh_token_type_is_refresh():
    token = create_refresh_token(user_id=7)
    payload = decode_token(token)
    assert payload["type"] == "refresh"


def test_create_refresh_token_has_jti():
    token = create_refresh_token(user_id=7)
    payload = decode_token(token)
    assert "jti" in payload
    assert len(payload["jti"]) == 32  # secrets.token_hex(16) → 32 hex chars


def test_two_refresh_tokens_have_different_jti():
    t1 = create_refresh_token(user_id=1)
    t2 = create_refresh_token(user_id=1)
    p1 = decode_token(t1)
    p2 = decode_token(t2)
    assert p1["jti"] != p2["jti"]


# ── JWT — decode ──────────────────────────────────────────────────────────────


def test_decode_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_token("not.a.real.token")


def test_decode_tampered_token_raises():
    token = create_access_token(user_id=1)
    tampered = token[:-4] + "XXXX"
    with pytest.raises(JWTError):
        decode_token(tampered)


# ── Refresh token hashing ─────────────────────────────────────────────────────


def test_hash_refresh_token_is_deterministic():
    raw = "some_refresh_token_string"
    assert hash_refresh_token(raw) == hash_refresh_token(raw)


def test_hash_refresh_token_different_inputs_differ():
    assert hash_refresh_token("token_a") != hash_refresh_token("token_b")


def test_hash_refresh_token_length():
    # SHA-256 → 64 hex characters
    result = hash_refresh_token("any_token")
    assert len(result) == 64
