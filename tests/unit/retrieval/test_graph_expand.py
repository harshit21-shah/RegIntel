"""Tests for graph-guided retrieval expansion."""

from __future__ import annotations

from services.retrieval.graph_expand import merge_retrieved
from services.retrieval.types import RetrievedClause


def test_merge_retrieved_deduplicates_by_clause_id() -> None:
    a = RetrievedClause(
        clause_id="x",
        text="a",
        score=0.5,
        regulation_id="r",
        source_url="u",
        section_number="1",
        title=None,
    )
    b = RetrievedClause(
        clause_id="x",
        text="a",
        score=0.9,
        regulation_id="r",
        source_url="u",
        section_number="1",
        title=None,
        hop_distance=1,
    )
    merged = merge_retrieved([a], [b])
    assert len(merged) == 1
    assert merged[0].score == 0.9
