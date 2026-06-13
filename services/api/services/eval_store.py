"""Persist eval run results for admin dashboards."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from services.api.models import EvalRun
from services.eval.entailment.harness import EntailmentResult


async def persist_eval_run(
    db: AsyncSession,
    *,
    suite: str,
    results: list[EntailmentResult],
    accuracy: float,
    threshold: float,
) -> EvalRun:
    passed = accuracy >= threshold
    run = EvalRun(
        id=uuid.uuid4(),
        suite=suite,
        cases=len(results),
        accuracy=Decimal(str(round(accuracy, 4))),
        threshold=Decimal(str(round(threshold, 4))),
        passed=passed,
        details=[
            {
                "case_id": item.case_id,
                "expected": item.expected,
                "predicted": item.predicted,
                "correct": item.correct,
            }
            for item in results
        ],
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
