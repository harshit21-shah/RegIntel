"""Federal Register API adapter for FDA-related documents."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, cast

import httpx

from services.ingestion.models import DocumentRef, RawDocument

logger = logging.getLogger(__name__)

FR_BASE = "https://www.federalregister.gov/api/v1"


class FederalRegisterAdapter:
    source_id = "federal_register"

    def __init__(
        self,
        *,
        cfr_title: int = 21,
        cfr_parts: tuple[str, ...] = ("1", "101"),
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.cfr_title = cfr_title
        self.cfr_parts = cfr_parts
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
        client = await self._get_client()
        refs: list[DocumentRef] = []
        for part in self.cfr_parts:
            params: list[tuple[str, str | int]] = [
                ("conditions[cfr][title]", self.cfr_title),
                ("conditions[cfr][part]", part),
                ("conditions[publication_date][gte]", since.strftime("%Y-%m-%d")),
                ("per_page", 20),
                ("order", "newest"),
                ("fields[]", "document_number"),
                ("fields[]", "title"),
                ("fields[]", "publication_date"),
                ("fields[]", "html_url"),
                ("fields[]", "full_text_xml_url"),
            ]
            response = await client.get(
                f"{FR_BASE}/documents.json",
                params=cast(Any, params),
            )
            response.raise_for_status()
            for item in response.json().get("results", []):
                pub_date = datetime.strptime(item["publication_date"], "%Y-%m-%d").replace(
                    tzinfo=UTC
                )
                refs.append(
                    DocumentRef(
                        source_id=self.source_id,
                        document_id=f"fr-{item['document_number']}",
                        title=item["title"],
                        published_at=pub_date,
                        metadata={
                            "document_number": item["document_number"],
                            "html_url": item.get("html_url", ""),
                            "full_text_xml_url": item.get("full_text_xml_url", ""),
                            "cfr_part": part,
                        },
                    )
                )
        return refs

    async def fetch(self, ref: DocumentRef) -> RawDocument:
        client = await self._get_client()
        xml_url = ref.metadata.get("full_text_xml_url") or ref.metadata.get("html_url", "")
        if not xml_url:
            raise ValueError(f"No fetch URL for Federal Register document {ref.document_id}")

        logger.info("Fetching Federal Register document %s", ref.document_id)
        response = await client.get(xml_url)
        response.raise_for_status()
        content_type = "application/xml" if xml_url.endswith(".xml") else "text/html"
        return RawDocument(ref=ref, content=response.text, content_type=content_type)
