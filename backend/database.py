"""
database.py - Database connection management for the FastAPI backend.

This module owns one thing: the connection pool.

A connection pool keeps a set of open database connections ready to use.
Instead of opening and closing a connection on every HTTP request (slow),
the pool lends out an existing connection and takes it back when done (fast).

The pool is created once when the FastAPI app starts (via the lifespan in main.py)
and shut down cleanly when the app stops.

Usage in a route handler:
    with database.get_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT ...")
"""

import os
from typing import Optional
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

# Load environment variables from the .env file at the project root.
load_dotenv()

# Read the DATABASE_URL that was set up in Session 2.
# The .env value is formatted for SQLAlchemy / Alembic: postgresql+psycopg://...
# psycopg3 (used directly here) expects the standard format: postgresql://...
# We strip the "+psycopg" driver suffix before handing it to the pool.
_raw_url = os.environ["DATABASE_URL"]
DATABASE_URL = _raw_url.replace("postgresql+psycopg://", "postgresql://")

# The pool starts as None and is assigned in main.py during app startup.
# Keeping it here (rather than in main.py) makes it importable by all routers.
# Optional is used here instead of "ConnectionPool | None" because this project
# runs on Python 3.9, which does not support the X | Y union syntax for type hints.
pool: Optional[ConnectionPool] = None


def get_pool() -> ConnectionPool:
    """
    Return the active connection pool.

    All route handlers call this to get a connection.
    Raises RuntimeError if called before the app has started
    (which should never happen in normal use).
    """
    if pool is None:
        raise RuntimeError(
            "Connection pool has not been initialized. "
            "Make sure the FastAPI app is running via uvicorn."
        )
    return pool
