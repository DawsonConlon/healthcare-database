"""
routers/patients.py - Patient API endpoints.

This router handles all operations on the patients table.
It is mounted at /patients in main.py, so:
    GET  /patients         -> list_patients()
    POST /patients         -> create_patient()
    GET  /patients/{id}    -> get_patient()       (stub - UI-3)
    PATCH /patients/{id}   -> update_patient()    (stub - UI-3)

UI-2 builds: list_patients() and create_patient() with real SQL.
UI-3 builds: get_patient() and update_patient() with real SQL.
"""

from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

import backend.database as database

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models
#
# Pydantic is FastAPI's validation library. When a route function accepts a
# BaseModel argument, FastAPI automatically:
#   1. Reads the request body as JSON
#   2. Validates every field against the type annotation
#   3. Returns a 422 Unprocessable Entity if anything is wrong
#
# Fields with no default are REQUIRED. Fields with a default of None are
# optional and will be NULL in the database if the caller omits them.
# ---------------------------------------------------------------------------

class PatientCreate(BaseModel):
    """
    Request body accepted by POST /patients.

    Only the required DB fields have no default. Everything else is Optional
    so callers can omit columns they do not have yet - those land as NULL in
    Postgres and can be filled in later via PATCH (UI-3).
    """

    # --- Required fields (NOT NULL in the patients table) ---
    first_name: str
    last_name: str
    date_of_birth: date          # Caller sends an ISO 8601 string: "YYYY-MM-DD"
    consent_given: bool          # PIPEDA: explicit consent must be recorded

    # --- Optional fields (nullable columns in the patients table) ---
    # These are accepted by the API now even though the UI-2 form does not
    # expose them. That keeps the API complete for future use (curl, UI-3).
    sex: Optional[str] = None
    health_card_number: Optional[str] = None
    health_card_province: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None


class PatientSummary(BaseModel):
    """
    The shape of a single patient in the list response.

    This is a summary - not every column. The full record is returned by
    GET /patients/{id} (built in UI-3). Keeping the list lean means less
    data sent over the wire when the table has thousands of rows.
    """

    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: str           # Serialised as "YYYY-MM-DD" for JSON
    province: Optional[str]      # Can be NULL - not every patient has one yet
    consent_given: bool


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _row_to_summary(row: dict) -> dict:
    """
    Convert a psycopg row dict to a plain dict safe for JSON serialisation.

    psycopg3 returns UUID columns as uuid.UUID objects and DATE columns as
    Python date objects. JSON cannot serialise either of those directly, so
    we convert them to strings here before FastAPI turns the dict into a
    JSON response.
    """
    return {
        "patient_id": str(row["patient_id"]),               # uuid.UUID -> string
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "date_of_birth": row["date_of_birth"].isoformat(),  # date -> "YYYY-MM-DD"
        "province": row["province"],
        "consent_given": row["consent_given"],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[PatientSummary])
def list_patients(search: Optional[str] = None):
    """
    Return all active (non-archived) patients, optionally filtered by last name.

    Query parameters:
        ?search=Smith   - case-insensitive substring match on last_name.
                          Returns any patient whose last name contains "Smith".

    Results are sorted alphabetically by last name.
    Archived patients (archived_at IS NOT NULL) are never returned.
    """
    with database.get_pool().connection() as conn:

        # dict_row tells psycopg3 to return each row as a dict keyed by
        # column name instead of a plain tuple. This makes the code easier
        # to read: row["first_name"] instead of row[1].
        with conn.cursor(row_factory=dict_row) as cur:

            if search:
                # ILIKE is Postgres's case-insensitive version of LIKE.
                # The search term is wrapped in % wildcards to match anywhere
                # in the last name (prefix, suffix, or middle).
                # Using %s parameterisation (not f-strings) prevents SQL injection.
                cur.execute(
                    """
                    SELECT patient_id, first_name, last_name, date_of_birth,
                           province, consent_given
                    FROM   patients
                    WHERE  archived_at IS NULL
                      AND  last_name ILIKE %s
                    ORDER  BY last_name ASC
                    """,
                    (f"%{search}%",),
                )
            else:
                # No search term - return every active patient
                cur.execute(
                    """
                    SELECT patient_id, first_name, last_name, date_of_birth,
                           province, consent_given
                    FROM   patients
                    WHERE  archived_at IS NULL
                    ORDER  BY last_name ASC
                    """
                )

            rows = cur.fetchall()

    # Convert every row from a psycopg dict to a JSON-safe plain dict
    return [_row_to_summary(row) for row in rows]


@router.post("/", status_code=201, response_model=PatientSummary)
def create_patient(patient: PatientCreate):
    """
    Insert a new patient record and return the created row.

    HTTP 201 Created is returned on success (rather than 200) to signal that
    a new resource was created. FastAPI returns this automatically because we
    set status_code=201 on the decorator.

    consent_given_at is stamped automatically by this endpoint when
    consent_given is True. The caller never needs to send it manually.

    The patient_id is generated by the database (gen_random_uuid() via
    pgcrypto), so the caller does not include it in the request body. It is
    returned in the response so the frontend can navigate to the new record.
    """

    # Stamp the consent timestamp in Python and pass it to Postgres as a
    # parameterised value. This keeps the "when was consent given" moment
    # accurate to the instant the API received the request.
    # If consent is not given yet, consent_given_at stays NULL.
    consent_at: Optional[datetime] = (
        datetime.now(timezone.utc) if patient.consent_given else None
    )

    with database.get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # INSERT and immediately RETURNING the new row so we can send it
            # back to the caller without a second SELECT query.
            cur.execute(
                """
                INSERT INTO patients (
                    first_name, last_name, date_of_birth,
                    sex, health_card_number, health_card_province,
                    phone, email,
                    address_line1, address_line2, city, province, postal_code,
                    emergency_contact_name, emergency_contact_phone,
                    emergency_contact_relationship,
                    guardian_name, guardian_phone,
                    consent_given, consent_given_at
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    %s,
                    %s, %s,
                    %s, %s
                )
                RETURNING patient_id, first_name, last_name, date_of_birth,
                          province, consent_given
                """,
                (
                    patient.first_name, patient.last_name, patient.date_of_birth,
                    patient.sex, patient.health_card_number, patient.health_card_province,
                    patient.phone, patient.email,
                    patient.address_line1, patient.address_line2, patient.city,
                    patient.province, patient.postal_code,
                    patient.emergency_contact_name, patient.emergency_contact_phone,
                    patient.emergency_contact_relationship,
                    patient.guardian_name, patient.guardian_phone,
                    patient.consent_given, consent_at,
                ),
            )

            new_row = cur.fetchone()

            # psycopg3 does not auto-commit. We must call conn.commit() to
            # persist the INSERT. If we do not, the transaction rolls back
            # when the connection is returned to the pool.
            conn.commit()

    return _row_to_summary(new_row)


# ---------------------------------------------------------------------------
# Stubs for UI-3
# ---------------------------------------------------------------------------

@router.get("/{patient_id}")
def get_patient(patient_id: str):
    """
    Get the full record for a single patient plus their appointment history.

    Returns every column from the patients table (not just the summary fields)
    along with a list of that patient's appointments sorted by scheduled_at.
    Full implementation: UI-3.
    """
    return {"message": f"get patient {patient_id} - coming in UI-3"}


@router.patch("/{patient_id}")
def update_patient(patient_id: str):
    """
    Partially update a patient record.

    Only the fields sent in the request body are changed. The updated_at
    column is automatically re-stamped by the database trigger - do not
    pass it in the request body.
    Full implementation: UI-3.
    """
    return {"message": f"update patient {patient_id} - coming in UI-3"}
