"""Multi-tenant consultant triage endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.relevance import run_relevance_agent
from services.agents.schemas import ChangeEvent as AgentChangeEvent
from services.api.db import get_db
from services.api.deps import AuthContext, get_auth_context, require_roles
from services.api.models import Brief, ChangeEvent, ClientProfile
from services.api.schemas.briefs import BriefSummary
from services.api.schemas.consultant import ClientTriageItem, ConsultantDashboard

router = APIRouter(
    prefix="/api/v1/consultant",
    tags=["consultant"],
    dependencies=[Depends(require_roles("admin", "consultant"))],
)


@router.get("/dashboard", response_model=ConsultantDashboard)
async def consultant_dashboard(
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ConsultantDashboard:
    tenant = auth.tenant
    profiles_result = await db.execute(
        select(ClientProfile).where(ClientProfile.tenant_id == tenant.id)
    )
    profiles = profiles_result.scalars().all()
    profile_ids = [profile.id for profile in profiles]

    briefs: list[Brief] = []
    low_confidence = 0
    if profile_ids:
        briefs_result = await db.execute(
            select(Brief)
            .where(Brief.client_id.in_(profile_ids))
            .order_by(Brief.generated_at.desc())
            .limit(20)
        )
        briefs = list(briefs_result.scalars().all())
        low_confidence = int(
            await db.scalar(
                select(func.count())
                .select_from(Brief)
                .where(Brief.client_id.in_(profile_ids), Brief.status == "LOW_CONFIDENCE")
            )
            or 0
        )

    changes_count = await db.scalar(select(func.count()).select_from(ChangeEvent))

    return ConsultantDashboard(
        tenant_id=tenant.id,
        client_count=len(profiles),
        recent_briefs=[
            BriefSummary(
                brief_id=b.id,
                client_id=b.client_id,
                title=b.title,
                severity=b.severity,
                confidence=float(b.confidence),
                generated_at=b.generated_at,
                status=b.status,
            )
            for b in briefs
        ],
        total_changes=int(changes_count or 0),
        low_confidence_briefs=low_confidence,
    )


@router.get("/changes/{change_id}/triage")
async def consultant_triage(
    change_id: uuid.UUID,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[dict[str, object]]]:
    change_result = await db.execute(select(ChangeEvent).where(ChangeEvent.id == change_id))
    change = change_result.scalar_one_or_none()
    if change is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found")

    profiles_result = await db.execute(
        select(ClientProfile).where(ClientProfile.tenant_id == auth.tenant.id)
    )
    tenant_client_ids = {str(p.id) for p in profiles_result.scalars().all()}

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
    items = [
        ClientTriageItem(
            client_id=uuid.UUID(profile.client_id),
            relevance_score=profile.relevance_score,
            hop_path=profile.hop_path,
            matched_categories=profile.matched_categories,
        ).model_dump(mode="json")
        for profile in affected
        if profile.client_id in tenant_client_ids
    ]
    return {"items": items}
