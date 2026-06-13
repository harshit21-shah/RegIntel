"""Unit tests for LLM client."""

from decimal import Decimal

from services.agents.llm_client import estimate_cost


def test_estimate_cost_haiku() -> None:
    cost = estimate_cost("claude-3-5-haiku-20241022", tokens_in=1000, tokens_out=500)
    assert cost == Decimal("0.0028")


def test_estimate_cost_unknown_model_uses_default_rates() -> None:
    cost = estimate_cost("unknown-model", tokens_in=1_000_000, tokens_out=0)
    assert cost == Decimal("1.0")


def test_estimate_cost_groq_haiku() -> None:
    cost = estimate_cost("llama-3.1-8b-instant", tokens_in=1_000_000, tokens_out=1_000_000)
    assert cost == Decimal("0.13")
