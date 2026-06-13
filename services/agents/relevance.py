"""Relevance Agent — multi-hop graph traversal with feedback weights + LightGBM."""

from __future__ import annotations

import logging

from neo4j import AsyncGraphDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.llm_client import LLMClient
from services.agents.relevance_model import RelevanceFeatures, RelevanceRanker
from services.agents.relevance_weights import apply_hop_weight, load_weights
from services.agents.schemas import AffectedProfile, AgentTraceEntry, ChangeEvent
from services.api.config import Settings, get_settings

logger = logging.getLogger(__name__)

RELEVANCE_CYPHER = """
MATCH (c:Clause {clause_id: $clause_id})-[:PART_OF]->(r:Regulation)
OPTIONAL MATCH path = (r)-[:AMENDS|REFERENCES*0..3]-(related:Regulation)
WITH c, r, related, coalesce(length(path), 0) AS hops
OPTIONAL MATCH (related)-[:APPLIES_TO]->(bc:BusinessCategory)
WITH DISTINCT bc, hops
WHERE bc IS NOT NULL
MATCH (cp:ClientProfile)-[:CLASSIFIED_AS]->(bc)
OPTIONAL MATCH (cp)-[:OPERATES_IN]->(j:Jurisdiction)
WITH cp, bc, hops, collect(j.code) AS jurisdictions
RETURN cp.client_id AS client_id,
       bc.naics_code AS naics_code,
       hops AS hops,
       jurisdictions AS jurisdictions
ORDER BY hops ASC
"""


async def run_relevance_agent(
    change_event: ChangeEvent,
    *,
    llm: LLMClient | None = None,
    settings: Settings | None = None,
    db: AsyncSession | None = None,
) -> tuple[list[AffectedProfile], AgentTraceEntry]:
    settings = settings or get_settings()
    weights = await load_weights(db) if db is not None else await load_weights_from_defaults()
    ranker = RelevanceRanker()

    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    profiles: dict[str, AffectedProfile] = {}

    try:
        async with driver.session() as session:
            result = await session.run(RELEVANCE_CYPHER, clause_id=change_event.clause_id)
            async for record in result:
                client_id = str(record["client_id"])
                hops = int(record["hops"] or 0)
                base = max(0.1, 1.0 - (hops * 0.15))
                weighted = apply_hop_weight(base, hops, weights)
                naics = str(record["naics_code"])
                jurisdictions = record["jurisdictions"] or []
                jurisdiction_match = 1.0 if jurisdictions else 0.5

                features = RelevanceFeatures(
                    hop_count=hops,
                    base_score=base,
                    matched_category_count=1,
                    weight_multiplier=weighted / max(base, 0.01),
                    jurisdiction_match=jurisdiction_match,
                )
                score = ranker.score(features)

                hop_path = [change_event.clause_id, naics]
                if client_id in profiles:
                    existing = profiles[client_id]
                    profiles[client_id] = existing.model_copy(
                        update={
                            "relevance_score": max(existing.relevance_score, score),
                            "matched_categories": list(set(existing.matched_categories + [naics])),
                            "hop_path": existing.hop_path + [naics],
                        }
                    )
                else:
                    profiles[client_id] = AffectedProfile(
                        client_id=client_id,
                        relevance_score=score,
                        hop_path=hop_path,
                        matched_categories=[naics],
                    )
    finally:
        await driver.close()

    affected = sorted(profiles.values(), key=lambda p: p.relevance_score, reverse=True)

    model_used = "cypher+ranker"
    tokens_in = 0
    tokens_out = 0
    latency_ms = 0
    if (
        llm is not None
        and affected
        and (llm.budget_remaining_usd is None or llm.budget_remaining_usd > 0.05)
    ):
        try:
            response = await llm.complete(
                "Explain in one sentence why these client profiles are affected by "
                f"regulatory change {change_event.clause_id}.",
                tier="haiku",
                prompt_version="relevance-v2",
            )
            affected[0] = affected[0].model_copy(
                update={"path_explanation": response.content.strip()}
            )
            model_used = response.model
            tokens_in = response.tokens_in
            tokens_out = response.tokens_out
            latency_ms = response.latency_ms
        except Exception:
            logger.warning("Hop path explanation failed", exc_info=True)

    trace = AgentTraceEntry(
        agent_name="relevance_agent",
        input_snapshot=change_event.model_dump(mode="json"),
        output_snapshot={"affected_profiles": [p.model_dump(mode="json") for p in affected]},
        model_used=model_used,
        prompt_version="relevance-v2",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
    )
    return affected, trace


async def load_weights_from_defaults() -> dict[tuple[str, int], float]:
    from services.agents.relevance_weights import DEFAULT_WEIGHTS

    return DEFAULT_WEIGHTS.copy()
