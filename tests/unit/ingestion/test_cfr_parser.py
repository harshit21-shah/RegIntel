"""Tests for CFR markdown parser."""

from datetime import UTC, datetime
from pathlib import Path

from services.ingestion.models import DocumentRef, RawDocument
from services.ingestion.parsers.cfr import parse_cfr_markdown, parse_federal_register_document

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "ecfr_part101_sample.md"


def _sample_raw() -> RawDocument:
    return RawDocument(
        ref=DocumentRef(
            source_id="ecfr",
            document_id="ecfr-21-101-2026-06-11",
            title="21 CFR Part 101",
            metadata={
                "title_number": "21",
                "part": "101",
                "effective_date": "2026-06-11",
            },
        ),
        content=FIXTURE.read_text(encoding="utf-8"),
    )


def test_parse_cfr_markdown_extracts_sections_and_subsections() -> None:
    document = parse_cfr_markdown(_sample_raw())
    clause_ids = {clause.clause_id for clause in document.clauses}

    assert document.source == "ecfr"
    assert document.regulation_id == "ecfr-21-101"
    assert "ecfr:21:101:101.1" in clause_ids
    assert "ecfr:21:101:101.1:a" in clause_ids
    assert "ecfr:21:101:101.9:j" in clause_ids
    assert len(document.clauses) >= 20


def test_parse_cfr_html_extracts_sections() -> None:
    html = """
    <div class="part" id="part-101">
    <h4 data-hierarchy-metadata='{"path":"/on/2026-06-11/title-21/section-101.1","citation":"21 CFR 101.1"}'>
    &#167; 101.1 Principal display panel.</h4>
    <p>The term <em>principal display panel</em> means the front of the package.</p>
    <div id="p-101.1(a)"><p class="indent-1">(a) For rectangular packages, height times width.</p></div>
    </div>
    """
    raw = RawDocument(
        ref=DocumentRef(
            source_id="ecfr",
            document_id="ecfr-21-101-html",
            title="21 CFR Part 101",
            metadata={"title_number": "21", "part": "101", "effective_date": "2026-06-11"},
        ),
        content=html,
    )
    document = parse_cfr_markdown(raw)
    clause_ids = {clause.clause_id for clause in document.clauses}
    assert "ecfr:21:101:101.1" in clause_ids
    assert "ecfr:21:101:101.1:a" in clause_ids


def test_parse_federal_register_document_strips_html() -> None:
    raw = RawDocument(
        ref=DocumentRef(
            source_id="federal_register",
            document_id="fr-2024-00001",
            title="Sample Rule",
            published_at=datetime(2024, 1, 15, tzinfo=UTC),
            metadata={"document_number": "2024-00001", "html_url": "https://example.com"},
        ),
        content="<p>Manufacturers <strong>shall</strong> maintain records.</p>",
    )
    document = parse_federal_register_document(raw)
    assert len(document.clauses) == 1
    assert "shall" in document.clauses[0].text
    assert document.clauses[0].clause_id == "fr:2024-00001"
