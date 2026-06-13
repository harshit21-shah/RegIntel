"""JWT creation and validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from services.api.config import Settings, get_settings

TokenType = str


def _settings() -> Settings:
    return get_settings()


def create_access_token(
    *,
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    email: str,
) -> str:
    settings = _settings()
    expire = datetime.now(tz=UTC) + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "email": email,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(*, user_id: UUID, tenant_id: UUID) -> str:
    settings = _settings()
    expire = datetime.now(tz=UTC) + timedelta(days=settings.jwt_refresh_expire_days)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = _settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
