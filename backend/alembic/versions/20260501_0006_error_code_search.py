"""Add searchable error-code metadata.

Revision ID: 20260501_0006
Revises: 20260501_0005
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260501_0006"
down_revision: Union[str, None] = "20260501_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE error_codes
            ADD COLUMN IF NOT EXISTS source VARCHAR(500),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
                NOT NULL DEFAULT now()
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_manufacturer "
        "ON error_codes (manufacturer)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_model "
        "ON error_codes (model)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_manufacturer_model "
        "ON error_codes (manufacturer, model)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_error_codes_updated_at "
        "ON error_codes (updated_at)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_error_codes_updated_at")
    op.execute("DROP INDEX IF EXISTS ix_error_codes_manufacturer_model")
    op.execute("DROP INDEX IF EXISTS ix_error_codes_model")
    op.execute("DROP INDEX IF EXISTS ix_error_codes_manufacturer")
    op.execute(
        """
        ALTER TABLE error_codes
            DROP COLUMN IF EXISTS updated_at,
            DROP COLUMN IF EXISTS source
        """
    )
