# Project Context - Healthcare Database

This file brings a new AI session fully up to speed on this project.
Read it top to bottom before touching anything.

Last updated: 2026-06-09

---

## What This Project Is

A PIPEDA-compliant PostgreSQL database for a private clinic in Canada, built
as a learning and portfolio project. No real patient data is ever stored here.

The project is being built piece by piece - one thing at a time, tested and
approved before moving to the next. It currently has a working database backend
and a FastAPI server skeleton. A React frontend is next.

GitHub: https://github.com/DawsonConlon/healthcare-database

---

## Rules - Read These First

These rules were established by the user and must be followed in every session:

1. Never commit .env - it contains real local credentials
2. No real PHI (patient health information) is ever committed to the repo
3. No emojis anywhere - not in code, not in documentation, not in comments
4. No em-dashes - use plain hyphens instead
5. Every block of code must have comments explaining what it does
6. Documentation must be plain text - no emoji status indicators
7. Build one piece at a time, test it, then move forward
8. The project uses Python 3.9 - do not use X | Y union type syntax (use Optional[X] from typing instead)

---

## Tech Stack (Locked - Do Not Change)

| Layer | Technology | Notes |
|---|---|---|
| Database | PostgreSQL 16 | Running in Docker on port 5433 |
| Python driver | psycopg3 (psycopg[binary]) | Raw SQL only - no ORM |
| Local dev | Docker + docker-compose | Port 5433 to avoid conflict with local Postgres on 5432 |
| Migrations | Alembic (raw SQL mode) | op.execute() only - no SQLAlchemy models |
| API backend | FastAPI | In progress on the backend branch |
| Frontend | React + Vite + TypeScript | Planned - not started yet |
| Styling | Tailwind CSS + shadcn/ui | Planned with the frontend |
| Future hosting | AWS RDS | Not started |

The virtual environment is at .venv/ in the project root.
Run: source .venv/bin/activate before any Python commands.

---

## Local Credentials (.env - never committed)

```
DATABASE_URL=postgresql+psycopg://postgres:clinic_local_pw@localhost:5433/clinic_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=clinic_local_pw
POSTGRES_DB=clinic_db
```

The DATABASE_URL uses the SQLAlchemy/Alembic format (postgresql+psycopg://).
When using psycopg3 directly (in FastAPI), strip the "+psycopg" part:
    postgresql://postgres:clinic_local_pw@localhost:5433/clinic_db

This conversion is handled automatically in backend/database.py.

---

## How to Start Everything Locally

Three terminals are needed to run the full stack:

Terminal 1 - Database (Docker):
    docker-compose up -d

Terminal 2 - Backend (FastAPI):
    source .venv/bin/activate
    pip install -r backend/requirements.txt
    uvicorn backend.main:app --reload --port 8000

Terminal 3 - Frontend (React) - NOT YET BUILT:
    cd frontend
    npm run dev

The database runs on localhost:5433.
The FastAPI server runs on localhost:8000.
The React dev server will run on localhost:5173.

FastAPI auto-generates interactive API docs at: http://localhost:8000/docs

---

## Git Branch Structure

- main - stable, tested code. Sessions 1-4 (all DB migrations) are here.
- backend - FastAPI server work. Currently active. UI-1 is committed here.
- frontend - React frontend. Not created yet. Branch off main when starting.

Always confirm which branch you are on before writing code:
    git branch

---

## Complete File Structure

```
healthcare_database/
|
|-- backend/                          FastAPI server (on backend branch)
|   |-- __init__.py                   makes backend/ a Python package
|   |-- database.py                   psycopg3 connection pool
|   |-- main.py                       app entry point, CORS, /stats, /health
|   |-- requirements.txt              fastapi, uvicorn, psycopg[binary], psycopg-pool, python-dotenv
|   |-- routers/
|       |-- __init__.py
|       |-- patients.py               patient endpoints (stubs - built in UI-2 and UI-3)
|       |-- providers.py              provider endpoints (stubs - built in UI-6)
|       |-- appointments.py           appointment endpoints (stubs - built in UI-4 and UI-5)
|
|-- alembic/                          migration tooling
|   |-- env.py                        loads DATABASE_URL from .env
|   |-- versions/
|       |-- 001_create_patients.py    patients table + pgcrypto + set_updated_at() trigger
|       |-- 002_create_providers.py   providers table + provider_role ENUM
|       |-- 003_create_appointments.py appointments table + two status ENUMs + FKs
|
|-- docs/
|   |-- SCHEMA_OVERVIEW.md            table-by-table column reference with build status
|   |-- TECH_STACK.md                 tech decisions and rationale
|   |-- PIPEDA_COMPLIANCE.md          10-principle PIPEDA checklist
|
|-- docker-compose.yml                runs postgres:16 on port 5433
|-- alembic.ini                       Alembic config (DATABASE_URL comes from .env not here)
|-- requirements.txt                  root: alembic, psycopg[binary], python-dotenv
|-- .env                              real credentials - git-ignored
|-- .env.example                      safe template - committed
|-- .gitignore
|-- README.md
|-- SECURITY.md
|-- PROJECT_CONTEXT.md                this file
```

---

## Database Schema (What Exists in Postgres Right Now)

Migration chain: base -> 001 (patients) -> 002 (providers) -> 003 (appointments) [HEAD]

Run to confirm: alembic current


### patients table (migration 001)

Core design patterns established here apply to all tables:
- UUID primary key using gen_random_uuid() via pgcrypto extension
- archived_at TIMESTAMPTZ - NULL means active, non-NULL means soft-deleted
- created_at and updated_at both TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at is auto-stamped by the set_updated_at() trigger on every UPDATE

| Column | Type | Nullable | Notes |
|---|---|---|---|
| patient_id | UUID PK | No | gen_random_uuid() |
| first_name | VARCHAR(100) | No | PHI |
| last_name | VARCHAR(100) | No | PHI |
| date_of_birth | DATE | No | PHI |
| sex | VARCHAR(10) | Yes | M / F / Other / Unknown |
| health_card_number | VARCHAR(20) | Yes | PHI - UNIQUE constraint |
| health_card_province | CHAR(2) | Yes | e.g. ON, BC, AB |
| phone | VARCHAR(20) | Yes | PHI |
| email | VARCHAR(255) | Yes | PHI |
| address_line1 | VARCHAR(255) | Yes | PHI |
| address_line2 | VARCHAR(255) | Yes | PHI |
| city | VARCHAR(100) | Yes | PHI |
| province | CHAR(2) | Yes | |
| postal_code | VARCHAR(7) | Yes | Canadian format A1A 1A1 |
| emergency_contact_name | VARCHAR(200) | Yes | |
| emergency_contact_phone | VARCHAR(20) | Yes | |
| emergency_contact_relationship | VARCHAR(50) | Yes | |
| guardian_name | VARCHAR(200) | Yes | For minors |
| guardian_phone | VARCHAR(20) | Yes | For minors |
| consent_given | BOOLEAN | No | DEFAULT FALSE - PIPEDA |
| consent_given_at | TIMESTAMPTZ | Yes | |
| consent_withdrawn_at | TIMESTAMPTZ | Yes | |
| created_at | TIMESTAMPTZ | No | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | No | auto-set by trigger |
| archived_at | TIMESTAMPTZ | Yes | NULL = active |

Indexes: idx_patients_last_name, idx_patients_dob
Unique: uq_health_card on health_card_number
Trigger: trg_patients_updated_at - calls set_updated_at()
Extension: pgcrypto (created once here, reused by all tables)


### providers table (migration 002)

| Column | Type | Nullable | Notes |
|---|---|---|---|
| provider_id | UUID PK | No | gen_random_uuid() |
| first_name | VARCHAR(100) | No | |
| last_name | VARCHAR(100) | No | |
| role | provider_role ENUM | No | doctor / nurse / admin |
| specialty | VARCHAR(100) | Yes | e.g. General Practice |
| license_number | VARCHAR(50) | Yes | Null allowed for admin staff |
| license_province | CHAR(2) | Yes | |
| email | VARCHAR(255) | No | UNIQUE |
| phone | VARCHAR(20) | Yes | |
| active | BOOLEAN | No | DEFAULT TRUE |
| created_at | TIMESTAMPTZ | No | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | No | auto-set by trigger |
| archived_at | TIMESTAMPTZ | Yes | NULL = active |

Indexes: idx_providers_last_name, idx_providers_role
Unique: uq_provider_email, uq_provider_license (partial - WHERE license_number IS NOT NULL)
Partial unique index explanation: admin staff have no license number so multiple NULLs must be
allowed, but any actual license number must be unique across providers.
Trigger: trg_providers_updated_at - reuses set_updated_at() from migration 001
ENUM type: provider_role


### appointments table (migration 003)

First junction table - links patients to providers via foreign keys.

| Column | Type | Nullable | Notes |
|---|---|---|---|
| appointment_id | UUID PK | No | gen_random_uuid() |
| patient_id | UUID FK | No | REFERENCES patients(patient_id) |
| provider_id | UUID FK | No | REFERENCES providers(provider_id) |
| scheduled_at | TIMESTAMPTZ | No | Booked date and time |
| duration_minutes | INTEGER | No | DEFAULT 30 |
| visit_type | appointment_visit_type ENUM | No | in_person / telehealth / follow_up / urgent |
| status | appointment_status ENUM | No | DEFAULT scheduled |
| reason | TEXT | Yes | Patient-reported reason |
| notes | TEXT | Yes | Provider notes |
| cancelled_at | TIMESTAMPTZ | Yes | Set when status changes to cancelled |
| created_at | TIMESTAMPTZ | No | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | No | auto-set by trigger |
| archived_at | TIMESTAMPTZ | Yes | NULL = active |

Indexes: idx_appointments_patient_id, idx_appointments_provider_id,
         idx_appointments_scheduled_at, idx_appointments_status
Foreign keys: patient_id references patients, provider_id references providers
Trigger: trg_appointments_updated_at - reuses set_updated_at()
ENUM types: appointment_status, appointment_visit_type


### Shared trigger function (created in migration 001)

set_updated_at() is a PL/pgSQL function created once in migration 001.
Every subsequent table wires its own trigger to this same function.
The downgrade of migration 002 and 003 must NOT drop this function - it belongs to 001.

---

## FastAPI Backend - Current State (UI-2 Complete)

The backend folder is on the backend branch. PR #1 is open against main.

What is implemented:
- GET /health - returns {"status": "ok"}
- GET /stats  - returns total_patients, total_providers, appointments_today (live DB queries)
- GET /patients - real SQL, optional ?search= on last_name ILIKE, ORDER BY last_name ASC
- POST /patients - real INSERT with RETURNING, auto-stamps consent_given_at when consent_given=true
- GET /patients/{id} - stub (UI-3)
- PATCH /patients/{id} - stub (UI-3)
- GET/POST /providers - stub (UI-6)
- GET/POST /appointments - stub (UI-4)
- PATCH /appointments/{id} - stub (UI-5)

Pydantic models in patients.py:
- PatientCreate: required (first_name, last_name, date_of_birth, consent_given) + all optional columns
- PatientSummary: response shape for list and create

The connection pool is opened at app startup via FastAPI's lifespan pattern
(in main.py) and shared by all route handlers via database.get_pool().

## React Frontend - Current State (UI-2 Complete)

The frontend folder is on the frontend branch. PR #2 is open against main.

Stack confirmed and locked:
- React 19 + Vite + TypeScript (scaffold installed React 19, not 18 - both work the same)
- Tailwind CSS v4 with @tailwindcss/vite plugin (no postcss config needed)
- shadcn/ui components installed: button, input, dialog, table
- Dark mode: class="dark" hardcoded on <html> in index.html - no toggle
- HTTP client: axios via src/api/patients.ts

Important Tailwind v4 note: there is no tailwind.config.js file.
Configuration is done via CSS @theme in src/index.css.
The npx tailwindcss init command does not exist in v4.
Use: npm install -D @tailwindcss/vite

Important shadcn note: shadcn creates files relative to the aliases in components.json.
If the alias resolves incorrectly, files land in a literal "@/" folder.
The fix is to move them manually to src/components/ui/ and src/lib/.

File structure added:
- frontend/src/api/patients.ts     - typed axios client (listPatients, createPatient)
- frontend/src/components/Sidebar.tsx  - fixed sidebar, NavLink active highlighting
- frontend/src/components/ui/      - shadcn components (button, dialog, input, table)
- frontend/src/lib/utils.ts        - shadcn cn() utility
- frontend/src/pages/DashboardPage.tsx    - stat cards from GET /stats
- frontend/src/pages/PatientsPage.tsx     - table, search, detail panel, add dialog
- frontend/src/pages/PlaceholderPage.tsx  - placeholder for unbuilt routes
- frontend/src/App.tsx             - BrowserRouter with all 4 routes
- .claude/launch.json              - preview server config (npm --prefix frontend run dev)

---

## Planned UI Build Order

Each session below follows the same pattern: build, test, commit.

| Session | What Gets Built | Status |
|---|---|---|
| UI-1 | FastAPI skeleton, /stats, /health, router stubs, CORS | Complete |
| UI-2 | Patient list + search endpoints, React app scaffold, Patients page | Complete |
| UI-3 | Patient detail page, edit form, PATCH /patients/{id} endpoint | Next |
| UI-4 | Appointments endpoints, Appointments list page | Planned |
| UI-5 | Add appointment form, status update (confirm/cancel/complete) | Planned |
| UI-6 | Providers page, polish, dark mode refinement, nav sidebar | Planned |


### React frontend decisions (locked as of UI-2)

- Framework: React 19 + Vite + TypeScript (scaffold defaulted to 19)
- Styling: Tailwind CSS v4 + shadcn/ui
- HTTP client: axios via src/api/patients.ts
- Auth: none for now
- Location: /frontend folder in the same repo
- Branch: frontend (created, on GitHub, PR #2 open)

Screens planned:
1. Dashboard - stats cards (total patients, today appointments, total providers)
   + recent appointments list
2. Patients list - searchable table, Add Patient button
3. Patient detail - full record + their appointments, Edit button
4. Appointments list - filterable by status and provider, Add Appointment button
5. Providers list - table, Add Provider button

---

## Key Design Patterns - Follow These Consistently

Soft delete: never DELETE rows. Set archived_at = NOW() to deactivate.
All list queries filter with: WHERE archived_at IS NULL

Auto timestamps: created_at and updated_at are always TIMESTAMPTZ NOT NULL DEFAULT NOW().
updated_at is always maintained by the set_updated_at() trigger - never set it manually.

UUIDs: all primary keys are UUID generated by gen_random_uuid() via pgcrypto.
pgcrypto was enabled once in migration 001 and stays enabled.

Migrations: always use op.execute() with raw SQL. Never use SQLAlchemy models.
Always include a downgrade() that exactly reverses the upgrade().
Never drop set_updated_at() in a downgrade unless it is migration 001 being rolled back.

Python 3.9 compatibility: use Optional[X] from typing, not X | None.

---

## Sessions Completed

| Session | What Was Built | Branch | Commit |
|---|---|---|---|
| 1 | Tech stack decisions, project structure, GitHub repo, docs | main | be7011d |
| 2 | Docker, Alembic setup, patients table (migration 001) | main | 56e5f2b |
| 3 | providers table (migration 002) | main | 6bd537d |
| 4 | appointments table (migration 003) | main | 3c81600 |
| UI-1 | FastAPI skeleton, /stats, /health, router stubs | backend | 68b87dc |
| UI-2 | GET/POST /patients (real SQL) + full React frontend scaffold | backend/frontend | 2ef7367 / f17ecff |

PRs open on GitHub: #1 (backend - UI-2), #2 (frontend - UI-2)

---

## What to Do Next (UI-3)

Merge both UI-2 PRs first, then pull main.

Work on the frontend branch (rebase or merge main in first).

Backend (backend/routers/patients.py):
- Replace get_patient() stub:
  SELECT all columns FROM patients WHERE patient_id = %s AND archived_at IS NULL
  Also SELECT appointment list for this patient (patient_id, scheduled_at, status, visit_type, provider name)
  Return 404 if not found
- Replace update_patient() stub:
  Accept partial body (all fields Optional in a PatientUpdate Pydantic model)
  Build a dynamic UPDATE statement - only set columns that are not None
  updated_at is auto-stamped by the DB trigger, do not pass it
  Return the updated row

Frontend (frontend branch):
- Add GET /patients/{id} to src/api/patients.ts
- Add PATCH /patients/{id} to src/api/patients.ts
- Build PatientDetailPage at /patients/:id
  Full record display: all columns, not just summary fields
  Edit button that switches the page into edit mode (inline form)
  Appointment history list at the bottom (date, status, visit type, provider)
- Wire the "Full record (UI-3)" button in the detail panel to navigate to /patients/:id
- Add react-router-dom useParams in the new page to read the UUID from the URL

Test end to end: open a patient detail page, edit a field, confirm the change appears in psql.
