"""Merge legacy conversations into technical cases.

Revision ID: 20260501_0005
Revises: 20260501_0004
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260501_0005"
down_revision: Union[str, None] = "20260501_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.technical_cases') IS NULL
               AND to_regclass('public.conversations') IS NOT NULL THEN
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
            IF to_regclass('public.conversations') IS NOT NULL THEN
                INSERT INTO technical_cases (
                    id,
                    title,
                    status,
                    created_at,
                    updated_at
                )
                SELECT
                    conversations.id,
                    conversations.title,
                    'open',
                    conversations.created_at,
                    conversations.updated_at
                FROM conversations
                ON CONFLICT (id) DO NOTHING;
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
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE messages
                RENAME COLUMN conversation_id TO technical_case_id;
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'conversation_id'
            ) AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'messages'
                   AND column_name = 'technical_case_id'
            ) THEN
                UPDATE messages
                   SET technical_case_id = conversation_id
                 WHERE technical_case_id IS NULL;
                ALTER TABLE messages DROP COLUMN conversation_id;
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
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) THEN
                ALTER TABLE usage_events
                RENAME COLUMN conversation_id TO technical_case_id;
            ELSIF EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'conversation_id'
            ) AND EXISTS (
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public'
                   AND table_name = 'usage_events'
                   AND column_name = 'technical_case_id'
            ) THEN
                UPDATE usage_events
                   SET technical_case_id = conversation_id
                 WHERE technical_case_id IS NULL;
                ALTER TABLE usage_events DROP COLUMN conversation_id;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            constraint_record record;
        BEGIN
            FOR constraint_record IN
                SELECT DISTINCT c.conname
                  FROM pg_constraint c
                  JOIN pg_attribute a
                    ON a.attrelid = c.conrelid
                   AND a.attnum = ANY(c.conkey)
                 WHERE c.conrelid = 'public.messages'::regclass
                   AND c.contype = 'f'
                   AND a.attname IN ('conversation_id', 'technical_case_id')
            LOOP
                EXECUTE format(
                    'ALTER TABLE messages DROP CONSTRAINT IF EXISTS %I',
                    constraint_record.conname
                );
            END LOOP;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_messages_technical_case_id_technical_cases'
                   AND conrelid = 'public.messages'::regclass
            ) THEN
                ALTER TABLE messages
                ADD CONSTRAINT fk_messages_technical_case_id_technical_cases
                FOREIGN KEY (technical_case_id)
                REFERENCES technical_cases(id)
                ON DELETE CASCADE;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        DECLARE
            constraint_record record;
        BEGIN
            FOR constraint_record IN
                SELECT DISTINCT c.conname
                  FROM pg_constraint c
                  JOIN pg_attribute a
                    ON a.attrelid = c.conrelid
                   AND a.attnum = ANY(c.conkey)
                 WHERE c.conrelid = 'public.usage_events'::regclass
                   AND c.contype = 'f'
                   AND a.attname IN ('conversation_id', 'technical_case_id')
            LOOP
                EXECUTE format(
                    'ALTER TABLE usage_events DROP CONSTRAINT IF EXISTS %I',
                    constraint_record.conname
                );
            END LOOP;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_usage_events_technical_case_id_technical_cases'
                   AND conrelid = 'public.usage_events'::regclass
            ) THEN
                ALTER TABLE usage_events
                ADD CONSTRAINT fk_usage_events_technical_case_id_technical_cases
                FOREIGN KEY (technical_case_id)
                REFERENCES technical_cases(id)
                ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'ck_technical_cases_status'
                   AND conrelid = 'public.technical_cases'::regclass
            ) THEN
                ALTER TABLE technical_cases
                ADD CONSTRAINT ck_technical_cases_status
                CHECK (status IN ('open', 'closed'));
            END IF;
        END $$;
        """
    )
    op.execute("DROP INDEX IF EXISTS ix_usage_events_conversation_id")
    op.execute("CREATE INDEX IF NOT EXISTS ix_technical_cases_status ON technical_cases (status)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_messages_technical_case_id "
        "ON messages (technical_case_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_technical_case_id "
        "ON usage_events (technical_case_id)"
    )
    op.execute("DROP TABLE IF EXISTS conversations")


def downgrade() -> None:
    op.execute("ALTER TABLE technical_cases DROP CONSTRAINT IF EXISTS ck_technical_cases_status")
