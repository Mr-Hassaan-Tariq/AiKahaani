"""
Application configuration via pydantic-settings.

All settings are sourced from environment variables (with .env file fallback).
Every setting is type-checked at startup — a missing required value raises an
error immediately rather than at the moment it is first used.
"""

from functools import lru_cache
from typing import Optional

from pydantic import computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.backend"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Core ──────────────────────────────────────────────────────────────────
    secret_key: str
    debug: bool = False
    environment: str = "production"
    frontend_url: str = "http://localhost:3000"

    # ── Database ──────────────────────────────────────────────────────────────
    # Preferred: full DATABASE_URL (Railway provides this automatically)
    database_url: Optional[str] = None

    # Fallback: individual vars
    database_user: str = "postgres"
    database_password: str = ""
    database_name: str = "video_scripts"
    database_host: str = "localhost"
    database_port: int = 5432

    @computed_field
    @property
    def async_database_url(self) -> str:
        """SQLAlchemy-compatible async database URL (postgresql+asyncpg://)."""
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    # ── JWT ───────────────────────────────────────────────────────────────────
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # ── Google OAuth2 ─────────────────────────────────────────────────────────
    google_oauth2_client_id: str = ""
    google_oauth2_client_secret: str = ""
    google_oauth2_redirect_uri: str = "http://localhost:3000/"

    # ── OpenAI ────────────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1"
    title_generation_api_key: str = ""
    title_generation_model: str = "gpt-4.1"

    @model_validator(mode="after")
    def set_title_generation_api_key_fallback(self) -> "Settings":
        """Fall back to the main OpenAI key if no separate title key is provided."""
        if not self.title_generation_api_key and self.openai_api_key:
            self.title_generation_api_key = self.openai_api_key
        return self

    # ── YouTube Transcript Proxy ───────────────────────────────────────────────
    transcript_proxy_username: str = ""
    transcript_proxy_password: str = ""

    # ── Brevo Email ───────────────────────────────────────────────────────────
    brevo_api_key: str = ""
    default_from_email: str = "noreply@videoscripts.com"

    # ── AWS S3 ────────────────────────────────────────────────────────────────
    use_s3_for_storage: bool = False
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_storage_bucket_name: str = ""
    aws_s3_region_name: str = "us-east-1"
    aws_presigned_url_expiration: int = 3600

    @computed_field
    @property
    def use_s3_storage(self) -> bool:
        """True only when the flag is enabled AND all credentials are present."""
        return self.use_s3_for_storage and all([
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_storage_bucket_name,
        ])

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Additional origins from env (comma-separated string)
    cors_extra_origins: str = ""

    @computed_field
    @property
    def cors_allowed_origins(self) -> list[str]:
        base = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "https://videoscripts.vercel.app",
            "https://videoscripts-frontend.vercel.app",
            "https://videoscripts.com",
            "https://www.videoscripts.com",
            "https://stage-app.videoscripts.com",
            "https://stage-admin.videoscripts.com",
            "https://app.videoscripts.com",
            "https://admin.videoscripts.com",
            "https://charmed-simple-asp.ngrok-free.app",
        ]
        if self.cors_extra_origins:
            extra = [o.strip() for o in self.cors_extra_origins.split(",") if o.strip()]
            base.extend(extra)
        return base

    # ── Subscription / Trial (reserved for future payment integration) ─────────
    trial_outline_limit: int = 10


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance. Import this rather than Settings() directly."""
    return Settings()


# Module-level singleton for convenient import
settings = get_settings()
