"""Create my_medicines table for personal medicine cabinet

Revision ID: c1d2e3f4a5b6
Revises: a3f7e2b1c905
Create Date: 2026-05-19 12:00:00.000000

Creates:
- my_medicines: User's personal medicine cabinet with AI scan metadata
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "a3f7e2b1c905"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "my_medicines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dosage", sa.String(50), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("warnings_json", sa.Text(), nullable=True),
        sa.Column("guidance", sa.Text(), nullable=True),
        sa.Column("schedule", sa.Text(), nullable=True),
        sa.Column("remaining_pills", sa.Integer(), nullable=True),
        sa.Column("doctor_notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_my_medicines_user_id", "my_medicines", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_my_medicines_user_id", table_name="my_medicines")
    op.drop_table("my_medicines")
