"""Feedback endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.relevance_weights import adjust_weights_from_feedback
from services.api.db import get_db
from services.api.deps import AuthContext, get_auth_context, require_roles
from services.api.models import Brief, ClientProfile, Feedback
from services.api.schemas.briefs import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/api/v1/briefs", tags=["feedback"])


@router.post(
    "/{brief_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "consultant"))],
)
async def create_feedback(
    brief_id: uuid.UUID,
    body: FeedbackCreate,
    auth: AuthContext = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> Feedback:
    if auth.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")

    result = await db.execute(
        select(Brief)
        .join(ClientProfile, ClientProfile.id == Brief.client_id)
        .where(Brief.id == brief_id, ClientProfile.tenant_id == auth.tenant.id)
    )
    brief = result.scalar_one_or_none()
    if brief is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found")

    feedback = Feedback(
        id=uuid.uuid4(),
        brief_id=brief_id,
        user_id=auth.user.id,
        rating=body.rating,
        comment=body.comment,
        hop_path=body.hop_path,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    if body.rating == "NOT_RELEVANT":
        await adjust_weights_from_feedback(db, feedback_id=feedback.id)
    return feedback
