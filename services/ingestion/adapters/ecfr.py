"""eCFR API adapter for Title 21 Parts 1 and 101."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, cast

import httpx

from services.ingestion.models import DocumentRef, RawDocument

logger = logging.getLogger(__name__)

ECFR_BASE = "https://www.ecfr.gov/api"
DEFAULT_TITLE = 21
DEFAULT_PARTS = ("1", "101")


class EcfrAdapter:
    source_id = "ecfr"

    def __init__(
        self,
        *,
        title: int = DEFAULT_TITLE,
        parts: tuple[str, ...] = DEFAULT_PARTS,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.title = title
        self.parts = parts
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0, follow_redirects=True)
        return self._client

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_latest_date(self) -> str:
        client = await self._get_client()
        response = await client.get(f"{ECFR_BASE}/versioner/v1/titles")
        response.raise_for_status()
        payload = response.json()
        for item in payload["titles"]:
            if item["number"] == self.title:
                return str(item["up_to_date_as_of"])
        raise ValueError(f"Title {self.title} not found in eCFR titles response")

    async def list_updates(self, since: datetime) -> list[DocumentRef]:
        effective_date = await self.get_latest_date()
        refs: list[DocumentRef] = []
        for part in self.parts:
            document_id = f"ecfr-{self.title}-{part}-{effective_date}"
            refs.append(
                DocumentRef(
                    source_id=self.source_id,
                    document_id=document_id,
                    title=f"{self.title} CFR Part {part}",
                    published_at=datetime.fromisoformat(effective_date).replace(tzinfo=UTC),
                    metadata={
                        "title_number": str(self.title),
                        "part": part,
                        "effective_date": effective_date,
                    },
                )
            )
        return [ref for ref in refs if ref.published_at and ref.published_at >= since]

    async def fetch(self, ref: DocumentRef) -> RawDocument:
        part = ref.metadata["part"]
        effective_date = ref.metadata["effective_date"]
        client = await self._get_client()
        url = (
            f"{ECFR_BASE}/renderer/v1/content/enhanced/"
            f"{effective_date}/title-{self.title}?part={part}"
        )
        logger.info("Fetching eCFR part %s for title %s (%s)", part, self.title, effective_date)
        response = await client.get(url)
        response.raise_for_status()
        return RawDocument(
            ref=ref,
            content=response.text,
            content_type="text/markdown",
        )

    async def fetch_structure(self, effective_date: str) -> dict[str, Any]:
        client = await self._get_client()
        url = f"{ECFR_BASE}/versioner/v1/structure/{effective_date}/title-{self.title}.json"
        response = await client.get(url)
        response.raise_for_status()
        return cast(dict[str, Any], response.json())
