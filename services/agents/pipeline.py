"""LangGraph multi-agent pipeline (see AGENTS.md)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Literal, TypedDict, cast

from langgraph.graph import END, StateGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.brief_generation import run_brief_generation_agent
from services.agents.change_detector import run_change_detector
from services.agents.config import get_agent_settings
from services.agents.impact_analysis import run_impact_analysis_agent
from services.agents.llm_client import LLMClient
from services.agents.relevance import run_relevance_agent
from services.agents.schemas import (
    AffectedProfile,
    AgentTraceEntry,
    ChangeEvent,
    ComplianceBrief,
    ImpactDraft,
    PipelineRunResult,
    VerifiedImpact,
)
from services.agents.verification import run_verification_agent
from services.api.models import AgentTrace, Brief, BriefCitation, ClientProfile, Tenant
from services.api.models import ChangeEvent as ChangeEventModel
from services.api.services.notifications import (
    notify_critical_brief,
    notify_critical_review_required,
)
from services.ingestion.severity import ClassifiedChange

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    classified_change: ClassifiedChange
    change_event: ChangeEvent | None
    affected_profiles: list[AffectedProfile]
    impact_drafts: list[ImpactDraft]
    verified_impacts: list[VerifiedImpact]
    briefs: list[ComplianceBrief]
    status: Literal["IN_PROGRESS", "COMPLETE", "LOW_CONFIDENCE", "NO_IMPACT"]
    trace: list[AgentTraceEntry]
    db: AsyncSession
    llm: LLMClient
    change_event_id: uuid.UUID | None
    brief_ids: list[uuid.UUID]


async def _node_change_detector(state: PipelineState) -> PipelineState:
    event, trace = await run_change_detector(state["classified_change"], llm=state["llm"])
    state["change_event"] = event
    state["trace"].append(trace)
    return state


async def _node_relevance(state: PipelineState) -> PipelineState:
    assert state["change_event"] is not None
    affected, trace = await run_relevance_agent(
        state["change_event"],
        llm=state["llm"],
        db=state["db"],
    )
    state["affected_profiles"] = affected
    state["trace"].append(trace)
    if not affected:
        state["status"] = "NO_IMPACT"
    return state


def _route_after_relevance(state: PipelineState) -> str:
    if state["status"] == "NO_IMPACT":
        return "end"
    return "impact_analysis"


async def _node_impact_analysis(state: PipelineState) -> PipelineState:
    assert state["change_event"] is not None
    drafts: list[ImpactDraft] = []
    for profile in state["affected_profiles"]:
        draft, trace = await run_impact_analysis_agent(
            state["change_event"],
            profile,
            db=state["db"],
            llm=state["llm"],
        )
        drafts.append(draft)
        state["trace"].append(trace)
    state["impact_drafts"] = drafts
    return state


async def _node_verification(state: PipelineState) -> PipelineState:
    verified: list[VerifiedImpact] = []
    all_passed = True
    for draft in state["impact_drafts"]:
        result, trace, passed = await run_verification_agent(draft, llm=state["llm"])
        verified.append(result)
        state["trace"].append(trace)
        if not passed:
            all_passed = False
    state["verified_impacts"] = verified
    state["status"] = "COMPLETE" if all_passed else "LOW_CONFIDENCE"
    return state


def _route_after_verification(state: PipelineState) -> str:
    if state["status"] == "LOW_CONFIDENCE":
        return "end"
    return "brief_generation"


async def _node_brief_generation(state: PipelineState) -> PipelineState:
    assert state["change_event"] is not None
    briefs: list[ComplianceBrief] = []
    for verified in state["verified_impacts"]:
        brief, trace = await run_brief_generation_agent(
            state["change_event"],
            verified,
            llm=state["llm"],
        )
        briefs.append(brief)
        state["trace"].append(trace)
    state["briefs"] = briefs
    state["status"] = "COMPLETE"
    return state


def build_pipeline_graph() -> StateGraph:  # type: ignore[type-arg]
    graph = StateGraph(PipelineState)
    graph.add_node("change_detector", _node_change_detector)
    graph.add_node("relevance_agent", _node_relevance)
    graph.add_node("impact_analysis", _node_impact_analysis)
    graph.add_node("verification", _node_verification)
    graph.add_node("brief_generation", _node_brief_generation)

    graph.set_entry_point("change_detector")
    graph.add_edge("change_detector", "relevance_agent")
    graph.add_conditional_edges(
        "relevance_agent",
        _route_after_relevance,
        {"end": END, "impact_analysis": "impact_analysis"},
    )
    graph.add_edge("impact_analysis", "verification")
    graph.add_conditional_edges(
        "verification",
        _route_after_verification,
        {"end": END, "brief_generation": "brief_generation"},
    )
    graph.add_edge("brief_generation", END)
    return graph


async def persist_pipeline_result(state: PipelineState) -> PipelineRunResult:
    db = state["db"]
    classified = state["classified_change"]
    change_event_id = state.get("change_event_id")

    change_row: ChangeEventModel | None = None
    if change_event_id is None:
        change_row = ChangeEventModel(
            id=uuid.uuid4(),
            document_id=classified.document_id,
            clause_id=classified.clause_id,
            change_type=classified.change_type.value,
            severity=classified.severity.value,
            old_text=classified.old_text,
            new_text=classified.new_text,
            effective_date=classified.effective_date,
            source=classified.source,
        )
        db.add(change_row)
        await db.flush()
        change_event_id = change_row.id
        state["change_event_id"] = change_event_id
    else:
        existing = await db.execute(
            select(ChangeEventModel).where(ChangeEventModel.id == change_event_id)
        )
        change_row = existing.scalar_one_or_none()

    brief_ids: list[uuid.UUID] = []
    for brief in state["briefs"]:
        brief_row = Brief(
            id=uuid.uuid4(),
            client_id=uuid.UUID(brief.client_id),
            change_event_id=change_event_id,
            title=brief.title,
            change_summary=brief.change_summary,
            severity=brief.severity,
            obligations=[o.model_dump(mode="json") for o in brief.obligations],
            recommended_actions=brief.recommended_actions,
            confidence=Decimal(str(brief.confidence)),
            status=brief.status,
            disclaimer=brief.disclaimer,
        )
        db.add(brief_row)
        await db.flush()
        brief_ids.append(brief_row.id)

        for citation in brief.citations:
            db.add(
                BriefCitation(
                    id=uuid.uuid4(),
                    brief_id=brief_row.id,
                    clause_id=citation.clause_id,
                    source_url=citation.source_url,
                    excerpt=citation.excerpt,
                )
            )

        if (
            change_row is not None
            and brief_row.severity == "CRITICAL"
            and brief_row.status == "COMPLETE"
        ):
            profile_row = await db.execute(
                select(ClientProfile).where(ClientProfile.id == brief_row.client_id)
            )
            profile = profile_row.scalar_one_or_none()
            if profile is not None:
                tenant_row = await db.execute(select(Tenant).where(Tenant.id == profile.tenant_id))
                tenant = tenant_row.scalar_one_or_none()
                if tenant is not None:
                    await notify_critical_brief(
                        db,
                        brief=brief_row,
                        change_event=change_row,
                        client_profile=profile,
                        tenant=tenant,
                    )

    for entry in state["trace"]:
        trace_row = AgentTrace(
            id=uuid.uuid4(),
            brief_id=brief_ids[0] if brief_ids else None,
            change_event_id=change_event_id,
            agent_name=entry.agent_name,
            input_snapshot=entry.input_snapshot,
            output_snapshot=entry.output_snapshot,
            model_used=entry.model_used,
            prompt_version=entry.prompt_version,
            tokens_in=entry.tokens_in,
            tokens_out=entry.tokens_out,
            latency_ms=entry.latency_ms,
        )
        db.add(trace_row)

    if (
        change_row is not None
        and state["status"] == "LOW_CONFIDENCE"
        and change_row.severity == "CRITICAL"
        and not brief_ids
        and state["affected_profiles"]
    ):
        first_client = uuid.UUID(state["affected_profiles"][0].client_id)
        profile_row = await db.execute(
            select(ClientProfile).where(ClientProfile.id == first_client)
        )
        profile = profile_row.scalar_one_or_none()
        if profile is not None:
            await notify_critical_review_required(
                db,
                change_event=change_row,
                tenant_id=profile.tenant_id,
            )

    await db.commit()
    state["brief_ids"] = brief_ids
    return PipelineRunResult(
        change_event_id=change_event_id,
        brief_ids=brief_ids,
        status=state["status"],
        briefs=state["briefs"],
        trace=state["trace"],
    )


async def run_pipeline(
    classified: ClassifiedChange,
    *,
    db: AsyncSession,
    llm: LLMClient | None = None,
) -> PipelineRunResult:
    llm = llm or LLMClient(max_cost_usd=get_agent_settings().max_cost_per_brief_usd)
    initial: PipelineState = {
        "classified_change": classified,
        "change_event": None,
        "affected_profiles": [],
        "impact_drafts": [],
        "verified_impacts": [],
        "briefs": [],
        "status": "IN_PROGRESS",
        "trace": [],
        "db": db,
        "llm": llm,
        "change_event_id": None,
        "brief_ids": [],
    }
    graph = build_pipeline_graph().compile()
    final_state = cast(PipelineState, await graph.ainvoke(initial))
    return await persist_pipeline_result(final_state)
