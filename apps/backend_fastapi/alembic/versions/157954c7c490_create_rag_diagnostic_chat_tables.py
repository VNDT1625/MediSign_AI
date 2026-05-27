"""Create RAG diagnostic chat tables

Revision ID: 157954c7c490
Revises:
Create Date: 2025-01-01 00:00:00.000000

Creates the following tables:
- chat_conversations: Multi-turn diagnostic chat conversations
- chat_messages: Individual messages within conversations
- kb_embeddings: Knowledge base embedding index for hybrid RAG retrieval (pgvector)
- disease_symptom_edges: Disease-symptom graph edges for differential questioning

Requirements: 15.1, 15.2, 15.3, 18.1, 18.2
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "157954c7c490"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all four RAG diagnostic chat tables and indexes."""

    # 1. chat_conversations
    op.create_table(
        "chat_conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("adapter", sa.String(20), nullable=False, server_default="medical"),
        sa.Column("phase", sa.String(20), nullable=False, server_default="initial"),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # 2. chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), nullable=False, index=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite"),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )

    # Composite index for efficient history paging by conversation + time
    op.create_index(
        "ix_chat_messages_conv_created",
        "chat_messages",
        ["conversation_id", "created_at"],
    )

    # 3. kb_embeddings (pgvector)
    # Enable pgvector extension if not already enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "kb_embeddings",
        sa.Column("record_id", sa.String(255), primary_key=True),
        sa.Column("embedding", sa.Text(), nullable=False),  # pgvector Vector(384) handled at app level
        sa.Column("kind", sa.String(20), nullable=False),
        sa.CheckConstraint(
            "kind IN ('disease', 'symptom', 'evidence')",
            name="ck_kb_embeddings_kind",
        ),
    )

    # Replace the Text column with actual vector type if pgvector is available
    op.execute(
        "ALTER TABLE kb_embeddings ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384)"
    )

    # 4. disease_symptom_edges
    op.create_table(
        "disease_symptom_edges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("disease_id", sa.String(255), nullable=False, index=True),
        sa.Column("symptom", sa.String(255), nullable=False, index=True),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("is_discriminative", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.CheckConstraint(
            "weight >= 0.0 AND weight <= 1.0",
            name="ck_disease_symptom_edges_weight",
        ),
    )


def downgrade() -> None:
    """Drop all four RAG diagnostic chat tables in reverse order."""

    # Drop in reverse order of creation
    op.drop_table("disease_symptom_edges")
    op.drop_table("kb_embeddings")
    op.drop_index("ix_chat_messages_conv_created", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_table("chat_conversations")
