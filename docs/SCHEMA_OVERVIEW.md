# Schema Overview

This document tracks all database tables, their purpose, and their current build status.

Tables are built one at a time, tested, and signed off before the next one is started.

---

## Build Order & Status

| # | Table | Module | Status |
|---|---|---|---|
| 1 | `patients` | Patients & Demographics | ⬜ Planned |
| 2 | `providers` | Providers & Staff | ⬜ Planned |
| 3 | `appointments` | Appointments & Scheduling | ⬜ Planned |
| 4 | `medical_records` | Medical Records / Notes | ⬜ Planned |
| 5 | `audit_log` | Audit & Compliance | ⬜ Planned |
| 6 | `billing` | Billing | ⬜ Future |
| 7 | `prescriptions` | Prescriptions | ⬜ Future |
| 8 | `lab_results` | Lab Results | ⬜ Future |

---

## Table Designs

> Designs will be added here as each table is planned and approved before building.

### Upcoming: `patients`

Columns under consideration:
- `patient_id` — UUID primary key
- `first_name`, `last_name` — encrypted
- `date_of_birth` — encrypted
- `health_card_number` — column-level encryption (`pgcrypto`)
- `phone`, `email`, `address` — encrypted
- `emergency_contact_name`, `emergency_contact_phone`
- `consent_given` — boolean
- `consent_given_at` — timestamp
- `consent_withdrawn_at` — nullable timestamp
- `created_at`, `updated_at` — timestamps
- `archived_at` — nullable, for soft deletes (PIPEDA retention)
- `active` — boolean derived from `archived_at IS NULL`
