"""Regex-based cross-reference extraction from clause text."""

from __future__ import annotations

import re
from dataclasses import dataclass

CFR_REF_RE = re.compile(
    r"(?P<title>\d+)\s*CFR\s*(?:Part\s*)?(?P<part>\d+(?:\.\d+)?)"
    r"(?:\s*[§.]?\s*(?P<section>\d+(?:\.\d+)*)?(?:\((?P<sub>[a-z0-9]+)\))?)?",
    re.I,
)
AMENDS_RE = re.compile(r"\bamends?\b", re.I)
SEE_ALSO_RE = re.compile(r"\bsee also\b", re.I)


@dataclass(frozen=True)
class CrossReference:
    source_clause_id: str
    target_regulation_id: str
    target_clause_id: str | None
    relationship: str
    confidence: float
    raw_match: str


def _regulation_id(title: str, part: str) -> str:
    part_num = part.split(".")[0]
    return f"ecfr-{title}-{part_num}"


def _clause_id(title: str, part: str, section: str | None, sub: str | None) -> str | None:
    if not section:
        return None
    part_num = part.split(".")[0]
    base = f"ecfr:{title}:{part_num}:{section}"
    if sub:
        return f"{base}:{sub}"
    return base


def extract_cross_references(source_clause_id: str, text: str) -> list[CrossReference]:
    refs: list[CrossReference] = []
    for match in CFR_REF_RE.finditer(text):
        title = match.group("title")
        part = match.group("part")
        section = match.group("section")
        sub = match.group("sub")
        relationship = "REFERENCES"
        window = text[max(0, match.start() - 40) : match.end() + 40]
        if AMENDS_RE.search(window):
            relationship = "AMENDS"
        elif SEE_ALSO_RE.search(window):
            relationship = "REFERENCES"

        refs.append(
            CrossReference(
                source_clause_id=source_clause_id,
                target_regulation_id=_regulation_id(title, part),
                target_clause_id=_clause_id(title, part, section, sub),
                relationship=relationship,
                confidence=0.7,
                raw_match=match.group(0),
            )
        )
    return refs
