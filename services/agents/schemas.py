"""Pydantic contracts for the multi-agent pipeline (see AGENTS.md)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChangeEvent(BaseModel):
    document_id: str
    clause_id: str
    change_type: Literal["ADDED", "MODIFIED", "REMOVED"]
    severity: Literal["SUBSTANTIVE", "CRITICAL"]
    old_text: str | None = None
    new_text: str | None = None
    effective_date: date | None = None
    source: str
    change_summary: str | None = None


class AffectedProfile(BaseModel):
    client_id: str
    relevance_score: float
    hop_path: list[str]
    matched_categories: list[str]
    path_explanation: str | None = None


class Obligation(BaseModel):
    text: str
    deadline: date | None = None
    citation_clause_ids: list[str] = Field(default_factory=list)


class ImpactDraft(BaseModel):
    client_id: str
    summary: str
    obligations: list[Obligation] = Field(default_factory=list)
    retrieved_clause_ids: list[str] = Field(default_factory=list)
    reformulation_rounds: int = 0


class VerifiedImpact(BaseModel):
    client_id: str
    verified_obligations: list[Obligation] = Field(default_factory=list)
    confidence: float
    unsupported_claims_removed: list[str] = Field(default_factory=list)


class CitationRef(BaseModel):
    clause_id: str
    source_url: str
    excerpt: str


class ComplianceBrief(BaseModel):
    client_id: str
    title: str
    change_summary: str
    severity: str
    obligations: list[Obligation]
    recommended_actions: list[str]
    citations: list[CitationRef]
    confidence: float
    generated_at: datetime
    disclaimer: str
    status: Literal["COMPLETE", "LOW_CONFIDENCE", "NO_IMPACT"] = "COMPLETE"


class AgentTraceEntry(BaseModel):
    agent_name: str
    input_snapshot: dict[str, object]
    output_snapshot: dict[str, object]
    model_used: str
    prompt_version: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0


class PipelineRunResult(BaseModel):
    change_event_id: UUID | None = None
    brief_ids: list[UUID] = Field(default_factory=list)
    status: Literal["IN_PROGRESS", "COMPLETE", "LOW_CONFIDENCE", "NO_IMPACT"]
    briefs: list[ComplianceBrief] = Field(default_factory=list)
    trace: list[AgentTraceEntry] = Field(default_factory=list)
