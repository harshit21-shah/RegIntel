"""Shared test fixtures."""

from __future__ import annotations

import os
import socket

import pytest

# Must be set before services.api.db is imported (NullPool for test isolation).
os.environ.setdefault("APP_ENV", "test")


@pytest.fixture(scope="session")
def postgres_available() -> bool:
    """TCP probe — avoids asyncio.run() poisoning TestClient's event loop on Windows."""
    for port in (5433, 5432):
        try:
            with socket.create_connection(("localhost", port), timeout=2):
                return True
        except OSError:
            continue
    return False
