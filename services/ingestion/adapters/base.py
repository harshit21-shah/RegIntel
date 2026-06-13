"""Source adapter protocol."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from services.ingestion.models import DocumentRef, RawDocument


class SourceAdapter(Protocol):
    source_id: str

    async def list_updates(self, since: datetime) -> list[DocumentRef]: ...

    async def fetch(self, ref: DocumentRef) -> RawDocument: ...
