"""Production hardening tests: errors, rate limits, tenant guards."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from services.api.exceptions import RateLimitError
from services.api.main import app
from services.api.services.rate_limit import check_rate_limit

client = TestClient(app)


def test_validation_error_format() -> None:
    response = client.post("/api/v1/auth/login", json={"email": "bad", "password": "short"})
    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in body["error"]
    assert response.headers.get("X-Request-Id")


def test_not_found_profile(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")
    response = client.get(f"/api/v1/profiles/{uuid.uuid4()}")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_rate_limit_blocks_excess_requests() -> None:
    tenant = str(uuid.uuid4())
    limit = 3
    for _ in range(limit):
        await check_rate_limit(tenant_id=tenant, bucket="test", limit=limit)
    with pytest.raises(RateLimitError):
        await check_rate_limit(tenant_id=tenant, bucket="test", limit=limit)


def test_healthz_has_request_id() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.headers.get("X-Request-Id")


def test_query_requires_min_question_length(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")
    response = client.post("/api/v1/query", json={"question": "ab"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_security_headers_present() -> None:
    response = client.get("/healthz")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
