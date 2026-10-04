"""
Supabase (Postgres) checkpointer wiring for the trial-eligibility graph.

Why a durable checkpointer matters here:
  - Supports Human-In-The-Loop (HITL) escalations and interrupt-driven resupply.
  - Pauses execution and persists thread state across restarts.
  - Automatically falls back to MemorySaver when database URIs are unset.
"""

import os
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from dotenv import find_dotenv, load_dotenv
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

# Ensure .env is resolved regardless of run location
load_dotenv(find_dotenv(usecwd=True))
_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")

# Checked in order of preference
DB_URI_ENV_KEYS = [
    "SUPABASE_DB_URI",
    "DATABASE_URL",
    "POSTGRES_URL",
    "SUPABASE_POSTGRES_URL",
]

# Prepared statements disabled for PgBouncer / Transaction pooler compatibility
_CONNECTION_KWARGS: Dict[str, Any] = {
    "autocommit": True,
    "prepare_threshold": None,
}


def _get_db_uri() -> Optional[str]:
    for key in DB_URI_ENV_KEYS:
        val = os.environ.get(key)
        if val and val.strip():
            uri = val.strip()
            # Standardize postgresql driver prefix for psycopg v3
            if uri.startswith("postgres://"):
                uri = uri.replace("postgres://", "postgresql://", 1)
            # Ensure sslmode is required for Supabase hosted databases (.co or .com)
            if ("supabase.co" in uri or "supabase.com" in uri) and "sslmode" not in uri:
                sep = "&" if "?" in uri else "?"
                uri = f"{uri}{sep}sslmode=require"
            return uri
    return None


def build_connection_pool(min_size: int = 1, max_size: int = 10):
    """Creates a psycopg connection pool connected to Supabase Postgres."""
    from psycopg_pool import ConnectionPool

    uri = _get_db_uri()
    if not uri:
        raise RuntimeError("Cannot initialize connection pool: No database URI environment variable is set.")

    return ConnectionPool(
        conninfo=uri,
        min_size=min_size,
        max_size=max_size,
        kwargs=_CONNECTION_KWARGS,
        open=True,
    )


def build_async_connection_pool(min_size: int = 1, max_size: int = 10):
    """Creates an async psycopg connection pool connected to Supabase Postgres."""
    from psycopg_pool import AsyncConnectionPool

    uri = _get_db_uri()
    if not uri:
        raise RuntimeError("Cannot initialize async connection pool: No database URI environment variable is set.")

    return AsyncConnectionPool(
        conninfo=uri,
        min_size=min_size,
        max_size=max_size,
        kwargs=_CONNECTION_KWARGS,
        open=False,
    )


@contextmanager
def supabase_checkpointer(min_size: int = 1, max_size: int = 10) -> Iterator[BaseCheckpointSaver]:
    """
    Synchronous checkpointer context manager.
    Yields PostgresSaver if a database URI is present, otherwise falls back to MemorySaver.
    """
    uri = _get_db_uri()
    if not uri:
        print("[Checkpointer Notice] No database URI configured. Falling back to in-memory checkpointer.")
        yield MemorySaver()
        return

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
    except ImportError:
        print("[Checkpointer Warning] langgraph-checkpoint-postgres not installed. Falling back to MemorySaver.")
        yield MemorySaver()
        return

    pool = None
    try:
        pool = build_connection_pool(min_size=min_size, max_size=max_size)
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()  # Idempotent table setup for checkpoints
        yield checkpointer
    except Exception as exc:
        print(f"[Checkpointer Warning] Failed connecting to Postgres ({exc}). Falling back to MemorySaver.")
        yield MemorySaver()
    finally:
        if pool is not None:
            pool.close()


@asynccontextmanager
async def async_supabase_checkpointer(min_size: int = 1, max_size: int = 10) -> AsyncIterator[BaseCheckpointSaver]:
    """
    Asynchronous checkpointer context manager for FastAPI / ASGI streaming routes.
    """
    uri = _get_db_uri()
    if not uri:
        print("[Checkpointer Notice] No database URI configured. Falling back to in-memory checkpointer.")
        yield MemorySaver()
        return

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    except ImportError:
        print("[Checkpointer Warning] langgraph-checkpoint-postgres not installed. Falling back to MemorySaver.")
        yield MemorySaver()
        return

    pool = None
    try:
        pool = build_async_connection_pool(min_size=min_size, max_size=max_size)
        await pool.open()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.asetup()  # Idempotent table setup for checkpoints
        yield checkpointer
    except Exception as exc:
        print(f"[Checkpointer Warning] Failed connecting to async Postgres ({exc}). Falling back to MemorySaver.")
        yield MemorySaver()
    finally:
        if pool is not None:
            await pool.close()


# ---------------------------------------------------------------------------
# Global Singleton Helpers (Safe for long-running FastAPI/Orchestrator lifecycles)
# ---------------------------------------------------------------------------
_GLOBAL_SYNC_CHECKPOINTER: Optional[BaseCheckpointSaver] = None
_GLOBAL_POOL: Optional[Any] = None


def get_default_checkpointer() -> BaseCheckpointSaver:
    """
    Returns a persistent singleton checkpointer instance for graph compilation.
    Initializes a PostgresSaver pool if credentials exist, otherwise returns a shared MemorySaver.
    """
    global _GLOBAL_SYNC_CHECKPOINTER, _GLOBAL_POOL
    if _GLOBAL_SYNC_CHECKPOINTER is not None:
        return _GLOBAL_SYNC_CHECKPOINTER

    uri = _get_db_uri()
    if not uri:
        print("[Checkpointer Notice] No database URI set in env. Using shared MemorySaver.")
        _GLOBAL_SYNC_CHECKPOINTER = MemorySaver()
        return _GLOBAL_SYNC_CHECKPOINTER

    try:
        from langgraph.checkpoint.postgres import PostgresSaver

        _GLOBAL_POOL = build_connection_pool(min_size=1, max_size=5)
        checkpointer = PostgresSaver(_GLOBAL_POOL)
        checkpointer.setup()
        _GLOBAL_SYNC_CHECKPOINTER = checkpointer
        return _GLOBAL_SYNC_CHECKPOINTER
    except Exception as exc:
        print(f"[Checkpointer Warning] Failed to connect to Postgres ({exc}). Falling back to MemorySaver.")
        _GLOBAL_SYNC_CHECKPOINTER = MemorySaver()
        return _GLOBAL_SYNC_CHECKPOINTER