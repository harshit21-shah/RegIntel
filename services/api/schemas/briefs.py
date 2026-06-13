"""Pydantic schemas for briefs, changes, and feedback."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BriefSummary(BaseModel):
    brief_id: UUID = Field(alias="id")
    client_id: UUID
    title: str
    severity: str
    confidence: float
    generated_at: datetime
    status: str

    model_config = {"from_attributes": True, "populate_by_name": True}


class BriefListResponse(BaseModel):
    items: list[BriefSummary]
    page: int
    page_size: int
    total: int


class CitationDetail(BaseModel):
    clause_id: str
    source_url: str
    excerpt: str


class AgentTraceSummary(BaseModel):
    agent_name: str
    model_used: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


class BriefDetail(BaseModel):
    brief_id: UUID = Field(alias="id")
    client_id: UUID
    title: str
    change_summary: str
    severity: str
    obligations: list[dict[str, object]]
    recommended_actions: list[str]
    citations: list[CitationDetail]
    confidence: float
    generated_at: datetime
    status: str
    disclaimer: str
    agent_trace: list[AgentTraceSummary] = Field(default_factory=list)

    model_config = {"from_attributes": True, "populate_by_name": True}


class ChangeSummary(BaseModel):
    change_id: UUID = Field(alias="id")
    document_id: str
    clause_id: str
    change_type: str
    severity: str
    summary: str | None = None
    detected_at: datetime
    affected_client_count: int = 0

    model_config = {"from_attributes": True, "populate_by_name": True}


class ChangeListResponse(BaseModel):
    items: list[ChangeSummary]
    page: int
    page_size: int
    total: int


class FeedbackCreate(BaseModel):
    rating: str = Field(pattern="^(HELPFUL|NOT_RELEVANT|INACCURATE)$")
    comment: str | None = Field(default=None, max_length=2000)
    hop_path: list[str] | None = None


class FeedbackResponse(BaseModel):
    feedback_id: UUID = Field(alias="id")
    brief_id: UUID
    rating: str
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}
