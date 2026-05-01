"""Initial CoolAgent schema with RAG tables.

Revision ID: 20260430_0001
Revises:
Create Date: 2026-04-30
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260430_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "manufacturers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name", name="uq_manufacturers_name"),
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=500), nullable=True),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("manufacturer", sa.String(length=200), nullable=True),
        sa.Column("equipment_model", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("model_used", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_messages_conversation_id_conversations",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "error_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("manufacturer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("manufacturer", sa.String(length=200), nullable=False),
        sa.Column("model", sa.String(length=200), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("possible_causes", sa.JSON(), nullable=True),
        sa.Column("suggested_fix", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["manufacturer_id"],
            ["manufacturers.id"],
            name="fk_error_codes_manufacturer_id_manufacturers",
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("manufacturer", sa.String(length=200), nullable=True),
        sa.Column("equipment_model", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("chunk_metadata", sa.JSON(), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["knowledge_documents.id"],
            name="fk_knowledge_chunks_document_id_knowledge_documents",
            ondelete="CASCADE",
        ),
    )

    op.create_index("ix_error_codes_code", "error_codes", ["code"])
    op.create_index(
        "ix_knowledge_documents_manufacturer",
        "knowledge_documents",
        ["manufacturer"],
    )
    op.create_index(
        "ix_knowledge_documents_equipment_model",
        "knowledge_documents",
        ["equipment_model"],
    )
    op.create_index(
        "ix_knowledge_documents_category",
        "knowledge_documents",
        ["category"],
    )
    op.create_index(
        "ix_knowledge_chunks_manufacturer",
        "knowledge_chunks",
        ["manufacturer"],
    )
    op.create_index(
        "ix_knowledge_chunks_equipment_model",
        "knowledge_chunks",
        ["equipment_model"],
    )
    op.create_index(
        "ix_knowledge_chunks_category",
        "knowledge_chunks",
        ["category"],
    )
    op.execute(
        """
        CREATE INDEX ix_knowledge_chunks_embedding_hnsw
        ON knowledge_chunks USING hnsw (embedding vector_cosine_ops)
        WHERE embedding IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunks_embedding_hnsw")
    op.drop_index("ix_knowledge_chunks_category", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_equipment_model", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_chunks_manufacturer", table_name="knowledge_chunks")
    op.drop_index("ix_knowledge_documents_category", table_name="knowledge_documents")
    op.drop_index(
        "ix_knowledge_documents_equipment_model",
        table_name="knowledge_documents",
    )
    op.drop_index("ix_knowledge_documents_manufacturer", table_name="knowledge_documents")
    op.drop_index("ix_error_codes_code", table_name="error_codes")
    op.drop_table("knowledge_chunks")
    op.drop_table("error_codes")
    op.drop_table("messages")
    op.drop_table("knowledge_documents")
    op.drop_table("manufacturers")
    op.drop_table("conversations")
