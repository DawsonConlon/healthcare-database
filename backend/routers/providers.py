"""
routers/providers.py - Provider API endpoints.

This router handles all operations on the providers table.
It is mounted at /providers in main.py, so:
    GET  /providers      -> list_providers()
    POST /providers      -> create_provider()

Providers are clinic staff: doctors, nurses, and admin.
Full implementation is built in session UI-6.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_providers():
    """
    List all active (non-archived) providers.

    Returns all clinic staff sorted by last name.
    Used by the Providers page and by the Add Appointment form
    (to populate the provider dropdown).
    Full implementation: UI-6.
    """
    return {"message": "providers list - coming in UI-6"}


@router.post("/")
def create_provider():
    """
    Create a new provider (doctor, nurse, or admin staff member).

    Accepts provider fields in the request body.
    Returns the newly created provider including their generated provider_id.
    Full implementation: UI-6.
    """
    return {"message": "create provider - coming in UI-6"}
