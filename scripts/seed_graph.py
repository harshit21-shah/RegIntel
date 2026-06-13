"""Graph seed and profile sync script."""

from __future__ import annotations

import asyncio
import logging

from services.api.db import AsyncSessionLocal
from services.graph.seed import seed_business_categories
from services.graph.sync_profiles import sync_all_profiles

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await seed_business_categories()
    async with AsyncSessionLocal() as session:
        count = await sync_all_profiles(session)
    logger.info("Graph seed complete; synced %d profiles", count)


if __name__ == "__main__":
    asyncio.run(main())
