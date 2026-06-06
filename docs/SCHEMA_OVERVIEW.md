# Schema Overview

This document tracks all database tables, their purpose, and their current build status.

Tables are built one at a time, tested, and signed off before the next one is started.

---

## Build Order & Status

| # | Table | Module | Status |
|---|---|---|---|
| 1 | `patients` | Patients & Demographics | ✅ Built & Verified |
| 2 | `providers` | Providers & Staff | ✅ Built & Verified |
| 3 | `appointments` | Appointments & Scheduling | ✅ Built & Verified |
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

### `providers` ✅

**Migration:** `alembic/versions/002_create_providers.py`  
**Built:** Session 3

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `provider_id` | UUID PK | No | `DEFAULT gen_random_uuid()` |
| `first_name` | VARCHAR(100) | No | |
| `last_name` | VARCHAR(100) | No | |
| `role` | `provider_role` ENUM | No | 'doctor' / 'nurse' / 'admin' |
| `specialty` | VARCHAR(100) | Yes | e.g. 'General Practice', 'Pediatrics' |
| `license_number` | VARCHAR(50) | Yes | Required for doctor/nurse; null for admin |
| `license_province` | CHAR(2) | Yes | Province where licensed |
| `email` | VARCHAR(255) | No | UNIQUE — identification only (auth is future) |
| `phone` | VARCHAR(20) | Yes | |
| `active` | BOOLEAN | No | DEFAULT TRUE |
| `created_at` | TIMESTAMPTZ | No | DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | No | DEFAULT NOW(), auto-updated via trigger |
| `archived_at` | TIMESTAMPTZ | Yes | NULL = active; set = soft-deleted |

**Indexes:** `idx_providers_last_name`, `idx_providers_role`  
**Unique:** `uq_provider_email`, `uq_provider_license` (partial — allows NULL for admin)  
**Trigger:** `trg_providers_updated_at` — reuses `set_updated_at()` from migration 001  
**Enum type:** `provider_role`

---

### `appointments` ✅

**Migration:** `alembic/versions/003_create_appointments.py`  
**Built:** Session 4

| Column | Type | Nullable | Notes |
|---|---|---|---|
| `appointment_id` | UUID PK | No | `DEFAULT gen_random_uuid()` |
| `patient_id` | UUID FK | No | `REFERENCES patients(patient_id)` |
| `provider_id` | UUID FK | No | `REFERENCES providers(provider_id)` |
| `scheduled_at` | TIMESTAMPTZ | No | Booked date/time of visit |
| `duration_minutes` | INTEGER | No | DEFAULT 30 |
| `visit_type` | `appointment_visit_type` ENUM | No | in_person / telehealth / follow_up / urgent |
| `status` | `appointment_status` ENUM | No | DEFAULT 'scheduled' |
| `reason` | TEXT | Yes | Patient-reported reason |
| `notes` | TEXT | Yes | Provider notes pre/post visit |
| `cancelled_at` | TIMESTAMPTZ | Yes | Set when status → cancelled |
| `created_at` | TIMESTAMPTZ | No | DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | No | DEFAULT NOW(), auto-updated via trigger |
| `archived_at` | TIMESTAMPTZ | Yes | NULL = active; set = soft-deleted |

**Indexes:** `idx_appointments_patient_id`, `idx_appointments_provider_id`, `idx_appointments_scheduled_at`, `idx_appointments_status`  
**Foreign keys:** `patient_id → patients`, `provider_id → providers`  
**Trigger:** `trg_appointments_updated_at` — reuses `set_updated_at()` from migration 001  
**Enum types:** `appointment_status`, `appointment_visit_type`

---

### Upcoming: `medical_records`

Stores clinical notes and visit summaries tied to a completed appointment.
