"""Weekly false-positive report for design partner feedback."""

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from services.api.db import AsyncSessionLocal
from services.api.models import Feedback

logger = logging.getLogger(__name__)


async def run_report(*, days: int = 7) -> dict[str, object]:
    since = datetime.now(tz=UTC) - timedelta(days=days)
    async with AsyncSessionLocal() as db:
        total = await db.scalar(
            select(func.count()).select_from(Feedback).where(Feedback.created_at >= since)
        )
        not_relevant = await db.scalar(
            select(func.count())
            .select_from(Feedback)
            .where(Feedback.created_at >= since, Feedback.rating == "NOT_RELEVANT")
        )
        recent_comments = await db.execute(
            select(Feedback.comment, Feedback.hop_path, Feedback.created_at)
            .where(Feedback.created_at >= since, Feedback.rating == "NOT_RELEVANT")
            .order_by(Feedback.created_at.desc())
            .limit(10)
        )

    total_count = int(total or 0)
    fp_count = int(not_relevant or 0)
    fp_rate = fp_count / max(1, total_count)
    comments = [
        {
            "comment": row[0],
            "hop_path": row[1],
            "created_at": row[2].isoformat() if row[2] else None,
        }
        for row in recent_comments.all()
        if row[0]
    ]
    return {
        "period_days": days,
        "total_feedback": total_count,
        "not_relevant": fp_count,
        "false_positive_rate": round(fp_rate, 4),
        "threshold_warning": fp_rate > 0.15,
        "recent_comments": comments,
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    report = await run_report(days=args.days)
    print("RegIntel weekly false-positive report")
    print(f"Period: {report['period_days']} days")
    print(f"Total feedback: {report['total_feedback']}")
    print(f"NOT_RELEVANT: {report['not_relevant']}")
    print(f"False-positive rate: {report['false_positive_rate']:.1%}")
    if report["threshold_warning"]:
        print("WARNING: FP rate exceeds 15% threshold")
    for item in report["recent_comments"]:
        print(f"- {item['created_at']}: {item['comment']}")


if __name__ == "__main__":
    asyncio.run(main())
