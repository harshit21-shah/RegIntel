"""Brief list and detail endpoints."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.api.db import get_db
from services.api.deps import AuthContext, enforce_bulk_rate_limit
from services.api.models import AgentTrace, Brief, ClientProfile
from services.api.schemas.briefs import (
    AgentTraceSummary,
    BriefDetail,
    BriefListResponse,
    BriefSummary,
    CitationDetail,
)

router = APIRouter(prefix="/api/v1/briefs", tags=["briefs"])


def _tenant_brief_query(tenant_id: uuid.UUID) -> Select[tuple[Brief]]:
    return (
        select(Brief)
        .join(ClientProfile, ClientProfile.id == Brief.client_id)
        .where(ClientProfile.tenant_id == tenant_id)
    )


@router.get("", response_model=BriefListResponse)
async def list_briefs(
    client_id: uuid.UUID | None = None,
    severity: str | None = None,
    brief_status: str | None = Query(default=None, alias="status"),
    since: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    auth: AuthContext = Depends(enforce_bulk_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> BriefListResponse:
    query = _tenant_brief_query(auth.tenant.id)
    if client_id:
        query = query.where(Brief.client_id == client_id)
    if severity:
        query = query.where(Brief.severity == severity)
    if brief_status:
        query = query.where(Brief.status == brief_status)
    if since:
        query = query.where(Brief.generated_at >= datetime.combine(since, datetime.min.time()))

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Brief.generated_at.desc()).offset(offset).limit(page_size)
    )
    items = result.scalars().all()
    return BriefListResponse(
        items=[
            BriefSummary(
                brief_id=item.id,
                client_id=item.client_id,
                title=item.title,
                severity=item.severity,
                confidence=float(item.confidence),
                generated_at=item.generated_at,
                status=item.status,
            )
            for item in items
        ],
        page=page,
        page_size=page_size,
        total=int(total or 0),
    )


@router.get("/{brief_id}", response_model=BriefDetail)
async def get_brief(
    brief_id: uuid.UUID,
    auth: AuthContext = Depends(enforce_bulk_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> BriefDetail:
    result = await db.execute(
        select(Brief)
        .join(ClientProfile, ClientProfile.id == Brief.client_id)
        .options(selectinload(Brief.citations))
        .where(Brief.id == brief_id, ClientProfile.tenant_id == auth.tenant.id)
    )
    brief = result.scalar_one_or_none()
    if brief is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found")

    trace_result = await db.execute(
        select(AgentTrace)
        .where(AgentTrace.change_event_id == brief.change_event_id)
        .order_by(AgentTrace.created_at.asc())
    )
    traces = [
        AgentTraceSummary(
            agent_name=row.agent_name,
            model_used=row.model_used,
            tokens_in=row.tokens_in,
            tokens_out=row.tokens_out,
            latency_ms=row.latency_ms,
        )
        for row in trace_result.scalars().all()
    ]

    return BriefDetail(
        brief_id=brief.id,
        client_id=brief.client_id,
        title=brief.title,
        change_summary=brief.change_summary,
        severity=brief.severity,
        obligations=brief.obligations,
        recommended_actions=brief.recommended_actions,
        citations=[
            CitationDetail(
                clause_id=c.clause_id,
                source_url=c.source_url,
                excerpt=c.excerpt,
            )
            for c in brief.citations
        ],
        confidence=float(brief.confidence),
        generated_at=brief.generated_at,
        status=brief.status,
        disclaimer=brief.disclaimer,
        agent_trace=traces,
    )
