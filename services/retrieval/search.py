"""Hybrid dense+sparse retrieval over Qdrant clause collection."""

from __future__ import annotations

import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import FieldCondition, Filter, Fusion, FusionQuery, MatchValue, Prefetch

from services.api.config import Settings, get_settings
from services.retrieval.embeddings import EmbeddingService
from services.retrieval.rerank_service import rerank
from services.retrieval.types import RetrievedClause

logger = logging.getLogger(__name__)


class ClauseRetriever:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.embedder = EmbeddingService(self.settings)

    async def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        jurisdiction: str | None = "US",
        regulation_id: str | None = None,
        seed_clause_ids: tuple[str, ...] = (),
    ) -> list[RetrievedClause]:
        dense_vectors = await self.embedder.embed_texts([query])
        sparse_indices, sparse_values = (await self.embedder.embed_sparse([query]))[0]

        filter_conditions: list[FieldCondition] = []
        if jurisdiction:
            filter_conditions.append(
                FieldCondition(key="jurisdiction", match=MatchValue(value=jurisdiction))
            )
        if regulation_id:
            filter_conditions.append(
                FieldCondition(key="regulation_id", match=MatchValue(value=regulation_id))
            )
        query_filter = Filter(must=filter_conditions) if filter_conditions else None

        client = AsyncQdrantClient(url=self.settings.qdrant_url)
        try:
            results = await client.query_points(
                collection_name=self.settings.qdrant_collection,
                prefetch=[
                    Prefetch(query=dense_vectors[0], using="dense", limit=50),
                    Prefetch(
                        query={"indices": sparse_indices, "values": sparse_values},
                        using="sparse",
                        limit=50,
                    ),
                ],
                query=FusionQuery(fusion=Fusion.RRF),
                query_filter=query_filter,
                limit=50,
                with_payload=True,
            )
        finally:
            await client.close()

        retrieved: list[RetrievedClause] = []
        for point in results.points:
            payload = point.payload or {}
            retrieved.append(
                RetrievedClause(
                    clause_id=str(payload.get("clause_id", "")),
                    text=str(payload.get("text", "")),
                    score=float(point.score or 0.0),
                    regulation_id=str(payload.get("regulation_id", "")),
                    source_url=str(payload.get("source_url", "")),
                    section_number=str(payload.get("section_number", "")),
                    title=str(payload.get("title")) if payload.get("title") else None,
                )
            )
        reranked = await rerank(query, retrieved, top_k=top_k)

        if seed_clause_ids:
            from services.retrieval.graph_expand import expand_from_clause, merge_retrieved

            seeded: list[RetrievedClause] = []
            for clause_id in seed_clause_ids:
                graph_items = await expand_from_clause(clause_id, settings=self.settings)
                seeded.extend(
                    RetrievedClause(
                        clause_id=item.clause_id,
                        text=item.text,
                        score=max(0.1, 1.0 - item.hop_distance * 0.2),
                        regulation_id=regulation_id or "",
                        source_url=item.source_url,
                        section_number=item.section_number,
                        title=item.title,
                        hop_distance=item.hop_distance,
                    )
                    for item in graph_items
                )
            reranked = await rerank(
                query,
                merge_retrieved(seeded, reranked),
                top_k=top_k,
                settings=self.settings,
            )

        logger.info("Retrieved %d clauses (%d after rerank)", len(retrieved), len(reranked))
        return reranked
