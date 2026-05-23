"""Add optional user ownership to cases and usage.

Revision ID: 20260522_0009
Revises: 20260503_0008
Create Date: 2026-05-22
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260522_0009"
down_revision: Union[str, None] = "20260503_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE technical_cases
            ADD COLUMN IF NOT EXISTS user_id UUID
        """
    )
    op.execute(
        """
        ALTER TABLE usage_events
            ADD COLUMN IF NOT EXISTS user_id UUID
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_technical_cases_user_id_users'
                   AND conrelid = 'public.technical_cases'::regclass
            ) THEN
                ALTER TABLE technical_cases
                ADD CONSTRAINT fk_technical_cases_user_id_users
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE SET NULL;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'fk_usage_events_user_id_users'
                   AND conrelid = 'public.usage_events'::regclass
            ) THEN
                ALTER TABLE usage_events
                ADD CONSTRAINT fk_usage_events_user_id_users
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )
    op.execute(
        """
        UPDATE usage_events ue
           SET user_id = tc.user_id
          FROM technical_cases tc
         WHERE ue.technical_case_id = tc.id
           AND ue.user_id IS NULL
           AND tc.user_id IS NOT NULL
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_technical_cases_user_id "
        "ON technical_cases (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_user_id "
        "ON usage_events (user_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_usage_events_user_id")
    op.execute("DROP INDEX IF EXISTS ix_technical_cases_user_id")
    op.execute(
        """
        ALTER TABLE usage_events
            DROP CONSTRAINT IF EXISTS fk_usage_events_user_id_users,
            DROP COLUMN IF EXISTS user_id
        """
    )
    op.execute(
        """
        ALTER TABLE technical_cases
            DROP CONSTRAINT IF EXISTS fk_technical_cases_user_id_users,
            DROP COLUMN IF EXISTS user_id
        """
    )
