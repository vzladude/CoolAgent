"""Add usage tracking table.

Revision ID: 20260501_0002
Revises: 20260430_0001
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260501_0002"
down_revision: Union[str, None] = "20260430_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_events (
            id UUID PRIMARY KEY,
            conversation_id UUID
                REFERENCES conversations(id) ON DELETE SET NULL,
            message_id UUID
                REFERENCES messages(id) ON DELETE SET NULL,
            event_type VARCHAR(50) NOT NULL,
            provider VARCHAR(100),
            model VARCHAR(150),
            prompt_policy_version VARCHAR(100),
            cache_status VARCHAR(20) NOT NULL,
            tokens_input INTEGER NOT NULL,
            tokens_output INTEGER NOT NULL,
            tokens_total INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_conversation_id "
        "ON usage_events (conversation_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_message_id "
        "ON usage_events (message_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_event_type "
        "ON usage_events (event_type)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_cache_status "
        "ON usage_events (cache_status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_created_at "
        "ON usage_events (created_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_usage_events_created_at")
    op.execute("DROP INDEX IF EXISTS ix_usage_events_cache_status")
    op.execute("DROP INDEX IF EXISTS ix_usage_events_event_type")
    op.execute("DROP INDEX IF EXISTS ix_usage_events_message_id")
    op.execute("DROP INDEX IF EXISTS ix_usage_events_conversation_id")
    op.drop_table("usage_events")
