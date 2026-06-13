"""Embedding pipeline: clause text -> vectors -> Qdrant upsert."""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Any

import httpx
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    SparseVector,
)

from services.api.config import Settings, get_settings
from services.ingestion.models import ParsedClause, ParsedDocument

logger = logging.getLogger(__name__)

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"
DENSE_DIM = 1024


@dataclass(frozen=True)
class EmbeddedClause:
    clause: ParsedClause
    document: ParsedDocument
    dense_vector: list[float]
    sparse_indices: list[int]
    sparse_values: list[float]
    source_url: str


def point_id(clause_id: str, version_hash: str) -> str:
    digest = hashlib.sha256(f"{clause_id}:{version_hash}".encode()).hexdigest()
    return str(uuid.UUID(digest[:32]))


def ecfr_source_url(document: ParsedDocument, clause: ParsedClause) -> str:
    if document.source == "ecfr":
        return f"https://www.ecfr.gov/current/title-21/section-{clause.section_number}"
    if document.source == "reference":
        from services.ingestion.reference_corpus import CLAUSE_SOURCE_URLS

        return CLAUSE_SOURCE_URLS.get(clause.clause_id, "https://www.sec.gov")
    if document.source == "sec_edgar":
        return "https://www.sec.gov/edgar/search-and-access"
    return document.regulation_id


class EmbeddingService:
    """Embeds clauses with Voyage (primary) or FastEmbed BGE (fallback)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._dense_model: Any = None
        self._sparse_model: Any = None

    def _load_fastembed(self) -> tuple[Any, Any]:
        if self._dense_model is None or self._sparse_model is None:
            from fastembed import SparseTextEmbedding, TextEmbedding

            self._dense_model = TextEmbedding(model_name="BAAI/bge-large-en-v1.5")
            self._sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
        return self._dense_model, self._sparse_model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.settings.voyage_api_key:
            return await self._embed_voyage(texts)
        dense_model, _ = self._load_fastembed()
        return [vector.tolist() for vector in dense_model.embed(texts)]

    async def embed_sparse(self, texts: list[str]) -> list[tuple[list[int], list[float]]]:
        _, sparse_model = self._load_fastembed()
        results: list[tuple[list[int], list[float]]] = []
        for sparse in sparse_model.embed(texts):
            results.append((sparse.indices.tolist(), sparse.values.tolist()))
        return results

    async def _embed_voyage(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                VOYAGE_URL,
                headers={
                    "Authorization": f"Bearer {self.settings.voyage_api_key}",
                    "Content-Type": "application/json",
                },
                json={"input": texts, "model": "voyage-law-2"},
            )
            response.raise_for_status()
            data = response.json()["data"]
            return [item["embedding"] for item in data]

    async def embed_document(self, document: ParsedDocument) -> list[EmbeddedClause]:
        if not document.clauses:
            return []
        texts = [clause.text for clause in document.clauses]
        dense_vectors = await self.embed_texts(texts)
        sparse_vectors = await self.embed_sparse(texts)
        embedded: list[EmbeddedClause] = []
        for clause, dense, (indices, values) in zip(
            document.clauses, dense_vectors, sparse_vectors, strict=True
        ):
            embedded.append(
                EmbeddedClause(
                    clause=clause,
                    document=document,
                    dense_vector=dense,
                    sparse_indices=indices,
                    sparse_values=values,
                    source_url=ecfr_source_url(document, clause),
                )
            )
        return embedded


async def supersede_old_versions(
    client: AsyncQdrantClient,
    *,
    collection: str,
    clause_ids: list[str],
) -> None:
    """Flag any existing points for these clause_ids as not-current.

    Point IDs are hash(clause_id + version_hash), so a new version creates a new
    point and the prior version persists. Without this step, hybrid retrieval can
    surface two contradictory versions of the same clause_id. We flip the old
    points to is_current=False BEFORE upserting the new version (which carries
    is_current=True), so a re-embed of the same version is harmless.
    """
    if not clause_ids:
        return
    await client.set_payload(
        collection_name=collection,
        payload={"is_current": False},
        points=Filter(must=[FieldCondition(key="clause_id", match=MatchAny(any=clause_ids))]),
    )


async def upsert_clauses(
    embedded_clauses: list[EmbeddedClause],
    *,
    settings: Settings | None = None,
) -> int:
    if not embedded_clauses:
        return 0
    settings = settings or get_settings()
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        clause_ids = [item.clause.clause_id for item in embedded_clauses]
        await supersede_old_versions(
            client, collection=settings.qdrant_collection, clause_ids=clause_ids
        )
        points = [
            PointStruct(
                id=point_id(item.clause.clause_id, item.document.version_hash),
                vector={
                    "dense": item.dense_vector,
                    "sparse": SparseVector(
                        indices=item.sparse_indices,
                        values=item.sparse_values,
                    ),
                },
                payload={
                    "clause_id": item.clause.clause_id,
                    "regulation_id": item.document.regulation_id,
                    "agency": item.document.agency,
                    "jurisdiction": item.document.jurisdiction,
                    "effective_date": item.document.effective_date.isoformat(),
                    "version_hash": item.document.version_hash,
                    "text": item.clause.text,
                    "section_number": item.clause.section_number,
                    "title": item.clause.title or item.document.title,
                    "source_url": item.source_url,
                    "business_categories": [],
                    "is_current": True,
                },
            )
            for item in embedded_clauses
        ]
        await client.upsert(collection_name=settings.qdrant_collection, points=points)
        logger.info("Upserted %d clauses to Qdrant", len(points))
        return len(points)
    finally:
        await client.close()


async def ingest_parsed_document(document: ParsedDocument) -> int:
    service = EmbeddingService()
    embedded = await service.embed_document(document)
    return await upsert_clauses(embedded)
