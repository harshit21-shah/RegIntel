"""Tests for severity classification."""

from datetime import date

from services.ingestion.diff_engine import ChangeType, ClauseDiff
from services.ingestion.severity import Severity, classify_rule_based, is_pipeline_trigger


def test_critical_for_new_obligation_with_deadline() -> None:
    diff = ClauseDiff(
        clause_id="ecfr:21:101:101.9:a",
        change_type=ChangeType.ADDED,
        new_text="Manufacturers shall comply by January 2027.",
    )
    result = classify_rule_based(
        diff,
        document_id="doc",
        source="ecfr",
        effective_date=date(2026, 6, 11),
    )
    assert result is not None
    assert result.severity == Severity.CRITICAL


def test_cosmetic_for_near_identical_change() -> None:
    diff = ClauseDiff(
        clause_id="ecfr:21:101:101.1",
        change_type=ChangeType.MODIFIED,
        old_text="The label shall be clear and conspicuous.",
        new_text="The label shall be clear and conspicuous",
        semantic_similarity=0.99,
    )
    result = classify_rule_based(
        diff,
        document_id="doc",
        source="ecfr",
        effective_date=date(2026, 6, 11),
    )
    assert result is not None
    assert result.severity == Severity.COSMETIC


def test_pipeline_trigger_excludes_cosmetic() -> None:
    assert is_pipeline_trigger(Severity.SUBSTANTIVE)
    assert is_pipeline_trigger(Severity.CRITICAL)
    assert not is_pipeline_trigger(Severity.COSMETIC)
