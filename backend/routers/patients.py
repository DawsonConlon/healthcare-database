"""
routers/patients.py - Patient API endpoints.

This router handles all operations on the patients table.
It is mounted at /patients in main.py, so:
    GET  /patients        -> list_patients()
    POST /patients        -> create_patient()
    GET  /patients/{id}   -> get_patient()
    PATCH /patients/{id}  -> update_patient()

Full implementation is built in sessions UI-2 and UI-3.
Stubs are here now so the server starts cleanly and the
/docs page shows the full planned API surface.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_patients(search: str = None):
    """
    List all active (non-archived) patients.

    Optional query parameter:
        ?search=Smith  - filters results to patients whose last name
                         contains the search term (case-insensitive).

    Returns a list of patient summary objects (not the full record).
    Full implementation: UI-2.
    """
    return {"message": "patients list - coming in UI-2"}


@router.post("/")
def create_patient():
    """
    Create a new patient record.

    Accepts patient fields in the request body.
    Returns the newly created patient including their generated patient_id.
    Full implementation: UI-2.
    """
    return {"message": "create patient - coming in UI-2"}


@router.get("/{patient_id}")
def get_patient(patient_id: str):
    """
    Get a single patient by their UUID.

    Returns the full patient record plus a list of their appointments.
    Used by the patient detail page.
    Full implementation: UI-3.
    """
    return {"message": f"get patient {patient_id} - coming in UI-3"}


@router.patch("/{patient_id}")
def update_patient(patient_id: str):
    """
    Update fields on an existing patient record.

    Only the fields included in the request body are changed.
    The updated_at column is auto-stamped by the database trigger.
    Full implementation: UI-3.
    """
    return {"message": f"update patient {patient_id} - coming in UI-3"}
