"""Parser for California HSC food code sections."""

from __future__ import annotations

import hashlib
import re
from datetime import date

from services.ingestion.models import ParsedClause, ParsedDocument, RawDocument

SECTION_SPLIT_RE = re.compile(r"\((?P<label>[a-z]|\d+)\)")


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def parse_ca_food_code(raw: RawDocument) -> ParsedDocument:
    section = raw.ref.metadata["section"]
    effective = raw.ref.published_at.date() if raw.ref.published_at else date.today()
    regulation_id = "ca-hsc-food-retail"
    parent_id = f"ca:HSC:{section}"
    clauses: list[ParsedClause] = []

    matches = list(SECTION_SPLIT_RE.finditer(raw.content))
    if not matches:
        clauses.append(
            ParsedClause(
                clause_id=parent_id,
                text=raw.content[:8000],
                parent_id=None,
                section_number=section,
                title=raw.ref.title,
            )
        )
    else:
        preamble = raw.content[: matches[0].start()].strip()
        if preamble:
            clauses.append(
                ParsedClause(
                    clause_id=parent_id,
                    text=preamble,
                    parent_id=None,
                    section_number=section,
                    title=raw.ref.title,
                )
            )
        for index, match in enumerate(matches):
            label = match.group("label")
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(raw.content)
            text = raw.content[start:end].strip()
            if text:
                clauses.append(
                    ParsedClause(
                        clause_id=f"{parent_id}:{label}",
                        text=f"({label}) {text}",
                        parent_id=parent_id,
                        section_number=section,
                        title=raw.ref.title,
                    )
                )

    return ParsedDocument(
        document_id=raw.ref.document_id,
        source="ca_food_code",
        title=raw.ref.title,
        regulation_id=regulation_id,
        agency="CDPH",
        jurisdiction="US-CA",
        effective_date=effective,
        version_hash=_hash_text(raw.content),
        clauses=clauses,
    )
