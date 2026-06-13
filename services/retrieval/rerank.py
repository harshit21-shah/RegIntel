"""Keyword + score fusion reranking for improved citation precision."""

from __future__ import annotations

import re
from collections.abc import Sequence

from services.retrieval.types import RetrievedClause

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _query_tokens(query: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(query.lower()) if len(token) > 2}


def rerank_clauses(
    query: str,
    clauses: Sequence[RetrievedClause],
    *,
    top_k: int = 5,
) -> list[RetrievedClause]:
    if not clauses:
        return []
    tokens = _query_tokens(query)
    scored: list[tuple[float, RetrievedClause]] = []

    for clause in clauses:
        clause_tokens = _query_tokens(clause.text)
        overlap = len(tokens & clause_tokens)
        keyword_score = overlap / max(1, len(tokens))
        title_boost = (
            0.1 if clause.title and any(t in clause.title.lower() for t in tokens) else 0.0
        )
        combined = (clause.score * 0.55) + (keyword_score * 0.35) + title_boost
        scored.append((combined, clause))

    scored.sort(key=lambda item: item[0], reverse=True)
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
        for score, clause in scored[:top_k]
    ]
