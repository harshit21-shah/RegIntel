"""Changes endpoint tests."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from services.api.main import app

client = TestClient(app)


def test_get_change_not_found(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")
    response = client.get(f"/api/v1/changes/{uuid.uuid4()}")
    assert response.status_code == 404
