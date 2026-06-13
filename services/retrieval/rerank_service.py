"""Pluggable reranking: heuristic, BGE cross-encoder, or Cohere API."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

import httpx

from services.api.config import Settings, get_settings
from services.retrieval.rerank import rerank_clauses as heuristic_rerank
from services.retrieval.types import RetrievedClause

logger = logging.getLogger(__name__)

COHERE_RERANK_URL = "https://api.cohere.ai/v1/rerank"
_bge_model: Any = None


def _load_bge_model() -> Any:
    global _bge_model
    if _bge_model is None:
        from sentence_transformers import CrossEncoder

        _bge_model = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _bge_model


def _apply_hop_boost(
    query: str,
    clauses: Sequence[RetrievedClause],
    *,
    top_k: int,
) -> list[RetrievedClause]:
    boosted: list[tuple[float, RetrievedClause]] = []
    for clause in clauses:
        hop_boost = 0.0
        if clause.hop_distance is not None:
            hop_boost = 0.15 * (1.0 / (1.0 + clause.hop_distance))
        boosted.append((clause.score + hop_boost, clause))
    boosted.sort(key=lambda item: item[0], reverse=True)
    return [
        RetrievedClause(
            clause_id=clause.clause_id,
            text=clause.text,
            score=round(score, 4),
            regulation_id=clause.regulation_id,
            source_url=clause.source_url,
            section_number=clause.section_number,
            title=clause.title,
            hop_distance=clause.hop_distance,
        )
        for score, clause in boosted[:top_k]
    ]


async def _cohere_rerank(
    query: str,
    clauses: Sequence[RetrievedClause],
    *,
    top_k: int,
    settings: Settings,
) -> list[RetrievedClause]:
    if not settings.cohere_api_key or not clauses:
        return heuristic_rerank(query, clauses, top_k=top_k)

    documents = [f"{clause.title or ''}\n{clause.text[:2000]}" for clause in clauses]
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            COHERE_RERANK_URL,
            headers={
                "Authorization": f"Bearer {settings.cohere_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "rerank-v3.5",
                "query": query,
                "documents": documents,
                "top_n": min(top_k, len(documents)),
            },
        )
        response.raise_for_status()
        results = response.json().get("results", [])

    reranked: list[RetrievedClause] = []
    for item in results:
        idx = int(item["index"])
        clause = clauses[idx]
        reranked.append(
            RetrievedClause(
                clause_id=clause.clause_id,
                text=clause.text,
                score=round(float(item.get("relevance_score", clause.score)), 4),
                regulation_id=clause.regulation_id,
                source_url=clause.source_url,
                section_number=clause.section_number,
                title=clause.title,
                hop_distance=clause.hop_distance,
            )
        )
    return reranked


def _bge_rerank(
    query: str,
    clauses: Sequence[RetrievedClause],
    *,
    top_k: int,
) -> list[RetrievedClause]:
    if not clauses:
        return []
    try:
        model = _load_bge_model()
        pairs = [(query, clause.text[:2000]) for clause in clauses]
        scores = model.predict(pairs)
        ranked = sorted(
            zip(scores, clauses, strict=True),
            key=lambda item: float(item[0]),
            reverse=True,
        )
        return [
            RetrievedClause(
                clause_id=clause.clause_id,
                text=clause.text,
                score=round(float(score), 4),
                regulation_id=clause.regulation_id,
                source_url=clause.source_url,
                section_number=clause.section_number,
                title=clause.title,
                hop_distance=clause.hop_distance,
            )
            for score, clause in ranked[:top_k]
        ]
    except Exception:
        logger.warning("BGE reranker unavailable; falling back to heuristic", exc_info=True)
        return heuristic_rerank(query, clauses, top_k=top_k)


async def rerank(
    query: str,
    clauses: Sequence[RetrievedClause],
    *,
    top_k: int = 5,
    settings: Settings | None = None,
) -> list[RetrievedClause]:
    settings = settings or get_settings()
    pool = list(clauses)[: settings.rerank_top_n]
    if not pool:
        return []

    provider = settings.reranker_provider.lower()
    if provider == "cohere":
        ranked = await _cohere_rerank(query, pool, top_k=top_k, settings=settings)
    elif provider == "bge":
        ranked = _bge_rerank(query, pool, top_k=top_k)
    else:
        ranked = heuristic_rerank(query, pool, top_k=top_k)

    return _apply_hop_boost(query, ranked, top_k=top_k)
