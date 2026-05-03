"""Add users table for authentication.

Revision ID: 20260503_0008
Revises: 20260502_0007
Create Date: 2026-05-03
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260503_0008"
down_revision: Union[str, None] = "20260502_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            email VARCHAR(320) NOT NULL,
            full_name VARCHAR(200),
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'technician',
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_verified BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
            last_login_at TIMESTAMP WITH TIME ZONE
        )
        """
    )
    op.execute(
        """
        ALTER TABLE users
            ADD COLUMN IF NOT EXISTS email VARCHAR(320),
            ADD COLUMN IF NOT EXISTS full_name VARCHAR(200),
            ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
            ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'technician',
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true,
            ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT false,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                 WHERE conname = 'uq_users_email'
                   AND conrelid = 'public.users'::regclass
            ) THEN
                ALTER TABLE users
                ADD CONSTRAINT uq_users_email UNIQUE (email);
            END IF;
        END $$;
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_is_active ON users (is_active)")


def downgrade() -> None:
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
