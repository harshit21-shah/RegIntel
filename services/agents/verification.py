"""Verification Agent — independent citation verification gate."""

from __future__ import annotations

import json
import logging

from services.agents.config import get_agent_settings
from services.agents.llm_client import LLMClient
from services.agents.schemas import AgentTraceEntry, ImpactDraft, Obligation, VerifiedImpact
from services.agents.tools import fetch_clause

logger = logging.getLogger(__name__)


async def _verify_obligation(
    obligation: Obligation, llm: LLMClient
) -> tuple[Obligation | None, str | None, str | None]:
    """Returns (verified_obligation, removed_claim_text, stale_clause_id)."""
    if not obligation.citation_clause_ids:
        return None, obligation.text, None

    supported = 0
    total = 0
    verified = obligation.model_copy(deep=True)

    for clause_id in obligation.citation_clause_ids:
        clause_text = await fetch_clause(clause_id)
        if not clause_text:
            # Clause cited by Impact-Analysis no longer resolves — likely repealed
            # or superseded between pipeline stages. This is a STALE_REFERENCE, not
            # an unsupported claim; the brief should be re-run on fresh graph state.
            return None, obligation.text, clause_id

        total += 1
        prompt = (
            "Determine if the CLAIM is supported by the CLAUSE TEXT.\n"
            'Respond JSON: {"verdict":"SUPPORTED|PARTIALLY_SUPPORTED|UNSUPPORTED"}\n\n'
            f"CLAIM: {obligation.text}\n\n"
            f"<source_document>\n{clause_text}\n</source_document>"
        )
        response = await llm.complete(
            prompt,
            tier="sonnet",
            system="You are an independent verification judge. Be strict.",
            prompt_version="verification-v1",
            max_tokens=256,
        )
        try:
            verdict = json.loads(response.content).get("verdict", "UNSUPPORTED")
        except json.JSONDecodeError:
            verdict = "UNSUPPORTED"

        if verdict in {"SUPPORTED", "PARTIALLY_SUPPORTED"}:
            supported += 1
        else:
            return None, obligation.text, None

    if total == 0:
        return None, obligation.text, None
    return verified, None, None


async def run_verification_agent(
    draft: ImpactDraft,
    *,
    llm: LLMClient,
) -> tuple[VerifiedImpact, AgentTraceEntry, bool]:
    settings = get_agent_settings()
    verified_obligations: list[Obligation] = []
    removed: list[str] = []
    stale: list[str] = []

    for obligation in draft.obligations:
        verified, removed_text, stale_clause = await _verify_obligation(obligation, llm)
        if verified is not None:
            verified_obligations.append(verified)
        elif removed_text:
            removed.append(removed_text)
        if stale_clause:
            stale.append(stale_clause)

    total_claims = max(1, len(draft.obligations))
    confidence = len(verified_obligations) / total_claims
    passed = confidence >= settings.verification_threshold and len(verified_obligations) > 0

    result = VerifiedImpact(
        client_id=draft.client_id,
        verified_obligations=verified_obligations,
        confidence=round(confidence, 3),
        unsupported_claims_removed=removed,
        stale_references=stale,
    )
    trace = AgentTraceEntry(
        agent_name="verification",
        input_snapshot=draft.model_dump(mode="json"),
        output_snapshot=result.model_dump(mode="json"),
        model_used="sonnet",
        prompt_version="verification-v1",
    )
    return result, trace, passed
