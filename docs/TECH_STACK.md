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

## 4. Database Migrations: Two Options — You Choose

A "migration" is a versioned SQL file that describes a change to the schema. Running migrations in order takes a fresh database and builds up the full schema step by step. This is how schema changes are tracked in version control.

---

### Option A: Plain Numbered SQL Files + yoyo-migrations

Files live in `migrations/` and are numbered:
```
migrations/
├── 001_create_patients.sql
├── 002_create_appointments.sql
├── 003_add_consent_to_patients.sql
```

A tool called `yoyo-migrations` runs them in order and tracks which ones have been applied.

**Pros:**
- Completely transparent — every migration is just a `.sql` file you can read
- Easy to understand as a beginner
- No Python abstraction on top of your SQL

**Cons:**
- Rollback support requires you to write a separate `down` migration manually
- Less commonly used in large production Python projects

**Good for:** Learning, smaller projects, teams that prefer SQL-first.

---

### Option B: Alembic (Recommended for Production Path)

Alembic is the migration tool used alongside SQLAlchemy, but it works perfectly with raw SQL — you don't need to use SQLAlchemy models.

```
alembic/
├── versions/
│   ├── 001_create_patients.py   ← contains raw SQL inside
│   └── 002_create_appointments.py
└── env.py
```

Each migration file looks like this (raw SQL inside Python):
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

**Run commands:**
```bash
alembic upgrade head      # apply all pending migrations
alembic downgrade -1      # roll back the last migration
alembic history           # see what has been applied
```

**Pros:**
- Built-in rollback (`downgrade`) for every migration
- Industry standard in Python projects — any Python developer will know it
- `alembic history` gives you a clear audit trail of schema changes
- Works cleanly with AWS RDS

**Cons:**
- Slightly more setup (a few config files)
- Migration files are `.py` not `.sql` — slightly less "pure"

**Recommendation: Alembic.** When we move to AWS, having proper rollback support and a clean migration history will matter. The extra setup is a one-time cost.

---

### Decision Needed

> **Before Session 2 begins:** Review both options above and pick one. Once chosen, we set it up and stick with it for the entire project.

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
| Alembic or yoyo | TBD | Schema migrations | **Needs decision** |
| FastAPI | latest | REST API layer | Future |
| AWS RDS | PostgreSQL 16 | Production hosting | Future |
| AWS Secrets Manager | — | Credential management | Future |
