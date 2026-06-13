"""Client profile CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_db
from services.api.deps import AuthContext, get_auth_context, require_roles
from services.api.models import ClientProfile
from services.api.schemas.profiles import (
    ProfileCreate,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdate,
)
from services.api.services.sqs_queue import enqueue_relevance_recheck
from services.graph.sync_profiles import sync_client_profile

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "consultant"))],
)
async def create_profile(
    body: ProfileCreate,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ClientProfile:
    profile = ClientProfile(
        id=uuid.uuid4(),
        tenant_id=auth.tenant.id,
        name=body.name,
        naics_codes=body.naics_codes,
        states_of_operation=body.states_of_operation,
        product_categories=body.product_categories,
        supply_chain_jurisdictions=body.supply_chain_jurisdictions,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    await sync_client_profile(profile)
    return profile


@router.get("", response_model=ProfileListResponse)
async def list_profiles(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ProfileListResponse:
    offset = (page - 1) * page_size
    total = await db.scalar(
        select(func.count())
        .select_from(ClientProfile)
        .where(ClientProfile.tenant_id == auth.tenant.id)
    )
    result = await db.execute(
        select(ClientProfile)
        .where(ClientProfile.tenant_id == auth.tenant.id)
        .order_by(ClientProfile.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()
    return ProfileListResponse(
        items=[ProfileResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=int(total or 0),
    )


@router.get("/{client_id}", response_model=ProfileResponse)
async def get_profile(
    client_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ClientProfile:
    result = await db.execute(
        select(ClientProfile).where(
            ClientProfile.id == client_id,
            ClientProfile.tenant_id == auth.tenant.id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.patch(
    "/{client_id}",
    response_model=ProfileResponse,
    dependencies=[Depends(require_roles("admin", "consultant"))],
)
async def update_profile(
    client_id: uuid.UUID,
    body: ProfileUpdate,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ClientProfile:
    result = await db.execute(
        select(ClientProfile).where(
            ClientProfile.id == client_id,
            ClientProfile.tenant_id == auth.tenant.id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    await sync_client_profile(profile)
    enqueue_relevance_recheck(client_id=profile.id, tenant_id=auth.tenant.id)
    return profile
