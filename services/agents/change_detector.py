"""Change-Detector Agent."""

from __future__ import annotations

import logging

from services.agents.llm_client import LLMClient
from services.agents.schemas import AgentTraceEntry, ChangeEvent
from services.ingestion.severity import ClassifiedChange

logger = logging.getLogger(__name__)


async def run_change_detector(
    classified: ClassifiedChange,
    *,
    llm: LLMClient | None = None,
) -> tuple[ChangeEvent, AgentTraceEntry]:
    event = ChangeEvent(
        document_id=classified.document_id,
        clause_id=classified.clause_id,
        change_type=classified.change_type.value,
        severity=classified.severity.value,
        old_text=classified.old_text,
        new_text=classified.new_text,
        effective_date=classified.effective_date,
        source=classified.source,
    )

    summary: str | None = None
    model_used = "none"
    tokens_in = 0
    tokens_out = 0
    latency_ms = 0

    if llm is not None:
        prompt = (
            "Summarize this regulatory clause change in 1-2 plain-English sentences.\n"
            f"Clause: {classified.clause_id}\n"
            f"Change type: {classified.change_type}\n"
            f"Old: {classified.old_text or 'N/A'}\n"
            f"New: {classified.new_text or 'N/A'}"
        )
        try:
            response = await llm.complete(
                prompt,
                tier="haiku",
                prompt_version="change-detector-v1",
            )
            summary = response.content.strip()
            model_used = response.model
            tokens_in = response.tokens_in
            tokens_out = response.tokens_out
            latency_ms = response.latency_ms
        except Exception:
            logger.warning("Change summary generation failed", exc_info=True)

    event.change_summary = summary
    trace = AgentTraceEntry(
        agent_name="change_detector",
        input_snapshot=classified.model_dump(mode="json"),
        output_snapshot=event.model_dump(mode="json"),
        model_used=model_used,
        prompt_version="change-detector-v1",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
    )
    return event, trace
