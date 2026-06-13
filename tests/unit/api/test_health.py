"""Unit tests for the API service."""

from fastapi.testclient import TestClient

from services.api.main import app


def test_healthz_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_returns_service_info() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "regintel-api"
