"""Ingestion orchestration: fetch, parse, diff, graph-build, embed, pipeline."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.llm_client import LLMClient
from services.agents.pipeline import run_pipeline
from services.graph.builder import GraphBuilder
from services.ingestion.adapters.ca_food_code import CaFoodCodeAdapter
from services.ingestion.adapters.ecfr import EcfrAdapter
from services.ingestion.adapters.federal_register import FederalRegisterAdapter
from services.ingestion.diff_engine import diff_documents
from services.ingestion.document_store import load_previous, save_document
from services.ingestion.models import ParsedDocument
from services.ingestion.parsers.ca_food_code import parse_ca_food_code
from services.ingestion.parsers.cfr import parse_cfr_markdown, parse_federal_register_document
from services.ingestion.severity import classify_with_fallback, is_pipeline_trigger
from services.retrieval.embeddings import ingest_parsed_document

logger = logging.getLogger(__name__)


async def _tracked_ingestion(
    db: AsyncSession | None,
    *,
    source: str,
    runner: Callable[[], Awaitable[list[ParsedDocument]]],
) -> list[ParsedDocument]:
    from services.api.services.ingestion_status import complete_ingestion_run, start_ingestion_run

    run = await start_ingestion_run(db, source=source)
    documents: list[ParsedDocument] = []
    error: str | None = None
    try:
        documents = await runner()
        return documents
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        await complete_ingestion_run(
            db,
            run,
            document_count=len(documents),
            error_message=error,
        )


async def process_document(
    parsed: ParsedDocument,
    *,
    db: AsyncSession | None = None,
    llm: LLMClient | None = None,
) -> ParsedDocument:
    previous = load_previous(parsed.document_id)
    diff = diff_documents(previous, parsed)
    builder = GraphBuilder()
    await builder.upsert_document(parsed)

    changed_clause_ids = {
        item.clause_id
        for item in diff.material_changes
        if item.change_type.value in {"ADDED", "MODIFIED"}
    }
    if changed_clause_ids or previous is None:
        await ingest_parsed_document(parsed)
    else:
        logger.info("No clause changes for %s; skipping re-embed", parsed.document_id)

    if db is not None and llm is not None:
        for clause_diff in diff.material_changes:
            if previous is None and clause_diff.change_type.value == "ADDED":
                continue
            classified = await classify_with_fallback(
                clause_diff,
                document_id=parsed.document_id,
                source=parsed.source,
                effective_date=parsed.effective_date,
                llm=llm,
            )
            if classified and is_pipeline_trigger(classified.severity):
                from services.api.services.sqs_queue import enqueue_pipeline_change

                if not enqueue_pipeline_change(classified):
                    logger.info("Running inline agent pipeline for %s", classified.clause_id)
                    await run_pipeline(classified, db=db, llm=llm)

    save_document(parsed)
    return parsed


async def ingest_ecfr_parts(
    *,
    parts: tuple[str, ...] = ("1", "101"),
    db: AsyncSession | None = None,
    llm: LLMClient | None = None,
) -> list[ParsedDocument]:
    async def _run() -> list[ParsedDocument]:
        adapter = EcfrAdapter(parts=parts)
        since = datetime.now(tz=UTC) - timedelta(days=3650)
        documents: list[ParsedDocument] = []
        try:
            refs = await adapter.list_updates(since)
            for ref in refs:
                raw = await adapter.fetch(ref)
                parsed = parse_cfr_markdown(raw)
                await process_document(parsed, db=db, llm=llm)
                logger.info("Processed %s with %d clauses", parsed.document_id, len(parsed.clauses))
                documents.append(parsed)
            return documents
        finally:
            await adapter.close()

    return await _tracked_ingestion(db, source="ecfr", runner=_run)


async def ingest_federal_register(
    *,
    limit: int = 5,
    db: AsyncSession | None = None,
    llm: LLMClient | None = None,
) -> list[ParsedDocument]:
    async def _run() -> list[ParsedDocument]:
        adapter = FederalRegisterAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=90)
        documents: list[ParsedDocument] = []
        try:
            refs = await adapter.list_updates(since)
            for ref in refs[:limit]:
                raw = await adapter.fetch(ref)
                parsed = parse_federal_register_document(raw)
                await process_document(parsed, db=db, llm=llm)
                documents.append(parsed)
            return documents
        finally:
            await adapter.close()

    return await _tracked_ingestion(db, source="federal_register", runner=_run)


async def ingest_ca_food_code(
    *,
    db: AsyncSession | None = None,
    llm: LLMClient | None = None,
) -> list[ParsedDocument]:
    async def _run() -> list[ParsedDocument]:
        adapter = CaFoodCodeAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=3650)
        documents: list[ParsedDocument] = []
        try:
            refs = await adapter.list_updates(since)
            for ref in refs:
                raw = await adapter.fetch(ref)
                parsed = parse_ca_food_code(raw)
                await process_document(parsed, db=db, llm=llm)
                documents.append(parsed)
            return documents
        finally:
            await adapter.close()

    return await _tracked_ingestion(db, source="ca_food_code", runner=_run)


async def ingest_sec_edgar(
    *,
    limit: int = 10,
    db: AsyncSession | None = None,
    llm: LLMClient | None = None,
) -> list[ParsedDocument]:
    from services.ingestion.adapters.sec_edgar import SecEdgarAdapter
    from services.ingestion.parsers.sec_edgar import parse_sec_filing

    async def _run() -> list[ParsedDocument]:
        adapter = SecEdgarAdapter()
        since = datetime.now(tz=UTC) - timedelta(days=30)
        documents: list[ParsedDocument] = []
        try:
            refs = await adapter.list_updates(since)
            for ref in refs[:limit]:
                raw = await adapter.fetch(ref)
                parsed = parse_sec_filing(raw)
                await process_document(parsed, db=db, llm=llm)
                documents.append(parsed)
            return documents
        finally:
            await adapter.close()

    return await _tracked_ingestion(db, source="sec_edgar", runner=_run)
