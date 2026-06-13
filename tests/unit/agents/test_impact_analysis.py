"""Tests for Impact-Analysis NO_IMPACT escape hatch parsing."""

from __future__ import annotations

from services.agents.impact_analysis import _declared_no_impact, _parse_obligations


def test_declared_no_impact_true() -> None:
    assert _declared_no_impact('{"no_impact": true, "obligations": []}') is True


def test_declared_no_impact_false_when_obligations_present() -> None:
    raw = '{"no_impact": false, "obligations": [{"text": "x", "citation_clause_ids": ["a"]}]}'
    assert _declared_no_impact(raw) is False


def test_declared_no_impact_false_on_garbage() -> None:
    assert _declared_no_impact("not json at all") is False


def test_no_impact_payload_yields_no_obligations() -> None:
    assert _parse_obligations('{"no_impact": true, "obligations": []}') == []
