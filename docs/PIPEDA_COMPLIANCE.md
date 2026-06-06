# PIPEDA Compliance Checklist

Canada's *Personal Information Protection and Electronic Documents Act* (PIPEDA) governs how private-sector organizations collect, use, and disclose personal information — including health information for private clinics. Provincial health privacy laws (e.g., Ontario's PHIPA, Alberta's HIA) layer on top of this.

This document tracks compliance requirements and our implementation status.

---

## Status Key
- ⬜ **Planned** — requirement identified, not yet implemented
- 🔄 **In Progress** — partially implemented
- ✅ **Implemented** — built and tested
- ❌ **Not Applicable** — does not apply to this project scope

---

## 1. Accountability

| Requirement | Status | Notes |
|---|---|---|
| Designate a privacy officer responsible for compliance | ⬜ Planned | In a real clinic, a named individual |
| Maintain a privacy policy | ⬜ Planned | Document to be created |

---

## 2. Identifying Purposes

| Requirement | Status | Notes |
|---|---|---|
| Document why each data field is collected | ⬜ Planned | Will be annotated in SCHEMA_OVERVIEW.md |
| Only collect data necessary for the stated purpose (data minimization) | ⬜ Planned | Schema design will enforce this |

---

## 3. Consent

| Requirement | Status | Notes |
|---|---|---|
| Patient consent must be obtained and recorded | ⬜ Planned | `consent_given` field + timestamp in `patients` table |
| Consent must be informed (patient understands what they're agreeing to) | ⬜ Planned | Application-layer concern |
| Withdrawal of consent must be supported | ⬜ Planned | Schema must support `consent_withdrawn_at` |

---

## 4. Limiting Collection

| Requirement | Status | Notes |
|---|---|---|
| Do not collect more personal information than needed | ⬜ Planned | Enforced during schema design review |

---

## 5. Limiting Use, Disclosure, and Retention

| Requirement | Status | Notes |
|---|---|---|
| PHI used only for the purpose it was collected | ⬜ Planned | Role-based access control (RBAC) in schema |
| Retention policy: data deleted or anonymized when no longer needed | ⬜ Planned | `archived_at` / soft-delete pattern |

---

## 6. Accuracy

| Requirement | Status | Notes |
|---|---|---|
| Patient records must be accurate and up-to-date | ⬜ Planned | `updated_at` timestamp on all patient tables |
| Patients have the right to correct their information | ⬜ Planned | Schema must allow amendments with audit trail |

---

## 7. Safeguards (Security) — Critical for Database Design

| Requirement | Status | Notes |
|---|---|---|
| Encryption in transit (TLS) for all DB connections | ⬜ Planned | `sslmode=require` in psycopg3 connection string |
| Encryption at rest for PHI fields | ⬜ Planned | `pgcrypto` extension OR AWS RDS volume encryption |
| Role-based access control — staff only see what they need | ⬜ Planned | PostgreSQL roles + Row Level Security (RLS) |
| Audit log: record who accessed or changed patient data | ⬜ Planned | Dedicated `audit_log` table + triggers |
| Strong password hashing for staff accounts | ⬜ Planned | `pgcrypto` `crypt()` or application-layer bcrypt |
| Database not publicly accessible | ⬜ Planned | Docker: internal network only. AWS: private subnet |

---

## 8. Openness

| Requirement | Status | Notes |
|---|---|---|
| Privacy practices are documented and available | ⬜ Planned | This file + privacy policy |

---

## 9. Individual Access

| Requirement | Status | Notes |
|---|---|---|
| Patients can request a copy of their data | ⬜ Planned | Schema must support full export per `patient_id` |
| Patients can challenge accuracy of their data | ⬜ Planned | Amendment workflow with audit trail |

---

## 10. Challenging Compliance

| Requirement | Status | Notes |
|---|---|---|
| Process for handling privacy complaints | ⬜ Planned | Out of scope for DB — application/process concern |

---

## PHI Fields Inventory

Fields that contain Protected Health Information and require special handling:

| Table | Field | Sensitivity | Protection Method |
|---|---|---|---|
| patients | `last_name`, `first_name` | High | Encryption at rest |
| patients | `date_of_birth` | High | Encryption at rest |
| patients | `health_card_number` | Very High | Column-level encryption (`pgcrypto`) |
| patients | `phone`, `email`, `address` | High | Encryption at rest |
| medical_records | `diagnosis`, `notes` | Very High | Encryption at rest |
| prescriptions | `medication`, `dosage` | High | Encryption at rest |

> This table will be updated as new tables are added to the schema.

---

## Resources

- [PIPEDA Fair Information Principles](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/p_principle/)
- [Ontario PHIPA](https://www.ontario.ca/laws/statute/04p03)
- [Alberta HIA](https://www.alberta.ca/health-information-act)
- [OPC PIPEDA guidance for health information](https://www.priv.gc.ca/en/privacy-topics/health-genetic-and-other-body-information/)
