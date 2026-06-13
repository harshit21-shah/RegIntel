"""Tests for startup search index bootstrap."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from services.api.config import Settings
from services.api.services.bootstrap import bootstrap_search_index


@pytest.mark.asyncio
async def test_bootstrap_skips_when_index_populated() -> None:
    settings = Settings(app_env="local", qdrant_collection="clauses_v1")
    with (
        patch("services.api.services.bootstrap.setup_collection", new_callable=AsyncMock) as setup,
        patch(
            "services.api.services.bootstrap.qdrant_point_count",
            new_callable=AsyncMock,
            return_value=10,
        ) as count,
        patch(
            "services.api.services.bootstrap.ingest_parsed_document",
            new_callable=AsyncMock,
        ) as ingest,
    ):
        result = await bootstrap_search_index(settings)
    assert result == 10
    setup.assert_awaited_once()
    count.assert_awaited_once()
    ingest.assert_not_awaited()


@pytest.mark.asyncio
async def test_bootstrap_embeds_reference_when_empty() -> None:
    settings = Settings(app_env="local", qdrant_collection="clauses_v1")
    with (
        patch("services.api.services.bootstrap.setup_collection", new_callable=AsyncMock),
        patch(
            "services.api.services.bootstrap.qdrant_point_count",
            new_callable=AsyncMock,
            side_effect=[0, 3],
        ),
        patch(
            "services.api.services.bootstrap.ingest_parsed_document",
            new_callable=AsyncMock,
            return_value=3,
        ) as ingest,
    ):
        result = await bootstrap_search_index(settings)
    assert result == 3
    ingest.assert_awaited_once()


@pytest.mark.asyncio
async def test_bootstrap_noop_in_test_env() -> None:
    settings = Settings(app_env="test")
    with patch("services.api.services.bootstrap.setup_collection", new_callable=AsyncMock) as setup:
        result = await bootstrap_search_index(settings)
    assert result == 0
    setup.assert_not_awaited()
