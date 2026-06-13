"""Verbatim reference clauses for common compliance concepts (public-domain sources)."""

from __future__ import annotations

from datetime import date

from services.ingestion.models import ParsedClause, ParsedDocument

REFERENCE_CLAUSES: list[tuple[str, str, str, str]] = [
    (
        "ref:sec:glossary:filings",
        "SEC",
        "https://www.sec.gov/about/edgar-landing",
        (
            "SEC filings are formal documents that public companies, certain insiders, and "
            "registered entities must submit to the U.S. Securities and Exchange Commission (SEC). "
            "Common filing types include Form 10-K (annual report), Form 10-Q (quarterly report), "
            "Form 8-K (material current events), and proxy statements. Filings are submitted through "
            "EDGAR, the Electronic Data Gathering, Analysis, and Retrieval system, and are used by "
            "investors and regulators to assess financial condition, risk factors, and compliance "
            "with federal securities laws."
        ),
    ),
    (
        "ref:sec:glossary:edgar",
        "SEC",
        "https://www.sec.gov/edgar/search-and-access",
        (
            "EDGAR is the SEC's system for collecting, validating, indexing, accepting, and "
            "forwarding submissions by companies and others required by law to file forms with the "
            "SEC. EDGAR filings are public and searchable. RegIntel indexes selected EDGAR filing "
            "text to support citation-backed compliance queries."
        ),
    ),
    (
        "ref:fda:glossary:overview",
        "FDA",
        "https://www.fda.gov/about-fda/what-we-do",
        (
            "The U.S. Food and Drug Administration (FDA) is a federal agency within the Department "
            "of Health and Human Services. FDA is responsible for protecting public health by "
            "assuring the safety, efficacy, and security of human and veterinary drugs, biological "
            "products, medical devices, the nation's food supply, cosmetics, and products that emit "
            "radiation. FDA requirements appear in statutes and in Title 21 of the Code of Federal "
            "Regulations (21 CFR)."
        ),
    ),
]

CLAUSE_SOURCE_URLS = {clause_id: url for clause_id, _, url, _ in REFERENCE_CLAUSES}


def reference_documents() -> list[ParsedDocument]:
    clauses = [
        ParsedClause(
            clause_id=clause_id,
            text=text,
            parent_id=None,
            section_number=clause_id.split(":")[-1],
            title=f"{agency} reference",
        )
        for clause_id, agency, _url, text in REFERENCE_CLAUSES
    ]
    return [
        ParsedDocument(
            document_id="reference-corpus-v1",
            source="reference",
            title="RegIntel reference glossary",
            regulation_id="reference-corpus",
            agency="MULTI",
            jurisdiction="US",
            effective_date=date(2025, 1, 1),
            version_hash="reference-v1",
            clauses=clauses,
        )
    ]
