# Schema Overview

This document tracks all database tables, their purpose, and their current build status.

Tables are built one at a time, tested, and signed off before the next one is started.

---

## Build Order & Status

| # | Table | Module | Status |
|---|---|---|---|
| 1 | `patients` | Patients & Demographics | ✅ Built & Verified |
| 2 | `providers` | Providers & Staff | ⬜ Planned |
| 3 | `appointments` | Appointments & Scheduling | ⬜ Planned |
| 4 | `medical_records` | Medical Records / Notes | ⬜ Planned |
| 5 | `audit_log` | Audit & Compliance | ⬜ Planned |
| 6 | `billing` | Billing | ⬜ Future |
| 7 | `prescriptions` | Prescriptions | ⬜ Future |
| 8 | `lab_results` | Lab Results | ⬜ Future |

---

## Table Designs

---

### `patients` ✅

**Migration:** `alembic/versions/001_create_patients.py`  
**Built:** Session 2

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `patient_id` | UUID PK | No | `DEFAULT gen_random_uuid()` via pgcrypto |
| `first_name` | VARCHAR(100) | No | PHI |
| `last_name` | VARCHAR(100) | No | PHI |
| `date_of_birth` | DATE | No | PHI |
| `sex` | VARCHAR(10) | Yes | M / F / Other / Unknown |
| `health_card_number` | VARCHAR(20) | Yes | PHI — UNIQUE constraint |
| `health_card_province` | CHAR(2) | Yes | e.g. ON, BC, AB |
| `phone` | VARCHAR(20) | Yes | PHI |
| `email` | VARCHAR(255) | Yes | PHI |
| `address_line1` | VARCHAR(255) | Yes | PHI |
| `address_line2` | VARCHAR(255) | Yes | PHI |
| `city` | VARCHAR(100) | Yes | PHI |
| `province` | CHAR(2) | Yes | |
| `postal_code` | VARCHAR(7) | Yes | Canadian format: A1A 1A1 |
| `emergency_contact_name` | VARCHAR(200) | Yes | |
| `emergency_contact_phone` | VARCHAR(20) | Yes | |
| `emergency_contact_relationship` | VARCHAR(50) | Yes | |
| `guardian_name` | VARCHAR(200) | Yes | For minors |
| `guardian_phone` | VARCHAR(20) | Yes | For minors |
| `consent_given` | BOOLEAN | No | DEFAULT FALSE — PIPEDA |
| `consent_given_at` | TIMESTAMPTZ | Yes | |
| `consent_withdrawn_at` | TIMESTAMPTZ | Yes | |
| `created_at` | TIMESTAMPTZ | No | DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | No | DEFAULT NOW(), auto-updated via trigger |
| `archived_at` | TIMESTAMPTZ | Yes | NULL = active, set = soft-deleted |

**Indexes:** `idx_patients_last_name`, `idx_patients_dob`  
**Trigger:** `trg_patients_updated_at` — auto-sets `updated_at` on every UPDATE  
**Extension:** `pgcrypto` (for UUID generation)

---

### Upcoming: `providers`

Staff members (doctors, nurses, admin). Required before `appointments` since appointments reference a provider.

Columns under consideration:
- `provider_id` — UUID PK
- `first_name`, `last_name`
- `role` — enum: doctor / nurse / admin / other
- `license_number` — for regulated health professionals
- `email` — used for login (future)
- `phone`
- `active` — boolean
- `created_at`, `updated_at`
