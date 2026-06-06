"""create appointments table

Revision ID: 003
Revises: 002
Create Date: 2026-06-06
"""

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

from alembic import op


def upgrade() -> None:
    op.execute("""
        CREATE TYPE appointment_status AS ENUM (
            'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
        );
    """)

    op.execute("""
        CREATE TYPE appointment_visit_type AS ENUM (
            'in_person', 'telehealth', 'follow_up', 'urgent'
        );
    """)

    op.execute("""
        CREATE TABLE appointments (
            appointment_id   UUID                   PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id       UUID                   NOT NULL REFERENCES patients(patient_id),
            provider_id      UUID                   NOT NULL REFERENCES providers(provider_id),
            scheduled_at     TIMESTAMPTZ            NOT NULL,
            duration_minutes INTEGER                NOT NULL DEFAULT 30,
            visit_type       appointment_visit_type NOT NULL,
            status           appointment_status     NOT NULL DEFAULT 'scheduled',
            reason           TEXT,
            notes            TEXT,
            cancelled_at     TIMESTAMPTZ,
            created_at       TIMESTAMPTZ            NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMPTZ            NOT NULL DEFAULT NOW(),
            archived_at      TIMESTAMPTZ
        );
    """)

    op.execute("CREATE INDEX idx_appointments_patient_id ON appointments (patient_id);")
    op.execute("CREATE INDEX idx_appointments_provider_id ON appointments (provider_id);")
    op.execute("CREATE INDEX idx_appointments_scheduled_at ON appointments (scheduled_at);")
    op.execute("CREATE INDEX idx_appointments_status ON appointments (status);")

    op.execute("""
        CREATE TRIGGER trg_appointments_updated_at
        BEFORE UPDATE ON appointments
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_appointments_updated_at ON appointments;")
    op.execute("DROP TABLE IF EXISTS appointments;")
    op.execute("DROP TYPE IF EXISTS appointment_status;")
    op.execute("DROP TYPE IF EXISTS appointment_visit_type;")
