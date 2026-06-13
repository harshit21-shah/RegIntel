"""Tests for ingestion run tracking."""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from services.ingestion.models import ParsedDocument
from services.ingestion.pipeline import _tracked_ingestion


@pytest.mark.asyncio
async def test_tracked_ingestion_records_success() -> None:
    doc = ParsedDocument(
        document_id="ecfr-21-101",
        source="ecfr",
        title="Title 21 Part 101",
        regulation_id="21:101",
        effective_date=date(2025, 1, 1),
        version_hash="abc123",
        clauses=[],
    )
    mock_run = AsyncMock()
    mock_run.id = uuid.uuid4()

    with (
        patch(
            "services.api.services.ingestion_status.start_ingestion_run",
            new_callable=AsyncMock,
            return_value=mock_run,
        ) as start_mock,
        patch(
            "services.api.services.ingestion_status.complete_ingestion_run",
            new_callable=AsyncMock,
        ) as complete_mock,
    ):
        db = AsyncMock()
        result = await _tracked_ingestion(
            db,
            source="ecfr",
            runner=AsyncMock(return_value=[doc]),
        )

    assert len(result) == 1
    start_mock.assert_awaited_once_with(db, source="ecfr")
    complete_mock.assert_awaited_once_with(
        db,
        mock_run,
        document_count=1,
        error_message=None,
    )


@pytest.mark.asyncio
async def test_tracked_ingestion_records_failure() -> None:
    mock_run = AsyncMock()
    mock_run.id = uuid.uuid4()

    async def failing_runner() -> list[ParsedDocument]:
        raise RuntimeError("adapter timeout")

    with (
        patch(
            "services.api.services.ingestion_status.start_ingestion_run",
            new_callable=AsyncMock,
            return_value=mock_run,
        ),
        patch(
            "services.api.services.ingestion_status.complete_ingestion_run",
            new_callable=AsyncMock,
        ) as complete_mock,
    ):
        db = AsyncMock()
        with pytest.raises(RuntimeError, match="adapter timeout"):
            await _tracked_ingestion(db, source="federal_register", runner=failing_runner)

    complete_mock.assert_awaited_once()
    kwargs = complete_mock.await_args.kwargs
    assert kwargs["document_count"] == 0
    assert kwargs["error_message"] == "adapter timeout"


@pytest.mark.asyncio
async def test_tracked_ingestion_noop_without_db() -> None:
    with (
        patch(
            "services.api.services.ingestion_status.start_ingestion_run",
            new_callable=AsyncMock,
            return_value=None,
        ) as start_mock,
        patch(
            "services.api.services.ingestion_status.complete_ingestion_run",
            new_callable=AsyncMock,
        ) as complete_mock,
    ):
        result = await _tracked_ingestion(
            None,
            source="sec_edgar",
            runner=AsyncMock(return_value=[]),
        )

    assert result == []
    start_mock.assert_awaited_once_with(None, source="sec_edgar")
    complete_mock.assert_awaited_once_with(None, None, document_count=0, error_message=None)
