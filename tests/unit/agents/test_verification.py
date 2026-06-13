"""Tests for the Verification Agent gate, incl. stale-reference handling."""

from __future__ import annotations

import services.agents.verification as verification
from services.agents.schemas import ImpactDraft, Obligation


class _UnusedLLM:
    async def complete(self, *args: object, **kwargs: object) -> object:  # pragma: no cover
        raise AssertionError("LLM should not be called when the clause is missing")


async def test_missing_clause_is_reported_as_stale_reference(monkeypatch) -> None:
    async def _fetch_none(_clause_id: str) -> str | None:
        return None

    monkeypatch.setattr(verification, "fetch_clause", _fetch_none)

    draft = ImpactDraft(
        client_id="c1",
        summary="draft",
        obligations=[
            Obligation(text="Must file by 2026-09-01.", citation_clause_ids=["ecfr:21:1:1450"])
        ],
        status="DRAFTED",
    )

    result, _trace, passed = await verification.run_verification_agent(draft, llm=_UnusedLLM())

    assert passed is False
    assert result.verified_obligations == []
    assert result.stale_references == ["ecfr:21:1:1450"]
    # Stale (clause vanished) is distinct from a claim that exists but isn't supported.
    assert "Must file by 2026-09-01." in result.unsupported_claims_removed
