"""Pydantic models for the ingestion pipeline."""

from __future__ import annotations

from datetime import UTC, date, datetime

from pydantic import BaseModel, Field


class DocumentRef(BaseModel):
    source_id: str
    document_id: str
    title: str
    published_at: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class RawDocument(BaseModel):
    ref: DocumentRef
    content: str
    content_type: str = "text/markdown"
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))


class ParsedClause(BaseModel):
    clause_id: str
    text: str
    parent_id: str | None = None
    section_number: str
    title: str | None = None


class ParsedDocument(BaseModel):
    document_id: str
    source: str
    title: str
    regulation_id: str
    agency: str = "FDA"
    jurisdiction: str = "US"
    effective_date: date
    version_hash: str
    clauses: list[ParsedClause]
