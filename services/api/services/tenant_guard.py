"""Tenant-scoped resource access guards."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.exceptions import NotFoundError
from services.api.models import Brief, ClientProfile


async def get_tenant_profile(
    db: AsyncSession,
    *,
    client_id: uuid.UUID,
    tenant_id: uuid.UUID,
    request_id: str | None = None,
) -> ClientProfile:
    result = await db.execute(
        select(ClientProfile).where(
            ClientProfile.id == client_id,
            ClientProfile.tenant_id == tenant_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise NotFoundError("Client profile not found", request_id=request_id)
    return profile


async def assert_brief_accessible(
    db: AsyncSession,
    *,
    brief_id: uuid.UUID,
    tenant_id: uuid.UUID,
    request_id: str | None = None,
) -> None:
    result = await db.execute(
        select(Brief)
        .join(ClientProfile, ClientProfile.id == Brief.client_id)
        .where(Brief.id == brief_id, ClientProfile.tenant_id == tenant_id)
    )
    if result.scalar_one_or_none() is None:
        raise NotFoundError("Brief not found", request_id=request_id)
