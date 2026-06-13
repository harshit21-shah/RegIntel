"""SEC EDGAR full-text search adapter for fintech/compliance filings."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from services.ingestion.models import DocumentRef, RawDocument

logger = logging.getLogger(__name__)

EFTS_SEARCH = "https://efts.sec.gov/LATEST/search-index"
SEC_USER_AGENT = "RegIntel compliance-bot contact@regintel.local"


class SecEdgarAdapter:
    source_id = "sec_edgar"

    def __init__(
        self,
        *,
        forms: tuple[str, ...] = ("8-K", "10-K"),
        query: str = "compliance OR regulatory OR material weakness",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.forms = forms
        self.query = query
        self._client = client
        self._owns_client = client is None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
                headers={"User-Agent": SEC_USER_AGENT, "Accept": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def list_updates(self, since: datetime) -> list[DocumentRef]:
        client = await self._get_client()
        params = {
            "q": self.query,
            "dateRange": "custom",
            "startdt": since.strftime("%Y-%m-%d"),
            "enddt": datetime.now(tz=UTC).strftime("%Y-%m-%d"),
            "forms": ",".join(self.forms),
        }
        response = await client.get(EFTS_SEARCH, params=params)
        response.raise_for_status()
        hits = response.json().get("hits", {}).get("hits", [])

        refs: list[DocumentRef] = []
        for hit in hits[:25]:
            source = hit.get("_source", {})
            accession = source.get("adsh", source.get("file_num", "unknown"))
            form_type = source.get("form", "8-K")
            filed = source.get("file_date", source.get("period_ending", ""))
            display = (
                source.get("display_names", [""])[0] if source.get("display_names") else accession
            )
            refs.append(
                DocumentRef(
                    source_id=self.source_id,
                    document_id=f"sec-{accession}",
                    title=f"{form_type} filing — {display}",
                    published_at=(
                        datetime.strptime(filed, "%Y-%m-%d").replace(tzinfo=UTC)
                        if filed and len(filed) >= 10
                        else datetime.now(tz=UTC)
                    ),
                    metadata={
                        "accession": accession,
                        "form": form_type,
                        "cik": str(source.get("ciks", [""])[0] if source.get("ciks") else ""),
                        "file_url": source.get("file_url", ""),
                    },
                )
            )
        return refs

    async def fetch(self, ref: DocumentRef) -> RawDocument:
        client = await self._get_client()
        file_url = ref.metadata.get("file_url", "")
        if not file_url:
            accession = ref.metadata.get("accession", "").replace("-", "")
            cik = ref.metadata.get("cik", "")
            if accession and cik:
                file_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/"
                    f"{ref.metadata.get('accession')}.txt"
                )
        if not file_url:
            raise ValueError(f"No fetch URL for SEC filing {ref.document_id}")

        logger.info("Fetching SEC EDGAR document %s", ref.document_id)
        response = await client.get(file_url)
        response.raise_for_status()
        return RawDocument(ref=ref, content=response.text, content_type="text/plain")
