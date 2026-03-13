"""
Pydantic schemas for the authentication domain.

Request and response models for all auth endpoints.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ── Shared sub-schemas ────────────────────────────────────────────────────────


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    fullname: str
    preferred_language: str
    profile_picture_url: Optional[str] = None
    is_email_verified: bool
    role: str
    plan: str

    model_config = {"from_attributes": True}


class UserBasicOut(BaseModel):
    """Minimal user object returned inside auth token responses."""

    id: int
    email: str
    username: str
    fullname: str

    model_config = {"from_attributes": True}


# ── Signup ────────────────────────────────────────────────────────────────────


class SignupRequest(BaseModel):
    email: EmailStr
    username: str
    fullname: str = ""
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    def model_post_init(self, __context) -> None:
        if self.password != self.password_confirm:
            raise ValueError("Passwords don't match")


class SignupResponse(BaseModel):
    user: UserOut


# ── Google OAuth ──────────────────────────────────────────────────────────────


class GoogleAuthRequest(BaseModel):
    id_token: str


class AuthTokensOut(BaseModel):
    """Access + refresh tokens with basic user info."""

    access: str
    refresh: str
    user: UserBasicOut
    created: bool = False


# ── Magic link ────────────────────────────────────────────────────────────────


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerifyRequest(BaseModel):
    token: str

    @field_validator("token")
    @classmethod
    def token_is_uuid(cls, v: str) -> str:
        import uuid
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid token format")
        return v


class MagicLinkVerifyOut(BaseModel):
    access: str
    refresh: str
    user: UserBasicOut


# ── Admin login ───────────────────────────────────────────────────────────────


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginOut(BaseModel):
    access_token: str
    refresh_token: str
    user: UserOut
    message: str


# ── Token refresh ─────────────────────────────────────────────────────────────


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenOut(BaseModel):
    access_token: str
    refresh_token: str
    message: str


# ── Logout ────────────────────────────────────────────────────────────────────


class LogoutRequest(BaseModel):
    refresh_token: str
