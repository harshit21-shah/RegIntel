"""Regulatory changes feed endpoints."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_db
from services.api.deps import AuthContext, enforce_bulk_rate_limit
from services.api.models import Brief, ChangeEvent, ClientProfile
from services.api.schemas.briefs import ChangeListResponse, ChangeSummary
from services.graph.sync_profiles import sync_client_profile

router = APIRouter(prefix="/api/v1/changes", tags=["changes"])

SOURCE_JURISDICTION = {
    "ecfr": "US",
    "federal_register": "US",
    "ca_food_code": "CA",
    "sec_edgar": "US",
}


@router.get("", response_model=ChangeListResponse)
async def list_changes(
    source: str | None = None,
    severity: str | None = None,
    jurisdiction: str | None = None,
    since: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _auth: AuthContext = Depends(enforce_bulk_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> ChangeListResponse:
    query = select(ChangeEvent)
    if source:
        query = query.where(ChangeEvent.source == source)
    if severity:
        query = query.where(ChangeEvent.severity == severity)
    if since:
        query = query.where(ChangeEvent.detected_at >= datetime.combine(since, datetime.min.time()))
    if jurisdiction:
        matching_sources = [
            key for key, value in SOURCE_JURISDICTION.items() if value == jurisdiction.upper()
        ]
        if matching_sources:
            query = query.where(ChangeEvent.source.in_(matching_sources))
        else:
            query = query.where(ChangeEvent.source == "__none__")

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(ChangeEvent.detected_at.desc()).offset(offset).limit(page_size)
    )
    items = result.scalars().all()

    summaries: list[ChangeSummary] = []
    for item in items:
        summaries.append(await _change_summary(db, item))

    return ChangeListResponse(
        items=summaries, page=page, page_size=page_size, total=int(total or 0)
    )


async def _change_summary(db: AsyncSession, item: ChangeEvent) -> ChangeSummary:
    affected_count = int(
        await db.scalar(
            select(func.count()).select_from(Brief).where(Brief.change_event_id == item.id)
        )
        or 0
    )
    return ChangeSummary(
        change_id=item.id,
        document_id=item.document_id,
        clause_id=item.clause_id,
        change_type=item.change_type,
        severity=item.severity,
        summary=item.new_text[:200] if item.new_text else None,
        detected_at=item.detected_at,
        affected_client_count=affected_count,
    )


@router.get("/{change_id}", response_model=ChangeSummary)
async def get_change(
    change_id: uuid.UUID,
    _auth: AuthContext = Depends(enforce_bulk_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> ChangeSummary:
    result = await db.execute(select(ChangeEvent).where(ChangeEvent.id == change_id))
    change = result.scalar_one_or_none()
    if change is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found")
    return await _change_summary(db, change)


@router.get("/{change_id}/affected-profiles")
async def affected_profiles(
    change_id: uuid.UUID,
    auth: AuthContext = Depends(enforce_bulk_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[dict[str, object]]]:
    result = await db.execute(select(ChangeEvent).where(ChangeEvent.id == change_id))
    change = result.scalar_one_or_none()
    if change is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found")

    profiles_result = await db.execute(
        select(ClientProfile).where(ClientProfile.tenant_id == auth.tenant.id)
    )
    profiles = profiles_result.scalars().all()
    for profile in profiles:
        await sync_client_profile(profile)

    from services.agents.relevance import run_relevance_agent
    from services.agents.schemas import ChangeEvent as AgentChangeEvent

    event = AgentChangeEvent(
        document_id=change.document_id,
        clause_id=change.clause_id,
        change_type=change.change_type,
        severity=change.severity,
        old_text=change.old_text,
        new_text=change.new_text,
        effective_date=change.effective_date,
        source=change.source,
    )
    affected, _ = await run_relevance_agent(event, llm=None, db=db)
    tenant_client_ids = {str(p.id) for p in profiles}
    filtered = [profile for profile in affected if profile.client_id in tenant_client_ids]
    return {"items": [profile.model_dump(mode="json") for profile in filtered]}
