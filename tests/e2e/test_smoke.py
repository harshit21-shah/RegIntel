"""E2E smoke tests against a deployed environment or local TestClient."""

from __future__ import annotations

import os

import httpx
import pytest
from fastapi.testclient import TestClient

from services.api.main import app


@pytest.fixture
def base_url() -> str:
    return os.environ.get("E2E_BASE_URL", "").rstrip("/")


@pytest.fixture
def client(base_url: str) -> httpx.Client | TestClient:
    if base_url:
        return httpx.Client(base_url=base_url, timeout=30.0)
    return TestClient(app)


def test_healthz(client: httpx.Client | TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root(client: httpx.Client | TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "regintel-api"


def test_openapi_docs(client: httpx.Client | TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
