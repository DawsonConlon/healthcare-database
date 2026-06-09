"""
routers/appointments.py - Appointment API endpoints.

This router handles all operations on the appointments table.
It is mounted at /appointments in main.py, so:
    GET   /appointments        -> list_appointments()
    POST  /appointments        -> create_appointment()
    PATCH /appointments/{id}   -> update_appointment_status()

Appointments link a patient to a provider for a scheduled visit.
Full implementation is built in sessions UI-4 and UI-5.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_appointments(status: str = None, provider_id: str = None):
    """
    List all active (non-archived) appointments.

    Optional query parameters:
        ?status=scheduled      - filter by appointment status
                                 (scheduled, confirmed, completed, cancelled, no_show)
        ?provider_id=<uuid>    - filter to appointments for a specific provider

    Both filters can be combined.
    Results are sorted by scheduled_at ascending (soonest first).
    Full implementation: UI-4.
    """
    return {"message": "appointments list - coming in UI-4"}


@router.post("/")
def create_appointment():
    """
    Create a new appointment linking a patient to a provider.

    Accepts appointment fields in the request body.
    Status defaults to 'scheduled' (set by the database).
    Returns the newly created appointment including its generated appointment_id.
    Full implementation: UI-5.
    """
    return {"message": "create appointment - coming in UI-5"}


@router.patch("/{appointment_id}")
def update_appointment_status(appointment_id: str):
    """
    Update the status of an existing appointment.

    Used when a provider confirms, completes, or cancels an appointment.
    When status is set to 'cancelled', cancelled_at is also stamped automatically.
    Full implementation: UI-5.
    """
    return {"message": f"update appointment {appointment_id} - coming in UI-5"}
