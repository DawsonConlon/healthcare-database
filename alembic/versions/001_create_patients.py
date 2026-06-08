"""create patients table

Revision ID: 001
Revises:
Create Date: 2026-06-06
"""

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.execute("""
        CREATE TABLE patients (
            patient_id                     UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            first_name                     VARCHAR(100) NOT NULL,
            last_name                      VARCHAR(100) NOT NULL,
            date_of_birth                  DATE         NOT NULL,
            sex                            VARCHAR(10),
            health_card_number             VARCHAR(20),
            health_card_province           CHAR(2),
            phone                          VARCHAR(20),
            email                          VARCHAR(255),
            address_line1                  VARCHAR(255),
            address_line2                  VARCHAR(255),
            city                           VARCHAR(100),
            province                       CHAR(2),
            postal_code                    VARCHAR(7),
            emergency_contact_name         VARCHAR(200),
            emergency_contact_phone        VARCHAR(20),
            emergency_contact_relationship VARCHAR(50),
            guardian_name                  VARCHAR(200),
            guardian_phone                 VARCHAR(20),
            consent_given                  BOOLEAN      NOT NULL DEFAULT FALSE,
            consent_given_at               TIMESTAMPTZ,
            consent_withdrawn_at           TIMESTAMPTZ,
            created_at                     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at                     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            archived_at                    TIMESTAMPTZ,
            CONSTRAINT uq_health_card UNIQUE (health_card_number)
        );
    """)

    # speed up lookups by last name and date of birth
    op.execute("CREATE INDEX idx_patients_last_name ON patients (last_name);")
    op.execute("CREATE INDEX idx_patients_dob ON patients (date_of_birth);")

    # Trigger function to auto-update updated_at on any row change
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_patients_updated_at
        BEFORE UPDATE ON patients
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_patients_updated_at ON patients;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
    op.execute("DROP TABLE IF EXISTS patients;")
