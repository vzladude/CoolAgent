"""Track error codes as reviewed knowledge-derived records.

Revision ID: 20260502_0007
Revises: 20260501_0006
Create Date: 2026-05-02
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260502_0007"
down_revision: Union[str, None] = "20260501_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE error_codes
            ADD COLUMN IF NOT EXISTS source_document_id UUID,
            ADD COLUMN IF NOT EXISTS source_chunk_id UUID,
            ADD COLUMN IF NOT EXISTS source_page INTEGER,
            ADD COLUMN IF NOT EXISTS source_excerpt TEXT,
            ADD COLUMN IF NOT EXISTS review_status VARCHAR(30)
                NOT NULL DEFAULT 'approved',
            ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION,
            ADD COLUMN IF NOT EXISTS extraction_metadata JSON
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_error_codes_source_document_id_knowledge_documents'
                   AND conrelid = 'public.error_codes'::regclass
            ) THEN
                ALTER TABLE error_codes
                ADD CONSTRAINT fk_error_codes_source_document_id_knowledge_documents
                FOREIGN KEY (source_document_id)
                REFERENCES knowledge_documents(id)
                ON DELETE SET NULL;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_error_codes_source_chunk_id_knowledge_chunks'
                   AND conrelid = 'public.error_codes'::regclass
            ) THEN
                ALTER TABLE error_codes
                ADD CONSTRAINT fk_error_codes_source_chunk_id_knowledge_chunks
                FOREIGN KEY (source_chunk_id)
                REFERENCES knowledge_chunks(id)
                ON DELETE SET NULL;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'ck_error_codes_review_status'
                   AND conrelid = 'public.error_codes'::regclass
            ) THEN
                ALTER TABLE error_codes
                ADD CONSTRAINT ck_error_codes_review_status
                CHECK (review_status IN ('pending_review', 'approved', 'rejected'));
            END IF;
        END $$;
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_review_status "
        "ON error_codes (review_status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_source_document_id "
        "ON error_codes (source_document_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_source_chunk_id "
        "ON error_codes (source_chunk_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_error_codes_source_chunk_id")
    op.execute("DROP INDEX IF EXISTS ix_error_codes_source_document_id")
    op.execute("DROP INDEX IF EXISTS ix_error_codes_review_status")
    op.execute(
        """
        ALTER TABLE error_codes
            DROP CONSTRAINT IF EXISTS ck_error_codes_review_status,
            DROP CONSTRAINT IF EXISTS fk_error_codes_source_chunk_id_knowledge_chunks,
            DROP CONSTRAINT IF EXISTS fk_error_codes_source_document_id_knowledge_documents
        """
    )
    op.execute(
        """
        ALTER TABLE error_codes
            DROP COLUMN IF EXISTS extraction_metadata,
            DROP COLUMN IF EXISTS confidence,
            DROP COLUMN IF EXISTS review_status,
            DROP COLUMN IF EXISTS source_excerpt,
            DROP COLUMN IF EXISTS source_page,
            DROP COLUMN IF EXISTS source_chunk_id,
            DROP COLUMN IF EXISTS source_document_id
        """
    )
