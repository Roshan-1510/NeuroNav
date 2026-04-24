from __future__ import annotations

import os

from pymongo import MongoClient


DEFAULT_LOCAL_MONGO_URI = "mongodb://localhost:27017/neuronav"


def _env_int(name: str, default: int) -> int:
    """Read an integer env var with a safe default."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean env var with a safe default."""
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _build_client(uri: str, server_selection_timeout_ms: int, connect_timeout_ms: int, socket_timeout_ms: int) -> MongoClient:
    """Create a Mongo client with standardized options."""
    return MongoClient(
        uri,
        serverSelectionTimeoutMS=server_selection_timeout_ms,
        connectTimeoutMS=connect_timeout_ms,
        socketTimeoutMS=socket_timeout_ms,
        retryReads=True,
        retryWrites=True,
    )


def get_mongo_uri() -> str:
    """Return the configured Mongo URI or a local development fallback."""
    return os.getenv("MONGO_URI", DEFAULT_LOCAL_MONGO_URI)


def create_mongo_client() -> MongoClient:
    """
    Create a Mongo client with a safe fallback for local development.

    Atlas SRV URIs can fail during DNS resolution on restricted networks or
    when the machine is offline. In that case we fall back to a local MongoDB
    URI so the backend can still start and the UI can surface a clearer DB error
    later if the local server is not running.
    """
    mongo_uri = get_mongo_uri()
    allow_local_fallback = _env_bool("MONGO_ALLOW_LOCAL_FALLBACK", False)
    server_selection_timeout_ms = _env_int("MONGO_SERVER_SELECTION_TIMEOUT_MS", 12000)
    connect_timeout_ms = _env_int("MONGO_CONNECT_TIMEOUT_MS", 12000)
    socket_timeout_ms = _env_int("MONGO_SOCKET_TIMEOUT_MS", 15000)

    try:
        client = _build_client(mongo_uri, server_selection_timeout_ms, connect_timeout_ms, socket_timeout_ms)
        # Validate connectivity now so we don't silently run against an unexpected fallback.
        client.admin.command("ping")
        return client
    except Exception as primary_error:
        fallback_uri = DEFAULT_LOCAL_MONGO_URI
        if mongo_uri == fallback_uri or not allow_local_fallback:
            raise primary_error

        print(
            f"⚠️ Mongo URI failed to initialize ({primary_error}). "
            f"Falling back to local MongoDB at {fallback_uri}."
        )

        fallback_client = _build_client(fallback_uri, server_selection_timeout_ms, connect_timeout_ms, socket_timeout_ms)
        fallback_client.admin.command("ping")
        return fallback_client