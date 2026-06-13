"""Tests for eCFR adapter."""

from datetime import UTC, datetime
from typing import Any

import pytest

from services.ingestion.adapters.ecfr import EcfrAdapter


@pytest.mark.asyncio
async def test_ecfr_list_updates_and_fetch(httpx_mock: Any) -> None:
    httpx_mock.add_response(
        url="https://www.ecfr.gov/api/versioner/v1/titles",
        json={
            "titles": [
                {
                    "number": 21,
                    "up_to_date_as_of": "2026-06-11",
                }
            ]
        },
    )
    httpx_mock.add_response(
        url="https://www.ecfr.gov/api/renderer/v1/content/enhanced/2026-06-11/title-21?part=101",
        text="#### § 101.1 Principal display panel.\n\n(a) Example text.",
    )

    adapter = EcfrAdapter(parts=("101",))
    refs = await adapter.list_updates(datetime(2020, 1, 1, tzinfo=UTC))
    assert len(refs) == 1
    assert refs[0].document_id == "ecfr-21-101-2026-06-11"

    raw = await adapter.fetch(refs[0])
    assert "101.1" in raw.content
    await adapter.close()
