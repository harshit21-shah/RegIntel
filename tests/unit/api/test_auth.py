"""Auth endpoint tests."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from services.api.auth.jwt import create_access_token, decode_token
from services.api.auth.passwords import hash_password, verify_password
from services.api.main import app

client = TestClient(app)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("secure-password-123")
    assert verify_password("secure-password-123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_jwt_access_token_roundtrip() -> None:
    user_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        role="consultant",
        email="test@example.com",
    )
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["type"] == "access"


def test_register_and_login_flow(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")
    email = f"user-{uuid.uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secure-password-123",
            "tenant_name": "Test Tenant",
            "role": "consultant",
        },
    )
    assert register.status_code == 201
    token_payload = register.json()
    assert token_payload["token_type"] == "bearer"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secure-password-123"},
    )
    assert login.status_code == 200
    access = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


def test_admin_requires_role(postgres_available: bool) -> None:
    if not postgres_available:
        pytest.skip("Postgres not available")
    email = f"viewer-{uuid.uuid4()}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secure-password-123",
            "tenant_name": "Viewer Tenant",
            "role": "viewer",
        },
    )
    access = register.json()["access_token"]
    response = client.get(
        "/api/v1/admin/cost/summary",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 403
