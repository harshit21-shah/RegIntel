"""Idempotent Qdrant collection setup for clause embeddings."""

from __future__ import annotations

import asyncio
import logging

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, SparseVectorParams, VectorParams

from services.api.config import get_settings

logger = logging.getLogger(__name__)

DENSE_DIM = 1024


async def setup_collection() -> None:
    settings = get_settings()
    client = AsyncQdrantClient(url=settings.qdrant_url)

    try:
        collections = await client.get_collections()
        existing = {c.name for c in collections.collections}

        if settings.qdrant_collection in existing:
            logger.info("Collection %s already exists", settings.qdrant_collection)
            return

        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config={
                "dense": VectorParams(size=DENSE_DIM, distance=Distance.COSINE),
            },
            sparse_vectors_config={"sparse": SparseVectorParams()},
        )
        logger.info("Created Qdrant collection: %s", settings.qdrant_collection)
    finally:
        await client.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(setup_collection())


if __name__ == "__main__":
    main()
