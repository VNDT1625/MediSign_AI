"""Baseline migration for tables that previously relied on Base.metadata.create_all

Revision ID: b7e8d9f1a234
Revises: c1d2e3f4a5b6
Create Date: 2026-05-19 14:00:00.000000

Adds Alembic tracking for the rest of the schema so production deployments no
longer need ``Base.metadata.create_all`` at startup. Each table is created
idempotently (checked via the inspector) so this revision is safe to apply on
existing databases that already have the tables.

Tables introduced here:
    - users, user_sessions, password_resets, email_verifications
    - medicine_registry, hospitals
    - family_connections, triage_history
    - community_posts, post_comments, post_likes
    - workout_sessions, fitness_goals
    - daily_journals, user_profiles
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "b7e8d9f1a234"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    return inspect(bind).has_table(name)


def _create_if_missing(name: str, *columns, **kwargs) -> None:
    if _table_exists(name):
        return
    op.create_table(name, *columns, **kwargs)


def upgrade() -> None:
    # ─── Users / auth ────────────────────────────────────────────────────────
    _create_if_missing(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("phone", sa.String(20), nullable=True, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_phone_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("account_type", sa.String(20), nullable=False, server_default="user"),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "user_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("device_id", sa.String(255), nullable=True),
        sa.Column("device_name", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "password_resets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "email_verifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ─── Public health data ──────────────────────────────────────────────────
    _create_if_missing(
        "medicine_registry",
        sa.Column("reg_number", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False, index=True),
        sa.Column("active_ingredient", sa.Text(), nullable=True),
        sa.Column("dosage_form", sa.String(100), nullable=True),
        sa.Column("strength", sa.String(100), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("contraindications", sa.Text(), nullable=True),
        sa.Column("side_effects", sa.Text(), nullable=True),
        sa.Column("interactions", sa.Text(), nullable=True),
        sa.Column("warnings", sa.Text(), nullable=True),
        sa.Column("usage", sa.Text(), nullable=True),
        sa.Column("storage", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "hospitals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(500), nullable=False, index=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("district", sa.String(100), nullable=True, index=True),
        sa.Column("city", sa.String(100), nullable=True, index=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("latitude", sa.String(50), nullable=True),
        sa.Column("longitude", sa.String(50), nullable=True),
        sa.Column("specialties", sa.Text(), nullable=True),
        sa.Column("accepts_bhyt", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_24h", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("has_emergency", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("hospital_type", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ─── Care connect / triage ───────────────────────────────────────────────
    _create_if_missing(
        "family_connections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.String(36), nullable=False, index=True),
        sa.Column("relative_id", sa.String(36), nullable=False, index=True),
        sa.Column("relationship", sa.String(50), nullable=True),
        sa.Column("permissions", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("initiated_by", sa.String(36), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "triage_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(36), nullable=False, index=True),
        sa.Column("age_range", sa.String(10), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column("duration", sa.String(50), nullable=True),
        sa.Column("triage_level", sa.String(10), nullable=True),
        sa.Column("advice", sa.Text(), nullable=True),
        sa.Column("recommended_specialty", sa.String(100), nullable=True),
        sa.Column("was_emergency", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )

    # ─── Community ───────────────────────────────────────────────────────────
    _create_if_missing(
        "community_posts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("author_id", sa.String(36), nullable=False, index=True),
        sa.Column("author_name", sa.String(100), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("moderation_note", sa.Text(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("comment_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("has_medical_disclaimer", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "post_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("post_id", sa.Integer(), nullable=False, index=True),
        sa.Column("author_id", sa.String(36), nullable=False, index=True),
        sa.Column("author_name", sa.String(100), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_anonymous", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "post_likes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("post_id", sa.Integer(), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ─── Fitness ─────────────────────────────────────────────────────────────
    _create_if_missing(
        "workout_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("exercise_id", sa.String(50), nullable=False),
        sa.Column("exercise_name", sa.String(100), nullable=False),
        sa.Column("target_area", sa.String(50), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("repetitions", sa.Integer(), nullable=True),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("calories_burned", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="completed"),
        sa.Column("difficulty_rating", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )

    _create_if_missing(
        "fitness_goals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("goal_type", sa.String(50), nullable=False),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("current_progress", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active", index=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # ─── Local-models tables (also created on the same SQLite/PG instance for
    #     environments that don't split storage) ──────────────────────────────
    _create_if_missing(
        "daily_journals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("tree_points", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    _create_if_missing(
        "user_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("yob", sa.Integer(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("disability_type", sa.String(20), nullable=True),
        sa.Column("preferred_communication", sa.String(50), nullable=True, server_default="text"),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(20), nullable=True),
        sa.Column("consent_personal_context", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # Drop in reverse dependency order. Safe-drop: tables may not exist when
    # the original schema came from create_all only.
    for name in [
        "user_profiles",
        "daily_journals",
        "fitness_goals",
        "workout_sessions",
        "post_likes",
        "post_comments",
        "community_posts",
        "triage_history",
        "family_connections",
        "hospitals",
        "medicine_registry",
        "email_verifications",
        "password_resets",
        "user_sessions",
        "users",
    ]:
        if _table_exists(name):
            op.drop_table(name)
