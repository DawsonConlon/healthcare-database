"""
main.py - FastAPI application entry point.

This file does four things:
    1. Creates the FastAPI app instance
    2. Opens the database connection pool on startup, closes it on shutdown
    3. Configures CORS so the React frontend can call this API
    4. Registers the three route modules and the /stats + /health endpoints

To run the server:
    uvicorn backend.main:app --reload --port 8000

Then visit http://localhost:8000/docs for the interactive API documentation
that FastAPI generates automatically from this code.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg_pool import ConnectionPool

import backend.database as database
from backend.routers import patients, providers, appointments


# --- Lifespan: startup and shutdown logic ---
#
# FastAPI's lifespan function replaces the older @app.on_event pattern.
# Everything before `yield` runs on startup; everything after runs on shutdown.
# We use it to open and close the database connection pool.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create the connection pool.
    # min_size=2 means 2 connections are always open and ready.
    # max_size=10 means up to 10 concurrent connections are allowed.
    print("Starting up - opening database connection pool...")
    database.pool = ConnectionPool(
        conninfo=database.DATABASE_URL,
        min_size=2,
        max_size=10,
    )
    print("Database connection pool is ready.")

    yield  # App is running - handle requests here

    # Shutdown: close all connections cleanly.
    print("Shutting down - closing database connection pool...")
    database.pool.close()
    print("Database connection pool closed.")


# --- App instance ---
app = FastAPI(
    title="Healthcare Database API",
    description=(
        "REST API for the clinic database. "
        "Powers the React frontend and provides structured access to "
        "patients, providers, and appointments. "
        "This is a learning and portfolio project - no real patient data."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# --- CORS (Cross-Origin Resource Sharing) ---
#
# Browsers block JavaScript on one origin (localhost:5173) from calling
# an API on a different origin (localhost:8000) unless the server explicitly
# allows it. This middleware tells the browser it is allowed.
#
# allow_origins: only the React dev server is permitted during local development.
# In production this would be set to the real domain name.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"],   # Accept any request headers
)


# --- Route modules ---
#
# Each router module handles one resource. The prefix sets the URL base:
#   patients     -> all routes start with /patients
#   providers    -> all routes start with /providers
#   appointments -> all routes start with /appointments
#
# The tags group them together in the /docs page.
app.include_router(patients.router,     prefix="/patients",     tags=["Patients"])
app.include_router(providers.router,    prefix="/providers",    tags=["Providers"])
app.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])


# --- Dashboard stats endpoint ---
#
# Returns the three numbers shown on the dashboard home screen.
# Queries are run in a single connection checkout for efficiency.
@app.get("/stats", tags=["Dashboard"])
def get_stats():
    """
    Summary counts for the dashboard home screen.

    Returns:
        total_patients:      number of active (non-archived) patients
        total_providers:     number of active providers
        appointments_today:  appointments scheduled for today (any status)
    """
    with database.get_pool().connection() as conn:
        with conn.cursor() as cur:

            # Active patients: archived_at is NULL means the record is not soft-deleted
            cur.execute(
                "SELECT COUNT(*) FROM patients WHERE archived_at IS NULL"
            )
            total_patients = cur.fetchone()[0]

            # Active providers: same soft-delete check
            cur.execute(
                "SELECT COUNT(*) FROM providers WHERE archived_at IS NULL"
            )
            total_providers = cur.fetchone()[0]

            # Today's appointments: cast scheduled_at to a date and compare to today
            cur.execute(
                "SELECT COUNT(*) FROM appointments "
                "WHERE scheduled_at::date = CURRENT_DATE "
                "AND archived_at IS NULL"
            )
            appointments_today = cur.fetchone()[0]

    return {
        "total_patients": total_patients,
        "total_providers": total_providers,
        "appointments_today": appointments_today,
    }


# --- Health check endpoint ---
#
# A simple ping used to confirm the server is running.
# Useful for monitoring and for the React app to test connectivity.
@app.get("/health", tags=["System"])
def health_check():
    """Returns ok if the server is running."""
    return {"status": "ok"}
