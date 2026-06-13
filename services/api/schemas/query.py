"""Pydantic schemas for ad-hoc Q&A."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    client_id: UUID | None = None
    question: str = Field(min_length=3, max_length=2000)


class CitationResponse(BaseModel):
    clause_id: str
    source_url: str
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    confidence: float
    status: str
    disclaimer: str
