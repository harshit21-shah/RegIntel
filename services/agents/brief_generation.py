"""Brief-Generation Agent."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from services.agents.llm_client import LLMClient
from services.agents.prompts.disclaimers import REGINTEL_DISCLAIMER
from services.agents.schemas import (
    AgentTraceEntry,
    ChangeEvent,
    CitationRef,
    ComplianceBrief,
    VerifiedImpact,
)
from services.agents.tools import fetch_clause

logger = logging.getLogger(__name__)


async def run_brief_generation_agent(
    change_event: ChangeEvent,
    verified: VerifiedImpact,
    *,
    llm: LLMClient,
) -> tuple[ComplianceBrief, AgentTraceEntry]:
    prompt = (
        "Generate a client-facing compliance brief as JSON with keys: "
        "title, change_summary, recommended_actions (list of strings).\n"
        f"Severity: {change_event.severity}\n"
        f"Verified obligations: {verified.model_dump_json()}\n"
        f"Original change summary: {change_event.change_summary or change_event.new_text}"
    )
    response = await llm.complete(
        prompt,
        tier="sonnet",
        system="Produce structured JSON only.",
        prompt_version="brief-generation-v1",
        max_tokens=2048,
    )

    try:
        payload = json.loads(response.content)
        title = payload["title"]
        change_summary = payload["change_summary"]
        recommended_actions = payload.get("recommended_actions", [])
    except (json.JSONDecodeError, KeyError):
        title = f"Regulatory Change Alert: {change_event.clause_id}"
        change_summary = change_event.change_summary or "A regulatory change was detected."
        recommended_actions = ["Review the cited clauses with your compliance team."]

    citations: list[CitationRef] = []
    for obligation in verified.verified_obligations:
        for clause_id in obligation.citation_clause_ids:
            text = await fetch_clause(clause_id) or obligation.text[:500]
            citations.append(
                CitationRef(
                    clause_id=clause_id,
                    source_url=f"https://www.ecfr.gov/current/title-21/section-{clause_id.split(':')[-1]}",
                    excerpt=text[:500],
                )
            )

    brief = ComplianceBrief(
        client_id=verified.client_id,
        title=title,
        change_summary=change_summary,
        severity=change_event.severity,
        obligations=verified.verified_obligations,
        recommended_actions=recommended_actions,
        citations=citations,
        confidence=verified.confidence,
        generated_at=datetime.now(tz=UTC),
        disclaimer=REGINTEL_DISCLAIMER,
        status="COMPLETE",
    )
    trace = AgentTraceEntry(
        agent_name="brief_generation",
        input_snapshot={
            "change_event": change_event.model_dump(mode="json"),
            "verified_impact": verified.model_dump(mode="json"),
        },
        output_snapshot=brief.model_dump(mode="json"),
        model_used=response.model,
        prompt_version="brief-generation-v1",
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        latency_ms=response.latency_ms,
    )
    return brief, trace
