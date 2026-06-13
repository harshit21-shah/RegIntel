"""Tests for severity classification."""

from datetime import date

import pytest

from services.ingestion.diff_engine import ChangeType, ClauseDiff
from services.ingestion.severity import (
    Severity,
    classify_rule_based,
    classify_with_fallback,
    is_pipeline_trigger,
)


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


class _FailingLLM:
    """Stands in for an LLM that is down/rate-limited."""

    async def complete(self, *args: object, **kwargs: object) -> object:
        raise RuntimeError("LLM unavailable")


@pytest.mark.asyncio
async def test_severity_fails_safe_to_substantive_not_cosmetic() -> None:
    # Ambiguous mid-similarity change that requires the LLM tier; the classifier
    # must NOT silently drop to COSMETIC when the LLM fails — the worst failure
    # mode for a compliance tool is a missed substantive change.
    diff = ClauseDiff(
        clause_id="ecfr:21:101:101.5",
        change_type=ChangeType.MODIFIED,
        old_text="The product description must be accurate and not misleading.",
        new_text="The product description must be accurate, complete, and not misleading.",
        semantic_similarity=0.9,
    )
    result = await classify_with_fallback(
        diff,
        document_id="doc",
        source="ecfr",
        effective_date=date(2026, 6, 11),
        llm=_FailingLLM(),  # type: ignore[arg-type]
    )
    assert result is not None
    assert result.severity == Severity.SUBSTANTIVE
    assert is_pipeline_trigger(result.severity)
