# Healthcare Database

A PostgreSQL-based database for a private clinic/practice, built to Canadian healthcare privacy standards (PIPEDA). This project is developed incrementally — one piece at a time, tested and approved before moving forward.

> **This is a learning/portfolio project. No real patient data is stored here. See [SECURITY.md](SECURITY.md).**

---

## Tech Stack

See [`docs/TECH_STACK.md`](docs/TECH_STACK.md) for the full breakdown and rationale.

| Layer | Technology |
|---|---|
| Database | PostgreSQL 16 |
| Python driver | psycopg3 (`psycopg[binary]`) |
| Local dev | Docker + docker-compose |
| Migrations | Alembic (raw SQL mode) |
| Future API | FastAPI (not yet implemented) |
| Future hosting | AWS RDS |

---

## Project Scope

### Modules (planned in order)
1. **Patients & Demographics** — health card numbers, contact info, emergency contacts
2. **Appointments & Scheduling** — provider assignment, visit type, status
3. **Medical Records / Notes** — clinical notes, diagnoses, visit summaries
4. **Providers & Staff** — roles, credentials
5. **Audit Logs** — PIPEDA-required access and change tracking
6. **Billing** — fees, payments (future)
7. **Prescriptions** — medications, dosage, refills (future)
8. **Lab Results** — orders, results, reference ranges (future)

---

## Privacy & Compliance

This project is designed to meet **PIPEDA** requirements and is compatible with provincial health privacy laws (PHIPA in Ontario, HIA in Alberta, etc.). See [`docs/PIPEDA_COMPLIANCE.md`](docs/PIPEDA_COMPLIANCE.md) for the full compliance checklist.

Key principles applied:
- Encryption at rest for all PHI fields
- TLS required for all database connections
- Audit logging for all access to patient data
- Data minimization — only collect what is clinically necessary
- Consent tracking per patient

---

## Local Development Setup

> Prerequisites: Docker Desktop installed and running.

```bash
# 1. Clone the repo
git clone https://github.com/dawsonconlon/healthcare-database.git
cd healthcare-database

# 2. Copy the environment template (create .env from template)
cp .env.example .env
# Edit .env with your local credentials

# 3. Start the database (runs on localhost:5433 to avoid conflicts with local Postgres)
docker-compose up -d

# 4. Run all migrations
source .venv/bin/activate
alembic upgrade head
```

---

## Build Log

| Session | What Was Built | Status |
|---|---|---|
| 1 | Tech stack decision, project structure, GitHub repo | ✅ Complete |
| 2 | Docker + Alembic setup, `patients` table | ✅ Complete |
| 3 | `providers` table | Planned |
| 4 | `appointments` table | Planned |
| 5 | `medical_records` table | Planned |
| 6 | Audit log table + triggers | Planned |
