"""Parser for SEC EDGAR plain-text filings."""

from __future__ import annotations

import hashlib
import re
from datetime import date

from services.ingestion.models import ParsedClause, ParsedDocument, RawDocument

ITEM_RE = re.compile(r"^Item\s+(\d+\.\d+)\.?\s*(.+)$", re.MULTILINE | re.I)


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_sec_filing(raw: RawDocument) -> ParsedDocument:
    published = raw.ref.published_at.date() if raw.ref.published_at else date.today()
    accession = raw.ref.metadata.get("accession", raw.ref.document_id)
    form_type = raw.ref.metadata.get("form", "8-K")
    regulation_id = f"sec-{accession}"
    clauses: list[ParsedClause] = []

    items = list(ITEM_RE.finditer(raw.content))
    if items:
        for index, match in enumerate(items):
            item_num = match.group(1)
            start = match.end()
            end = items[index + 1].start() if index + 1 < len(items) else len(raw.content)
            body = raw.content[start:end].strip()[:8000]
            if body:
                clauses.append(
                    ParsedClause(
                        clause_id=f"sec:{accession}:item:{item_num}",
                        text=f"Item {item_num}. {body}",
                        parent_id=None,
                        section_number=item_num,
                        title=match.group(2).strip()[:200],
                    )
                )
    else:
        clauses.append(
            ParsedClause(
                clause_id=f"sec:{accession}:full",
                text=raw.content[:8000],
                parent_id=None,
                section_number="full",
                title=raw.ref.title,
            )
        )

    return ParsedDocument(
        document_id=raw.ref.document_id,
        source="sec_edgar",
        title=f"{form_type} — {raw.ref.title}",
        regulation_id=regulation_id,
        agency="SEC",
        jurisdiction="US",
        effective_date=published,
        version_hash=_hash_text(raw.content),
        clauses=clauses,
    )
