"""Record and query ingestion run history."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models import IngestionRun


async def start_ingestion_run(db: AsyncSession | None, *, source: str) -> IngestionRun | None:
    if db is None:
        return None
    run = IngestionRun(id=uuid.uuid4(), source=source, status="RUNNING", document_count=0)
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def complete_ingestion_run(
    db: AsyncSession | None,
    run: IngestionRun | None,
    *,
    document_count: int,
    error_message: str | None = None,
) -> None:
    if db is None or run is None:
        return
    run.status = "FAILED" if error_message else "SUCCESS"
    run.document_count = document_count
    run.error_message = error_message
    run.completed_at = datetime.now(tz=UTC).replace(tzinfo=None)
    await db.commit()


async def latest_runs_by_source(db: AsyncSession) -> list[IngestionRun]:
    sources = ("ecfr", "federal_register", "ca_food_code", "sec_edgar")
    latest: list[IngestionRun] = []
    for source in sources:
        result = await db.execute(
            select(IngestionRun)
            .where(IngestionRun.source == source)
            .order_by(IngestionRun.started_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        if row is not None:
            latest.append(row)
    return latest
