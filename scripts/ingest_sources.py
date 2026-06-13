"""Ingest regulatory sources into Qdrant."""

from __future__ import annotations

import argparse
import asyncio
import logging

from services.agents.llm_client import LLMClient
from services.api.db import AsyncSessionLocal
from services.ingestion.pipeline import (
    ingest_ca_food_code,
    ingest_ecfr_parts,
    ingest_federal_register,
    ingest_sec_edgar,
)

logger = logging.getLogger(__name__)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest RegIntel regulatory sources")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["ecfr", "federal_register", "ca_food_code", "sec_edgar"],
        default=["ecfr"],
    )
    parser.add_argument("--parts", nargs="+", default=["1", "101"])
    parser.add_argument("--fr-limit", type=int, default=5)
    parser.add_argument("--sec-limit", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    async with AsyncSessionLocal() as db:
        llm = LLMClient()

        if "ecfr" in args.sources:
            docs = await ingest_ecfr_parts(parts=tuple(args.parts), db=db, llm=llm)
            logger.info("eCFR ingest complete: %d documents", len(docs))

        if "ca_food_code" in args.sources:
            docs = await ingest_ca_food_code(db=db, llm=llm)
            logger.info("CA food code ingest complete: %d documents", len(docs))

        if "federal_register" in args.sources:
            docs = await ingest_federal_register(limit=args.fr_limit, db=db, llm=llm)
            logger.info("Federal Register ingest complete: %d documents", len(docs))

        if "sec_edgar" in args.sources:
            docs = await ingest_sec_edgar(limit=args.sec_limit, db=db, llm=llm)
            logger.info("SEC EDGAR ingest complete: %d documents", len(docs))


if __name__ == "__main__":
    asyncio.run(main())
