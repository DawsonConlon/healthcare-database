# Tech Stack — Healthcare Database

This document explains every technology choice for this project, why it was chosen, and what the alternatives were.

---

## 1. Database: PostgreSQL 16

**Why PostgreSQL?**
- The industry standard for relational, structured data in healthcare
- Supports ACID transactions — critical when writing patient records (a failed write must not leave partial data)
- First-class support for `pgcrypto` (column-level encryption) and row-level security (RLS)
- Excellent audit extension ecosystem
- Fully supported by AWS RDS and every major cloud provider
- Free and open source

**Alternatives considered:**
- MySQL/MariaDB — less powerful for complex queries and lacks some security extensions
- SQLite — not suitable for multi-user or production use
- MongoDB — document databases are not ideal for relational healthcare data (patients have appointments, appointments have records — these relationships matter)

---

## 2. Python Driver: psycopg3 (`psycopg[binary]`)

**Why psycopg3?**
- Direct access to PostgreSQL — you write SQL, it executes SQL, no translation layer
- Full control over queries: important when optimizing complex clinical data queries
- `psycopg3` is the current-generation driver (successor to `psycopg2`), with async support built in for when we add a FastAPI layer
- No ORM means no "magic" hiding what queries actually run — in a compliance context, you want to know exactly what touches patient data

**Why not SQLAlchemy?**
- SQLAlchemy is excellent but adds a translation layer between Python objects and SQL
- For learning SQL and database design from the ground up, writing raw SQL is far more educational
- In a PIPEDA-compliant system, you often need to write very specific queries for audit reports — raw SQL is clearer for this

**Installation:**
```bash
pip install "psycopg[binary]"
```

**Basic usage:**
```python
import psycopg

with psycopg.connect("postgresql://user:password@localhost/clinic_db") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT patient_id, last_name FROM patients WHERE active = TRUE")
        rows = cur.fetchall()
```

---

## 3. Local Development: Docker + docker-compose

**Why Docker?**
- Your local Postgres environment is identical to the production environment — no "works on my machine" problems
- Easy to reset: `docker-compose down -v` wipes the database, `docker-compose up -d` starts fresh
- Multiple developers (or future-you on a new laptop) can set up instantly
- Prevents your local Mac from accumulating Postgres versions and data

**docker-compose will provide:**
- A `postgres:16` container with configuration matching production settings
- A named volume so your local data persists between restarts
- Environment variables for credentials (loaded from `.env`, never committed)

> docker-compose.yml will be created in Session 2 when we set up the first migration.

---

## 4. Database Migrations: Alembic ✅

A "migration" is a versioned file that describes a change to the schema. Running migrations in order takes a fresh database and builds up the full schema step by step. This is how schema changes are tracked in version control.

**Decision: Alembic** — chosen for its built-in rollback support, industry-standard status in Python projects, and clean migration history needed for PIPEDA compliance auditing.

Alembic works perfectly with raw SQL — no SQLAlchemy models required.

**Project structure:**
```
alembic/
├── versions/
│   ├── 001_create_patients.py
│   └── 002_create_appointments.py
└── env.py
alembic.ini
```

**Each migration file uses raw SQL inside Python:**
```python
def upgrade():
    op.execute("""
        CREATE TABLE patients (
            patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            last_name  VARCHAR(100) NOT NULL,
            ...
        );
    """)

def downgrade():
    op.execute("DROP TABLE patients;")
```

**Key commands:**
```bash
alembic upgrade head      # apply all pending migrations
alembic downgrade -1      # roll back the last migration
alembic history           # see what has been applied
```

**Installation:**
```bash
pip install alembic
```

> Alembic will be fully set up in Session 2 alongside Docker and the first migration.

---

## 5. Future: FastAPI (API Layer)

We are not building this yet. When we do:
- **FastAPI** — Python web framework, async-first, built-in data validation via Pydantic
- Routes will map to database operations via psycopg3
- JWT authentication for provider login
- Every API endpoint that touches patient data will write to the audit log

---

## 6. Future: AWS RDS (Production Hosting)

When the local version is stable:
- **AWS RDS for PostgreSQL** — managed Postgres, automatic backups, encryption at rest at the volume level
- **AWS Secrets Manager** — store database credentials (never in code or `.env` in production)
- **VPC** — database lives in a private subnet, not publicly accessible
- **Multi-AZ deployment** — for high availability once in production use

---

## Summary Table

| Technology | Version | Purpose | Status |
|---|---|---|---|
| PostgreSQL | 16 | Primary database | Decided |
| psycopg3 | latest | Python ↔ Postgres driver | Decided |
| Docker + docker-compose | latest | Local dev environment | Decided |
| Alembic | latest | Schema migrations | Decided ✅ |
| FastAPI | latest | REST API layer | Future |
| AWS RDS | PostgreSQL 16 | Production hosting | Future |
| AWS Secrets Manager | — | Credential management | Future |
