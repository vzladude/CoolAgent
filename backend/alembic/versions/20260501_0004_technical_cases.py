"""Rename conversations to technical cases and add context metadata.

Revision ID: 20260501_0004
Revises: 20260501_0003
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260501_0004"
down_revision: Union[str, None] = "20260501_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.conversations') IS NOT NULL
               AND to_regclass('public.technical_cases') IS NULL THEN
                ALTER TABLE conversations RENAME TO technical_cases;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        ALTER TABLE technical_cases
            ADD COLUMN IF NOT EXISTS manufacturer VARCHAR(200),
            ADD COLUMN IF NOT EXISTS equipment_model VARCHAR(200),
            ADD COLUMN IF NOT EXISTS category VARCHAR(100),
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'open',
            ADD COLUMN IF NOT EXISTS context_summary TEXT,
            ADD COLUMN IF NOT EXISTS summary_until_message_id UUID,
            ADD COLUMN IF NOT EXISTS summary_updated_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS summary_model VARCHAR(150)
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE messages
                RENAME COLUMN conversation_id TO technical_case_id;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE usage_events
                RENAME COLUMN conversation_id TO technical_case_id;
            END IF;
        END $$;
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technical_cases_status "
        "ON technical_cases (status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_messages_technical_case_id "
        "ON messages (technical_case_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_technical_case_id "
        "ON usage_events (technical_case_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_usage_events_technical_case_id")
    op.execute("DROP INDEX IF EXISTS ix_messages_technical_case_id")
    op.execute("DROP INDEX IF EXISTS ix_technical_cases_status")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) THEN
                ALTER TABLE usage_events
                RENAME COLUMN technical_case_id TO conversation_id;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) THEN
                ALTER TABLE messages
                RENAME COLUMN technical_case_id TO conversation_id;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        ALTER TABLE technical_cases
            DROP COLUMN IF EXISTS summary_model,
            DROP COLUMN IF EXISTS summary_updated_at,
            DROP COLUMN IF EXISTS summary_until_message_id,
            DROP COLUMN IF EXISTS context_summary,
            DROP COLUMN IF EXISTS status,
            DROP COLUMN IF EXISTS category,
            DROP COLUMN IF EXISTS equipment_model,
            DROP COLUMN IF EXISTS manufacturer
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.technical_cases') IS NOT NULL
               AND to_regclass('public.conversations') IS NULL THEN
                ALTER TABLE technical_cases RENAME TO conversations;
            END IF;
        END $$;
        """
    )
