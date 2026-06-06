"""create providers table

Revision ID: 002
Revises: 001
Create Date: 2026-06-06
"""

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    # pgcrypto already enabled by migration 001

    op.execute("""
        CREATE TYPE provider_role AS ENUM ('doctor', 'nurse', 'admin');
    """)

    op.execute("""
        CREATE TABLE providers (
            provider_id      UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
            first_name       VARCHAR(100)  NOT NULL,
            last_name        VARCHAR(100)  NOT NULL,
            role             provider_role NOT NULL,
            specialty        VARCHAR(100),
            license_number   VARCHAR(50),
            license_province CHAR(2),
            email            VARCHAR(255)  NOT NULL,
            phone            VARCHAR(20),
            active           BOOLEAN       NOT NULL DEFAULT TRUE,
            created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            archived_at      TIMESTAMPTZ,
            CONSTRAINT uq_provider_email UNIQUE (email)
        );
    """)

    # Partial unique index — allows multiple NULLs (admin has no license)
    op.execute("CREATE UNIQUE INDEX uq_provider_license ON providers (license_number) WHERE license_number IS NOT NULL;")
    op.execute("CREATE INDEX idx_providers_last_name ON providers (last_name);")
    op.execute("CREATE INDEX idx_providers_role ON providers (role);")

    # set_updated_at() already exists from migration 001 — just wire the trigger
    op.execute("""
        CREATE TRIGGER trg_providers_updated_at
        BEFORE UPDATE ON providers
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_providers_updated_at ON providers;")
    op.execute("DROP TABLE IF EXISTS providers;")
    op.execute("DROP TYPE IF EXISTS provider_role;")
    # Do NOT drop set_updated_at() — it belongs to migration 001
