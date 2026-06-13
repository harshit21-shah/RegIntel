"""Ensure disclaimer is present in brief schema."""

from datetime import UTC, datetime

from services.agents.prompts.disclaimers import REGINTEL_DISCLAIMER
from services.agents.schemas import ComplianceBrief, Obligation


def test_compliance_brief_includes_disclaimer() -> None:
    brief = ComplianceBrief(
        client_id="00000000-0000-0000-0000-000000000001",
        title="Test Brief",
        change_summary="Summary",
        severity="CRITICAL",
        obligations=[Obligation(text="Do something", citation_clause_ids=["ecfr:21:101:101.1"])],
        recommended_actions=["Review with counsel"],
        citations=[],
        confidence=0.95,
        generated_at=datetime.now(tz=UTC),
        disclaimer=REGINTEL_DISCLAIMER,
    )
    assert "not a substitute for legal advice" in brief.disclaimer
