"""Add kb_pending_records, diagnosis_feedback, weight_update_proposals tables

Revision ID: a3f7e2b1c905
Revises: 157954c7c490
Create Date: 2026-05-19 00:00:00.000000

Changes:
- kb_pending_records: staging table for KBLazyLoader-generated records (quarantine)
- diagnosis_feedback: user feedback on AI diagnosis conclusions (feedback loop)
- weight_update_proposals: proposed disease_symptom_edges weight updates from feedback
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3f7e2b1c905"
down_revision: Union[str, None] = "157954c7c490"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. kb_pending_records
    op.create_table(
        "kb_pending_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_query", sa.Text(), nullable=False),
        sa.Column("disease_name", sa.String(255), nullable=False, index=True),
        sa.Column("symptoms", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("red_flags", sa.Text(), nullable=True),
        sa.Column("home_care", sa.Text(), nullable=True),
        sa.Column("lab_tests", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_kb_pending_records_status",
        ),
    )
    op.create_index("ix_kb_pending_records_status", "kb_pending_records", ["status"])
    op.create_index("ix_kb_pending_records_created_at", "kb_pending_records", ["created_at"])

    # 2. diagnosis_feedback
    op.create_table(
        "diagnosis_feedback",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("conversation_id", sa.String(36), nullable=False, index=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("ai_predicted_disease", sa.String(255), nullable=False),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("actual_disease", sa.String(255), nullable=True),
        sa.Column("symptoms_at_time", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_diagnosis_feedback_created_at", "diagnosis_feedback", ["created_at"])

    # 3. weight_update_proposals
    op.create_table(
        "weight_update_proposals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("disease_id", sa.String(255), nullable=False, index=True),
        sa.Column("symptom", sa.String(255), nullable=False, index=True),
        sa.Column("current_weight", sa.Float(), nullable=False),
        sa.Column("proposed_weight", sa.Float(), nullable=False),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("feedback_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("incorrect_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(36), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_weight_update_proposals_status",
        ),
        sa.CheckConstraint(
            "direction IN ('increase', 'decrease')",
            name="ck_weight_update_proposals_direction",
        ),
    )
    op.create_index(
        "ix_weight_update_proposals_status", "weight_update_proposals", ["status"]
    )


def downgrade() -> None:
    op.drop_table("weight_update_proposals")
    op.drop_table("diagnosis_feedback")
    op.drop_table("kb_pending_records")
