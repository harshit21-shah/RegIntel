"""Export feedback + relevance traces as LightGBM training labels."""

from __future__ import annotations

import argparse
import asyncio
import csv
import logging
from pathlib import Path

from sqlalchemy import select

from services.agents.relevance_model import RelevanceFeatures
from services.api.db import AsyncSessionLocal
from services.api.models import AgentTrace, Brief, Feedback

logger = logging.getLogger(__name__)


async def export_labels(output: Path) -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Feedback, Brief, AgentTrace)
            .join(Brief, Feedback.brief_id == Brief.id)
            .join(AgentTrace, AgentTrace.change_event_id == Brief.change_event_id)
            .where(AgentTrace.agent_name == "relevance_agent")
        )
        rows = result.all()

    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "feedback_id",
                "rating",
                "hop_count",
                "base_score",
                "matched_category_count",
                "weight_multiplier",
                "jurisdiction_match",
                "label",
            ]
        )
        for feedback, _brief, trace in rows:
            profiles = trace.output_snapshot.get("affected_profiles", [])
            if not profiles:
                continue
            profile = profiles[0]
            features = RelevanceFeatures(
                hop_count=max(0, len(profile.get("hop_path", [])) - 2),
                base_score=float(profile.get("relevance_score", 0.5)),
                matched_category_count=1,
                weight_multiplier=1.0,
                jurisdiction_match=1.0,
            )
            label = 0 if feedback.rating == "NOT_RELEVANT" else 1
            writer.writerow(
                [
                    str(feedback.id),
                    feedback.rating,
                    features.hop_count,
                    features.base_score,
                    features.matched_category_count,
                    features.weight_multiplier,
                    features.jurisdiction_match,
                    label,
                ]
            )
            count += 1

    logger.info("Exported %d label rows to %s", count, output)
    return count


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/feedback_labels.csv")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    await export_labels(Path(args.output))


if __name__ == "__main__":
    asyncio.run(main())
