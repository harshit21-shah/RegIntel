"""Feedback-driven relevance edge weights (heuristic v1)."""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models import AgentTrace, Brief, Feedback, RelevanceWeight

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS: dict[tuple[str, int], float] = {
    ("APPLIES_TO", 0): 1.0,
    ("APPLIES_TO", 1): 0.9,
    ("REFERENCES", 1): 0.85,
    ("REFERENCES", 2): 0.7,
    ("REFERENCES", 3): 0.55,
    ("AMENDS", 1): 0.8,
    ("AMENDS", 2): 0.65,
    ("AMENDS", 3): 0.5,
}


async def load_weights(db: AsyncSession) -> dict[tuple[str, int], float]:
    result = await db.execute(select(RelevanceWeight))
    rows = result.scalars().all()
    if not rows:
        return DEFAULT_WEIGHTS.copy()
    weights: dict[tuple[str, int], float] = {}
    for row in rows:
        key = (row.edge_type, row.hop_depth)
        weights[key] = float(row.weight)
    return weights


def apply_hop_weight(base_score: float, hops: int, weights: dict[tuple[str, int], float]) -> float:
    edge_type = "REFERENCES" if hops > 0 else "APPLIES_TO"
    depth = min(hops, 3)
    multiplier = weights.get((edge_type, depth), weights.get(("APPLIES_TO", 0), 1.0))
    return max(0.05, min(1.0, base_score * multiplier))


async def adjust_weights_from_feedback(
    db: AsyncSession, feedback_id: uuid.UUID | None = None
) -> int:
    """Decrement weights for hop patterns associated with NOT_RELEVANT feedback."""
    query = (
        select(Feedback, Brief, AgentTrace)
        .join(Brief, Feedback.brief_id == Brief.id)
        .join(AgentTrace, AgentTrace.change_event_id == Brief.change_event_id)
        .where(Feedback.rating == "NOT_RELEVANT")
        .where(AgentTrace.agent_name == "relevance_agent")
    )
    if feedback_id is not None:
        query = query.where(Feedback.id == feedback_id)
    result = await db.execute(query)
    updated = 0
    for feedback, _brief, trace in result.all():
        if feedback.hop_path is not None and feedback_id is None:
            continue
        output = trace.output_snapshot
        profiles = output.get("affected_profiles", [])
        if not profiles:
            continue
        profile_data = profiles[0]
        hop_path = profile_data.get("hop_path", [])
        feedback.hop_path = hop_path
        hops = max(0, len(hop_path) - 2)
        edge_type = "REFERENCES" if hops > 0 else "APPLIES_TO"
        depth = min(hops, 3)
        naics_code = profile_data.get("naics_code")

        existing = await db.execute(
            select(RelevanceWeight).where(
                RelevanceWeight.edge_type == edge_type,
                RelevanceWeight.hop_depth == depth,
                RelevanceWeight.naics_code == naics_code,
            )
        )
        row = existing.scalar_one_or_none()
        if row is None:
            current = DEFAULT_WEIGHTS.get((edge_type, depth), 1.0)
            row = RelevanceWeight(
                id=uuid.uuid4(),
                edge_type=edge_type,
                hop_depth=depth,
                naics_code=naics_code,
                weight=Decimal(str(round(current * 0.9, 4))),
            )
            db.add(row)
        else:
            row.weight = Decimal(str(max(0.1, float(row.weight) * 0.9)))
        updated += 1

    await db.commit()
    logger.info("Adjusted relevance weights from %d feedback records", updated)
    return updated
