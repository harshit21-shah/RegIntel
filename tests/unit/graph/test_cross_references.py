"""Tests for cross-reference extraction."""

from services.graph.cross_references import extract_cross_references


def test_extract_cfr_reference() -> None:
    text = "This section amends 21 CFR 101.9(c) requirements for nutrition labeling."
    refs = extract_cross_references("ecfr:21:101:101.10", text)
    assert len(refs) >= 1
    assert refs[0].relationship == "AMENDS"
    assert refs[0].target_regulation_id == "ecfr-21-101"


def test_extract_see_also_reference() -> None:
    text = "See also 21 CFR Part 1 for general enforcement provisions."
    refs = extract_cross_references("ecfr:21:101:101.1", text)
    assert refs[0].relationship == "REFERENCES"
    assert refs[0].target_regulation_id == "ecfr-21-1"
