"""CFR markdown/XML parsers producing clause-level ParsedDocument objects."""

from __future__ import annotations

import hashlib
import html as html_lib
import re
from datetime import date

from services.ingestion.models import ParsedClause, ParsedDocument, RawDocument

SECTION_HEADER_RE = re.compile(
    r"^#{1,6}\s*§\s*(\d+\.\d+)\s+(.+?)\s*$",
    re.MULTILINE,
)
SECTION_HTML_RE = re.compile(
    r"<h4\s+data-hierarchy-metadata='[^']*section-([\d.]+)[^']*'[^>]*>(.*?)</h4>",
    re.DOTALL | re.IGNORECASE,
)
SUBSECTION_RE = re.compile(r"\(([a-z]|\d+[a-z]?)\)")


def canonical_clause_id(title: int, part: str, section: str, subsection: str | None = None) -> str:
    base = f"ecfr:{title}:{part}:{section}"
    if subsection:
        return f"{base}:{subsection}"
    return base


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _split_subsections(
    title_number: int,
    part: str,
    section_number: str,
    section_title: str,
    body: str,
) -> list[ParsedClause]:
    matches = list(SUBSECTION_RE.finditer(body))
    if not matches:
        clause_id = canonical_clause_id(title_number, part, section_number)
        text = body.strip()
        if not text:
            return []
        return [
            ParsedClause(
                clause_id=clause_id,
                text=text,
                parent_id=None,
                section_number=section_number,
                title=section_title,
            )
        ]

    clauses: list[ParsedClause] = []
    parent_id = canonical_clause_id(title_number, part, section_number)
    preamble = body[: matches[0].start()].strip()
    if preamble:
        clauses.append(
            ParsedClause(
                clause_id=parent_id,
                text=preamble,
                parent_id=None,
                section_number=section_number,
                title=section_title,
            )
        )

    part = section_number.split(".")[0]
    for index, match in enumerate(matches):
        subsection = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        subsection_text = body[start:end].strip()
        if not subsection_text:
            continue
        clauses.append(
            ParsedClause(
                clause_id=canonical_clause_id(title_number, part, section_number, subsection),
                text=f"({subsection}) {subsection_text}",
                parent_id=parent_id,
                section_number=section_number,
                title=section_title,
            )
        )
    return clauses


def _strip_html(text: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text).replace("\u00a7", "§")
    return re.sub(r"\s+", " ", text).strip()


def _extract_section_title(header_html: str, section_number: str) -> str:
    header_text = _strip_html(header_html)
    title_match = re.match(rf"§?\s*{re.escape(section_number)}\s+(.*)", header_text)
    return title_match.group(1).strip() if title_match else header_text


def _parse_sections_from_html(title_number: int, part: str, content: str) -> list[ParsedClause]:
    clauses: list[ParsedClause] = []
    section_matches = list(SECTION_HTML_RE.finditer(content))
    for index, match in enumerate(section_matches):
        section_number = match.group(1)
        section_title = _extract_section_title(match.group(2), section_number)
        body_start = match.end()
        body_end = (
            section_matches[index + 1].start() if index + 1 < len(section_matches) else len(content)
        )
        body = _strip_html(content[body_start:body_end])
        clauses.extend(_split_subsections(title_number, part, section_number, section_title, body))
    return clauses


def _parse_sections_from_markdown(title_number: int, part: str, content: str) -> list[ParsedClause]:
    clauses: list[ParsedClause] = []
    section_matches = list(SECTION_HEADER_RE.finditer(content))
    for index, match in enumerate(section_matches):
        section_number = match.group(1)
        section_title = match.group(2).strip()
        body_start = match.end()
        body_end = (
            section_matches[index + 1].start() if index + 1 < len(section_matches) else len(content)
        )
        body = content[body_start:body_end]
        clauses.extend(_split_subsections(title_number, part, section_number, section_title, body))
    return clauses


def parse_cfr_markdown(raw: RawDocument) -> ParsedDocument:
    title_number = int(raw.ref.metadata.get("title_number", "21"))
    part = raw.ref.metadata["part"]
    effective = date.fromisoformat(raw.ref.metadata["effective_date"])
    content = raw.content

    if content.lstrip().startswith("<"):
        clauses = _parse_sections_from_html(title_number, part, content)
    else:
        clauses = _parse_sections_from_markdown(title_number, part, content)

    version_hash = _hash_text(raw.content)
    return ParsedDocument(
        document_id=raw.ref.document_id,
        source="ecfr",
        title=raw.ref.title,
        regulation_id=f"ecfr-{title_number}-{part}",
        agency="FDA",
        jurisdiction="US",
        effective_date=effective,
        version_hash=version_hash,
        clauses=clauses,
    )


def parse_federal_register_document(raw: RawDocument) -> ParsedDocument:
    """Parse Federal Register content into a single-clause document for MVP."""
    published = raw.ref.published_at.date() if raw.ref.published_at else date.today()
    text = re.sub(r"<[^>]+>", " ", raw.content)
    text = re.sub(r"\s+", " ", text).strip()
    clause_id = f"fr:{raw.ref.metadata.get('document_number', raw.ref.document_id)}"
    version_hash = _hash_text(text)
    return ParsedDocument(
        document_id=raw.ref.document_id,
        source="federal_register",
        title=raw.ref.title,
        regulation_id=raw.ref.document_id,
        agency="FDA",
        jurisdiction="US",
        effective_date=published,
        version_hash=version_hash,
        clauses=[
            ParsedClause(
                clause_id=clause_id,
                text=text[:8000],
                parent_id=None,
                section_number=raw.ref.metadata.get("document_number", "full"),
                title=raw.ref.title,
            )
        ],
    )
