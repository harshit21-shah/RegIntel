"""Tests for relevance weight heuristics."""

from services.agents.relevance_weights import DEFAULT_WEIGHTS, apply_hop_weight


def test_apply_hop_weight_reduces_score_at_depth() -> None:
    base = 0.85
    shallow = apply_hop_weight(base, 0, DEFAULT_WEIGHTS)
    deep = apply_hop_weight(base, 3, DEFAULT_WEIGHTS)
    assert shallow > deep


def test_apply_hop_weight_never_below_floor() -> None:
    score = apply_hop_weight(0.1, 3, DEFAULT_WEIGHTS)
    assert score >= 0.05
