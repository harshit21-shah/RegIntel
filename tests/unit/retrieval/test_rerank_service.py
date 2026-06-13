"""Tests for rerank service providers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.api.config import Settings
from services.retrieval.rerank_service import rerank
from services.retrieval.types import RetrievedClause


@pytest.fixture
def sample_clauses() -> list[RetrievedClause]:
    return [
        RetrievedClause(
            clause_id="ecfr:21:101:101.1",
            text="principal display panel food package form label",
            score=0.7,
            regulation_id="21:101",
            source_url="https://example.com/101.1",
            section_number="101.1",
            title="Principal display panel",
        ),
        RetrievedClause(
            clause_id="ecfr:21:101:101.9",
            text="nutrition information relating to food",
            score=0.65,
            regulation_id="21:101",
            source_url="https://example.com/101.9",
            section_number="101.9",
            title="Nutrition labeling",
        ),
    ]


@pytest.mark.asyncio
async def test_heuristic_rerank_returns_top_k(sample_clauses: list[RetrievedClause]) -> None:
    settings = Settings(reranker_provider="heuristic")
    ranked = await rerank(
        "principal display panel requirements",
        sample_clauses,
        top_k=1,
        settings=settings,
    )
    assert len(ranked) == 1
    assert ranked[0].clause_id == "ecfr:21:101:101.1"


@pytest.mark.asyncio
async def test_cohere_rerank_uses_api(sample_clauses: list[RetrievedClause]) -> None:
    settings = Settings(reranker_provider="cohere", cohere_api_key="test-key")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "results": [{"index": 0, "relevance_score": 0.99}, {"index": 1, "relevance_score": 0.1}]
    }

    with patch("services.retrieval.rerank_service.httpx.AsyncClient") as client_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        client.post.return_value = mock_response
        client_cls.return_value = client

        ranked = await rerank("principal display panel", sample_clauses, top_k=1, settings=settings)

    assert ranked[0].clause_id == "ecfr:21:101:101.1"


@pytest.mark.asyncio
async def test_hop_distance_boost(sample_clauses: list[RetrievedClause]) -> None:
    settings = Settings(reranker_provider="heuristic")
    with_hop = [
        RetrievedClause(
            clause_id=sample_clauses[1].clause_id,
            text=sample_clauses[1].text,
            score=0.5,
            regulation_id=sample_clauses[1].regulation_id,
            source_url=sample_clauses[1].source_url,
            section_number=sample_clauses[1].section_number,
            title=sample_clauses[1].title,
            hop_distance=0,
        )
    ]
    ranked = await rerank("nutrition", with_hop, top_k=1, settings=settings)
    assert ranked[0].score >= 0.5
