"""Consultant view schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from services.api.schemas.briefs import BriefSummary


class ConsultantDashboard(BaseModel):
    tenant_id: UUID
    client_count: int
    recent_briefs: list[BriefSummary]
    total_changes: int
    low_confidence_briefs: int


class ClientTriageItem(BaseModel):
    client_id: UUID
    relevance_score: float
    hop_path: list[str]
    matched_categories: list[str]
