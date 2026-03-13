"""initial_schema

Revision ID: 79d6f1aeb433
Revises:
Create Date: 2026-03-13

Full initial schema for Video Scripts backend_v2.
Tables created in FK-dependency order.

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "79d6f1aeb433"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── PostgreSQL enum helpers ───────────────────────────────────────────────────

_user_role = postgresql.ENUM("user", "admin", "super_admin", name="user_role")
_user_plan = postgresql.ENUM("free", "pro", name="user_plan")
_auth_token_type = postgresql.ENUM("magic_link", "email_verification", name="auth_token_type")
_tone_scope = postgresql.ENUM("script", "title", "both", name="tone_scope")
_outline_status = postgresql.ENUM("draft", "generated", "saved", name="outline_status")
_script_status = postgresql.ENUM("draft", "generated", "saved", name="script_status")
_title_generation_type = postgresql.ENUM(
    "from_script", "from_idea", "optimized", name="title_generation_type"
)
_openai_run_type = postgresql.ENUM(
    "outline_generation",
    "script_generation",
    "title_generation",
    "image_analysis",
    name="openai_run_type",
)
_openai_run_status = postgresql.ENUM(
    "completed", "failed", "cancelled", name="openai_run_status"
)
_niche_status = postgresql.ENUM("active", "inactive", name="niche_status")
_notification_type = postgresql.ENUM(
    "script",
    "account",
    "feature",
    "tips",
    "community",
    "subscription",
    "drafts",
    "title",
    name="notification_type",
)


def upgrade() -> None:
    # ── Create ENUM types ─────────────────────────────────────────────────────
    _user_role.create(op.get_bind(), checkfirst=True)
    _user_plan.create(op.get_bind(), checkfirst=True)
    _auth_token_type.create(op.get_bind(), checkfirst=True)
    _tone_scope.create(op.get_bind(), checkfirst=True)
    _outline_status.create(op.get_bind(), checkfirst=True)
    _script_status.create(op.get_bind(), checkfirst=True)
    _title_generation_type.create(op.get_bind(), checkfirst=True)
    _openai_run_type.create(op.get_bind(), checkfirst=True)
    _openai_run_status.create(op.get_bind(), checkfirst=True)
    _niche_status.create(op.get_bind(), checkfirst=True)
    _notification_type.create(op.get_bind(), checkfirst=True)

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(150), nullable=False),
        sa.Column("fullname", sa.String(255), nullable=False, server_default=""),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("preferred_language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("profile_picture_url", sa.Text(), nullable=True),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "role",
            postgresql.ENUM("user", "admin", "super_admin", name="user_role", create_type=False),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "plan",
            postgresql.ENUM("free", "pro", name="user_plan", create_type=False),
            nullable=False,
            server_default="free",
        ),
        sa.Column("plan_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tolt_customer_id", sa.String(40), nullable=True),
        sa.Column("tolt_partner_id", sa.String(40), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])
    op.create_index("ix_users_tolt_customer_id", "users", ["tolt_customer_id"])
    op.create_index("ix_users_tolt_partner_id", "users", ["tolt_partner_id"])

    # ── user_settings ─────────────────────────────────────────────────────────
    op.create_table(
        "user_settings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "notification_preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "privacy_preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    # ── user_refresh_tokens ───────────────────────────────────────────────────
    op.create_table(
        "user_refresh_tokens",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_user_refresh_tokens_user_id", "user_refresh_tokens", ["user_id"])
    op.create_index("ix_user_refresh_tokens_expires_at", "user_refresh_tokens", ["expires_at"])

    # ── user_auth_tokens ──────────────────────────────────────────────────────
    op.create_table(
        "user_auth_tokens",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "token_type",
            postgresql.ENUM(
                "magic_link", "email_verification", name="auth_token_type", create_type=False
            ),
            nullable=False,
        ),
        sa.Column(
            "token",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),
        ),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        "ix_user_auth_tokens_user_id_token_type",
        "user_auth_tokens",
        ["user_id", "token_type"],
    )
    op.create_index("ix_user_auth_tokens_expires_at", "user_auth_tokens", ["expires_at"])

    # ── niches ────────────────────────────────────────────────────────────────
    op.create_table(
        "niches",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("tagline", sa.String(500), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column(
            "script_structure",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "tone",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "pacing",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("top_channels", sa.Text(), nullable=True),
        sa.Column("best_for", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM("active", "inactive", name="niche_status", create_type=False),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )
    op.create_index("ix_niches_status", "niches", ["status"])

    # ── niche_tones ───────────────────────────────────────────────────────────
    op.create_table(
        "niche_tones",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("niche_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["niche_id"], ["niches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_niche_tones_niche_id", "niche_tones", ["niche_id"])

    # ── niche_pacings ─────────────────────────────────────────────────────────
    op.create_table(
        "niche_pacings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("niche_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["niche_id"], ["niches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_niche_pacings_niche_id", "niche_pacings", ["niche_id"])

    # ── tones ─────────────────────────────────────────────────────────────────
    op.create_table(
        "tones",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "scope",
            postgresql.ENUM("script", "title", "both", name="tone_scope", create_type=False),
            nullable=False,
            server_default="both",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "scope", name="uq_tones_name_scope"),
    )
    op.create_index("ix_tones_scope", "tones", ["scope"])

    # ── template_styles ───────────────────────────────────────────────────────
    op.create_table(
        "template_styles",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("min_length", sa.Integer(), nullable=False),
        sa.Column("max_length", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("outline_sections", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ── script_outlines ───────────────────────────────────────────────────────
    op.create_table(
        "script_outlines",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("niche_id", sa.BigInteger(), nullable=True),
        sa.Column("template_style_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(300), nullable=False, server_default=""),
        sa.Column(
            "outline_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("outline_text", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "section_order",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft", "generated", "saved", name="outline_status", create_type=False
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("original_outline", sa.Text(), nullable=False, server_default=""),
        sa.Column("openai_model", sa.String(100), nullable=False, server_default=""),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generation_time", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("version >= 1", name="ck_script_outlines_version"),
        sa.ForeignKeyConstraint(["niche_id"], ["niches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_style_id"], ["template_styles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_script_outlines_user_id", "script_outlines", ["user_id"])
    op.create_index("ix_script_outlines_niche_id", "script_outlines", ["niche_id"])
    op.create_index(
        "ix_script_outlines_template_style_id", "script_outlines", ["template_style_id"]
    )
    op.create_index("ix_script_outlines_status", "script_outlines", ["status"])
    op.create_index(
        "ix_script_outlines_user_id_created_at", "script_outlines", ["user_id", "created_at"]
    )

    # ── outline_tones (M2M) ───────────────────────────────────────────────────
    op.create_table(
        "outline_tones",
        sa.Column("outline_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tone_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["outline_id"], ["script_outlines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tone_id"], ["tones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("outline_id", "tone_id"),
    )
    op.create_index("ix_outline_tones_tone_id", "outline_tones", ["tone_id"])

    # ── full_scripts ──────────────────────────────────────────────────────────
    op.create_table(
        "full_scripts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("outline_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "sections",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("word_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_duration", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft", "generated", "saved", name="script_status", create_type=False
            ),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("version", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("openai_model", sa.String(100), nullable=False, server_default=""),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generation_time", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("version >= 1", name="ck_full_scripts_version"),
        sa.CheckConstraint("word_count >= 0", name="ck_full_scripts_word_count"),
        sa.CheckConstraint("estimated_duration >= 0.0", name="ck_full_scripts_estimated_duration"),
        sa.ForeignKeyConstraint(["outline_id"], ["script_outlines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_full_scripts_user_id", "full_scripts", ["user_id"])
    op.create_index("ix_full_scripts_outline_id", "full_scripts", ["outline_id"])
    op.create_index("ix_full_scripts_status", "full_scripts", ["status"])
    op.create_index(
        "ix_full_scripts_user_id_created_at", "full_scripts", ["user_id", "created_at"]
    )

    # ── title_generations ─────────────────────────────────────────────────────
    op.create_table(
        "title_generations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("script_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "generation_type",
            postgresql.ENUM(
                "from_script",
                "from_idea",
                "optimized",
                name="title_generation_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("input_title", sa.Text(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column(
            "tones",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "titles",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("titles_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["script_id"], ["full_scripts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_title_generations_user_id", "title_generations", ["user_id"])
    op.create_index("ix_title_generations_script_id", "title_generations", ["script_id"])
    op.create_index(
        "ix_title_generations_generation_type", "title_generations", ["generation_type"]
    )
    op.create_index(
        "ix_title_generations_user_id_created_at", "title_generations", ["user_id", "created_at"]
    )

    # ── openai_run_logs ───────────────────────────────────────────────────────
    op.create_table(
        "openai_run_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "run_type",
            postgresql.ENUM(
                "outline_generation",
                "script_generation",
                "title_generation",
                "image_analysis",
                name="openai_run_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "completed", "failed", "cancelled", name="openai_run_status", create_type=False
            ),
            nullable=False,
            server_default="completed",
        ),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("word_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generation_time", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("thread_id", sa.String(255), nullable=True),
        sa.Column("run_id", sa.String(255), nullable=True),
        sa.Column("assistant_id", sa.String(255), nullable=True),
        sa.Column("file_search_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "file_search_snippets",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("script_outline_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("full_script_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title_generation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["full_script_id"], ["full_scripts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["script_outline_id"], ["script_outlines.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["title_generation_id"], ["title_generations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_openai_run_logs_user_id", "openai_run_logs", ["user_id"])
    op.create_index("ix_openai_run_logs_run_type", "openai_run_logs", ["run_type"])
    op.create_index("ix_openai_run_logs_status", "openai_run_logs", ["status"])
    op.create_index("ix_openai_run_logs_thread_id", "openai_run_logs", ["thread_id"])
    op.create_index("ix_openai_run_logs_run_id", "openai_run_logs", ["run_id"])
    op.create_index(
        "ix_openai_run_logs_user_id_created_at", "openai_run_logs", ["user_id", "created_at"]
    )

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "notification_type",
            postgresql.ENUM(
                "script",
                "account",
                "feature",
                "tips",
                "community",
                "subscription",
                "drafts",
                "title",
                name="notification_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "extra_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "ix_notifications_user_id_is_read", "notifications", ["user_id", "is_read"]
    )
    op.create_index(
        "ix_notifications_user_id_created_at", "notifications", ["user_id", "created_at"]
    )


def downgrade() -> None:
    # Drop in reverse FK-dependency order
    op.drop_table("notifications")
    op.drop_table("openai_run_logs")
    op.drop_table("title_generations")
    op.drop_table("full_scripts")
    op.drop_table("outline_tones")
    op.drop_table("script_outlines")
    op.drop_table("template_styles")
    op.drop_table("tones")
    op.drop_table("niche_pacings")
    op.drop_table("niche_tones")
    op.drop_table("niches")
    op.drop_table("user_auth_tokens")
    op.drop_table("user_refresh_tokens")
    op.drop_table("user_settings")
    op.drop_table("users")

    # Drop enum types in reverse order
    _notification_type.drop(op.get_bind(), checkfirst=True)
    _niche_status.drop(op.get_bind(), checkfirst=True)
    _openai_run_status.drop(op.get_bind(), checkfirst=True)
    _openai_run_type.drop(op.get_bind(), checkfirst=True)
    _title_generation_type.drop(op.get_bind(), checkfirst=True)
    _script_status.drop(op.get_bind(), checkfirst=True)
    _outline_status.drop(op.get_bind(), checkfirst=True)
    _tone_scope.drop(op.get_bind(), checkfirst=True)
    _auth_token_type.drop(op.get_bind(), checkfirst=True)
    _user_plan.drop(op.get_bind(), checkfirst=True)
    _user_role.drop(op.get_bind(), checkfirst=True)
