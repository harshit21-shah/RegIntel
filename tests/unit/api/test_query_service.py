"""Tests for query citation helpers."""

from services.api.schemas.query import CitationResponse
from services.api.services.query import (
    CITATION_TAG_RE,
    _estimate_confidence,
    _extract_citations,
)
from services.retrieval.types import RetrievedClause


def test_citation_tag_regex() -> None:
    answer = (
        "Labels must identify the PDP [ecfr:21:101:101.1] "
        "and list ingredients [ecfr:21:101:101.4:b]."
    )
    assert CITATION_TAG_RE.findall(answer) == ["ecfr:21:101:101.1", "ecfr:21:101:101.4:b"]


def test_extract_citations_maps_to_retrieved_clauses() -> None:
    retrieved = [
        RetrievedClause(
            clause_id="ecfr:21:101:101.1",
            text="Principal display panel text",
            score=0.9,
            regulation_id="ecfr-21-101",
            source_url="https://example.com/101.1",
            section_number="101.1",
            title="Principal display panel",
        )
    ]
    answer = "The principal display panel is defined in [ecfr:21:101:101.1]."
    citations = _extract_citations(answer, retrieved)
    assert len(citations) == 1
    assert citations[0] == CitationResponse(
        clause_id="ecfr:21:101:101.1",
        source_url="https://example.com/101.1",
        excerpt="Principal display panel text",
    )


def test_estimate_confidence_requires_citations_and_retrieval() -> None:
    retrieved = [
        RetrievedClause(
            clause_id="ecfr:21:101:101.1",
            text="text",
            score=0.8,
            regulation_id="ecfr-21-101",
            source_url="https://example.com",
            section_number="101.1",
            title=None,
        )
    ]
    confident = _estimate_confidence("See [ecfr:21:101:101.1].", retrieved)
    low = _estimate_confidence("No citations here.", retrieved)
    assert confident > low
    assert confident >= 0.55


def test_estimate_confidence_not_penalized_for_extra_retrieval() -> None:
    """One valid citation should not be downgraded because top_k returned extra clauses."""
    retrieved = [
        RetrievedClause(
            clause_id="ref:fda:glossary:overview",
            text="FDA overview",
            score=0.75,
            regulation_id="reference-corpus",
            source_url="https://fda.gov",
            section_number="overview",
            title="FDA reference",
        ),
        RetrievedClause(
            clause_id="ref:sec:glossary:filings",
            text="SEC filings",
            score=0.4,
            regulation_id="reference-corpus",
            source_url="https://sec.gov",
            section_number="filings",
            title="SEC reference",
        ),
    ]
    answer = "The FDA regulates drugs and food [ref:fda:glossary:overview]."
    confidence = _estimate_confidence(answer, retrieved)
    assert confidence >= 0.55
