"""California Retail Food Code adapter (HSC Division 104)."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime

import httpx

from services.ingestion.models import DocumentRef, RawDocument

logger = logging.getLogger(__name__)

CA_LEGINFO_BASE = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml"
DEFAULT_SECTIONS = ("113785", "113947", "114047", "114259", "114380")


class CaFoodCodeAdapter:
    source_id = "ca_food_code"

    def __init__(
        self,
        *,
        sections: tuple[str, ...] = DEFAULT_SECTIONS,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.sections = sections
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0, follow_redirects=True)
        return self._client

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def list_updates(self, since: datetime) -> list[DocumentRef]:
        refs: list[DocumentRef] = []
        for section in self.sections:
            refs.append(
                DocumentRef(
                    source_id=self.source_id,
                    document_id=f"ca-hsc-{section}-2026",
                    title=f"CA HSC Section {section}",
                    published_at=datetime.now(tz=UTC),
                    metadata={"section": section, "law_code": "HSC"},
                )
            )
        return [ref for ref in refs if ref.published_at and ref.published_at >= since]

    async def fetch(self, ref: DocumentRef) -> RawDocument:
        section = ref.metadata["section"]
        client = await self._get_client()
        url = f"{CA_LEGINFO_BASE}?lawCode=HSC&sectionNum={section}."
        logger.info("Fetching CA HSC section %s", section)
        response = await client.get(url)
        response.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", response.text)
        text = re.sub(r"\s+", " ", text).strip()
        return RawDocument(ref=ref, content=text, content_type="text/html")
