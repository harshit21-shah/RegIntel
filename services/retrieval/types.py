"""Shared retrieval types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedClause:
    clause_id: str
    text: str
    score: float
    regulation_id: str
    source_url: str
    section_number: str
    title: str | None
    hop_distance: int | None = None
