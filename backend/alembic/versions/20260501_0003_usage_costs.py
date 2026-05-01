"""Add usage cost and cache savings columns.

Revision ID: 20260501_0003
Revises: 20260501_0002
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260501_0003"
down_revision: Union[str, None] = "20260501_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE usage_events
            ADD COLUMN IF NOT EXISTS estimated_cost_usd NUMERIC(12, 8),
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_input INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_output INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_tokens_total INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS cache_saved_cost_usd NUMERIC(12, 8)
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_usage_events_model "
        "ON usage_events (model)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_usage_events_model")
    op.execute(
        """
        ALTER TABLE usage_events
            DROP COLUMN IF EXISTS cache_saved_cost_usd,
            DROP COLUMN IF EXISTS cache_saved_tokens_total,
            DROP COLUMN IF EXISTS cache_saved_tokens_output,
            DROP COLUMN IF EXISTS cache_saved_tokens_input,
            DROP COLUMN IF EXISTS estimated_cost_usd
        """
    )
