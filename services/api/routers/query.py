"""Ad-hoc Q&A endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.db import get_db
from services.api.deps import AuthContext, enforce_query_rate_limit
from services.api.schemas.query import QueryRequest, QueryResponse
from services.api.services.query import QueryService

router = APIRouter(prefix="/api/v1", tags=["query"])
_service = QueryService()


@router.post("/query", response_model=QueryResponse)
async def query_regulations(
    body: QueryRequest,
    request: Request,
    auth: AuthContext = Depends(enforce_query_rate_limit),
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    return await _service.answer(
        question=body.question,
        client_id=body.client_id,
        tenant_id=auth.tenant.id,
        db=db,
        request_id=getattr(request.state, "request_id", None),
    )
