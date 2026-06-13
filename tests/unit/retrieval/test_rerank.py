"""Tests for retrieval reranking."""

from services.retrieval.rerank import rerank_clauses
from services.retrieval.types import RetrievedClause


def _clause(clause_id: str, text: str, score: float) -> RetrievedClause:
    return RetrievedClause(
        clause_id=clause_id,
        text=text,
        score=score,
        regulation_id="ecfr-21-101",
        source_url="https://example.com",
        section_number="101.1",
        title="Food labeling",
    )


def test_rerank_prefers_keyword_overlap() -> None:
    query = "principal display panel mandatory label information"
    clauses = [
        _clause("a", "unrelated environmental regulation text", 0.9),
        _clause("b", "principal display panel mandatory label information clarity", 0.6),
    ]
    ranked = rerank_clauses(query, clauses, top_k=1)
    assert ranked[0].clause_id == "b"
