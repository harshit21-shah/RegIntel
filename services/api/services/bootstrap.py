"""Startup bootstrap: Qdrant collection + minimal searchable corpus."""

from __future__ import annotations

import asyncio
import logging

from qdrant_client import AsyncQdrantClient

from services.api.config import Settings, get_settings
from services.ingestion.reference_corpus import reference_documents
from services.retrieval.embeddings import ingest_parsed_document
from services.retrieval.migrations.setup_collection import setup_collection

logger = logging.getLogger(__name__)

MIN_SEARCH_POINTS = 3


async def qdrant_point_count(settings: Settings) -> int:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        collections = await client.get_collections()
        names = {collection.name for collection in collections.collections}
        if settings.qdrant_collection not in names:
            return 0
        info = await client.get_collection(settings.qdrant_collection)
        return int(info.points_count or 0)
    finally:
        await client.close()


async def bootstrap_search_index(settings: Settings | None = None) -> int:
    """Ensure Qdrant has a reference glossary so queries work out of the box."""
    settings = settings or get_settings()
    if settings.app_env == "test":
        return 0

    await setup_collection()
    existing = await qdrant_point_count(settings)
    if existing >= MIN_SEARCH_POINTS:
        logger.info("Search index ready (%d points in %s)", existing, settings.qdrant_collection)
        return existing

    logger.info("Search index empty — embedding reference corpus…")
    embedded = 0
    for document in reference_documents():
        embedded += await ingest_parsed_document(document)
    logger.info("Bootstrap complete: %d reference clauses indexed", embedded)
    return embedded


def schedule_search_bootstrap() -> None:
    """Fire-and-forget bootstrap so API startup is not blocked on embedding."""
    settings = get_settings()
    if settings.app_env == "test" or not settings.auto_bootstrap_search:
        return

    async def _run() -> None:
        try:
            await bootstrap_search_index(settings)
        except Exception:
            logger.warning(
                "Search index bootstrap failed (Qdrant/embedder unavailable)", exc_info=True
            )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(_run())
