"""Fast embed-only ingestion (no agent pipeline, no ingestion run tracking)."""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import UTC, datetime, timedelta

from services.ingestion.adapters.ca_food_code import CaFoodCodeAdapter
from services.ingestion.adapters.ecfr import EcfrAdapter
from services.ingestion.adapters.federal_register import FederalRegisterAdapter
from services.ingestion.adapters.sec_edgar import SecEdgarAdapter
from services.ingestion.parsers.ca_food_code import parse_ca_food_code
from services.ingestion.parsers.cfr import parse_cfr_markdown, parse_federal_register_document
from services.ingestion.parsers.sec_edgar import parse_sec_filing
from services.ingestion.reference_corpus import reference_documents
from services.retrieval.embeddings import ingest_parsed_document

logger = logging.getLogger(__name__)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Embed regulatory sources into Qdrant (fast path)")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["ecfr", "federal_register", "ca_food_code", "sec_edgar", "reference"],
        default=["reference", "sec_edgar", "ecfr"],
    )
    parser.add_argument("--parts", nargs="+", default=["101"])
    parser.add_argument("--title", type=int, default=21)
    parser.add_argument("--fr-limit", type=int, default=5)
    parser.add_argument("--sec-limit", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    total = 0

    if "reference" in args.sources:
        for document in reference_documents():
            count = await ingest_parsed_document(document)
            total += count
            logger.info("Embedded reference doc %s: %d clauses", document.document_id, count)

    if "ecfr" in args.sources:
        adapter = EcfrAdapter(title=args.title, parts=tuple(args.parts))
        since = datetime.now(tz=UTC) - timedelta(days=3650)
        try:
            for ref in await adapter.list_updates(since):
                raw = await adapter.fetch(ref)
                parsed = parse_cfr_markdown(raw)
                count = await ingest_parsed_document(parsed)
                total += count
                logger.info("Embedded %s: %d clauses", parsed.document_id, count)
        finally:
            await adapter.close()

    if "sec_edgar" in args.sources:
        adapter = SecEdgarAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=90)
        try:
            refs = await adapter.list_updates(since)
            for ref in refs[: args.sec_limit]:
                try:
                    raw = await adapter.fetch(ref)
                    parsed = parse_sec_filing(raw)
                    count = await ingest_parsed_document(parsed)
                    total += count
                    logger.info("Embedded %s: %d clauses", parsed.document_id, count)
                except Exception:
                    logger.warning("Skipping SEC filing %s", ref.document_id, exc_info=True)
        finally:
            await adapter.close()

    if "federal_register" in args.sources:
        adapter = FederalRegisterAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=90)
        try:
            refs = await adapter.list_updates(since)
            for ref in refs[: args.fr_limit]:
                raw = await adapter.fetch(ref)
                parsed = parse_federal_register_document(raw)
                count = await ingest_parsed_document(parsed)
                total += count
                logger.info("Embedded %s: %d clauses", parsed.document_id, count)
        finally:
            await adapter.close()

    if "ca_food_code" in args.sources:
        adapter = CaFoodCodeAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=3650)
        try:
            for ref in await adapter.list_updates(since):
                raw = await adapter.fetch(ref)
                parsed = parse_ca_food_code(raw)
                count = await ingest_parsed_document(parsed)
                total += count
                logger.info("Embedded %s: %d clauses", parsed.document_id, count)
        finally:
            await adapter.close()

    logger.info("Total clauses embedded: %d", total)


if __name__ == "__main__":
    asyncio.run(main())
