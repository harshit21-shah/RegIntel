"""Tests for clause-level diff engine."""

from datetime import date

from services.ingestion.diff_engine import ChangeType, diff_documents
from services.ingestion.models import ParsedClause, ParsedDocument


def _doc(clauses: list[ParsedClause], version: str) -> ParsedDocument:
    return ParsedDocument(
        document_id="ecfr-21-101-test",
        source="ecfr",
        title="Part 101",
        regulation_id="ecfr-21-101",
        effective_date=date(2026, 6, 11),
        version_hash=version,
        clauses=clauses,
    )


def test_diff_detects_added_modified_and_unchanged() -> None:
    old = _doc(
        [
            ParsedClause(
                clause_id="ecfr:21:101:101.1",
                text="Original text",
                section_number="101.1",
            ),
            ParsedClause(
                clause_id="ecfr:21:101:101.2",
                text="Stable text",
                section_number="101.2",
            ),
        ],
        "v1",
    )
    new = _doc(
        [
            ParsedClause(
                clause_id="ecfr:21:101:101.1",
                text="Updated text with shall requirement",
                section_number="101.1",
            ),
            ParsedClause(
                clause_id="ecfr:21:101:101.2",
                text="Stable text",
                section_number="101.2",
            ),
            ParsedClause(
                clause_id="ecfr:21:101:101.3",
                text="Brand new clause",
                section_number="101.3",
            ),
        ],
        "v2",
    )
    result = diff_documents(old, new)
    by_id = {item.clause_id: item.change_type for item in result.clause_diffs}
    assert by_id["ecfr:21:101:101.1"] == ChangeType.MODIFIED
    assert by_id["ecfr:21:101:101.2"] == ChangeType.UNCHANGED
    assert by_id["ecfr:21:101:101.3"] == ChangeType.ADDED
