"""Admin endpoints for cost dashboards and internal monitoring."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.config import get_settings
from services.api.db import get_db
from services.api.deps import require_roles
from services.api.models import AgentTrace, EvalRun, Feedback, LLMUsage, RelevanceWeight
from services.api.services.ingestion_status import latest_runs_by_source

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.get("/trends")
async def admin_trends(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Daily eval accuracy and cost-per-brief series for admin charts."""
    now = datetime.now(tz=UTC)
    eval_points: list[dict[str, object]] = []
    cost_points: list[dict[str, object]] = []

    for offset in range(days - 1, -1, -1):
        day_start = (now - timedelta(days=offset)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        label = day_start.strftime("%a")

        eval_result = await db.execute(
            select(EvalRun)
            .where(EvalRun.created_at >= day_start, EvalRun.created_at < day_end)
            .order_by(EvalRun.created_at.desc())
            .limit(1)
        )
        eval_run = eval_result.scalar_one_or_none()
        if eval_run is not None:
            eval_points.append(
                {
                    "date": label,
                    "accuracy": float(eval_run.accuracy),
                    "cases": eval_run.cases,
                }
            )

        day_cost = await db.scalar(
            select(func.coalesce(func.sum(LLMUsage.cost_usd), 0))
            .select_from(AgentTrace)
            .join(LLMUsage, LLMUsage.trace_id == AgentTrace.id)
            .where(
                AgentTrace.agent_name == "brief_generation",
                AgentTrace.created_at >= day_start,
                AgentTrace.created_at < day_end,
            )
        )
        brief_count = await db.scalar(
            select(func.count())
            .select_from(AgentTrace)
            .where(
                AgentTrace.agent_name == "brief_generation",
                AgentTrace.created_at >= day_start,
                AgentTrace.created_at < day_end,
            )
        )
        briefs = int(brief_count or 0)
        cost_points.append(
            {
                "date": label,
                "cost_per_brief": round(float(day_cost or 0) / max(1, briefs), 4),
                "briefs": briefs,
            }
        )

    return {"period_days": days, "eval": eval_points, "cost": cost_points}


@router.get("/cost/summary")
async def cost_summary(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    since = datetime.now(tz=UTC) - timedelta(days=days)
    total_cost = await db.scalar(
        select(func.coalesce(func.sum(LLMUsage.cost_usd), 0)).where(LLMUsage.created_at >= since)
    )
    brief_count = await db.scalar(
        select(func.count())
        .select_from(AgentTrace)
        .where(
            AgentTrace.agent_name == "brief_generation",
            AgentTrace.created_at >= since,
        )
    )
    cost = float(total_cost or 0)
    briefs = int(brief_count or 0)
    settings = get_settings()
    return {
        "period_days": days,
        "total_cost_usd": round(cost, 4),
        "briefs_generated": briefs,
        "cost_per_brief_usd": round(cost / max(1, briefs), 4),
        "target_cost_per_brief_usd": 0.50,
        "tenant_daily_cap_usd": settings.tenant_daily_cost_cap_usd,
        "global_daily_cap_usd": settings.global_daily_cost_cap_usd,
    }


@router.get("/cost/by-agent")
async def cost_by_agent(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    since = datetime.now(tz=UTC) - timedelta(days=days)
    result = await db.execute(
        select(AgentTrace.agent_name, func.sum(LLMUsage.cost_usd), func.count())
        .join(LLMUsage, LLMUsage.trace_id == AgentTrace.id)
        .where(AgentTrace.created_at >= since)
        .group_by(AgentTrace.agent_name)
    )
    items = [
        {
            "agent_name": row[0],
            "total_cost_usd": round(float(row[1] or 0), 4),
            "call_count": int(row[2] or 0),
        }
        for row in result.all()
    ]
    return {"period_days": days, "items": items}


@router.get("/eval/latest")
async def eval_latest(db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    result = await db.execute(select(EvalRun).order_by(EvalRun.created_at.desc()).limit(1))
    run = result.scalar_one_or_none()
    if run is None:
        return {
            "status": "no_runs",
            "message": "No eval runs recorded yet. Run make eval-pipeline.",
        }
    return {
        "suite": run.suite,
        "cases": run.cases,
        "accuracy": float(run.accuracy),
        "threshold": float(run.threshold),
        "passed": run.passed,
        "created_at": run.created_at.isoformat(),
        "failures": [item for item in run.details if not item.get("correct")],
    }


@router.get("/ingestion/status")
async def ingestion_status(db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    settings = get_settings()
    runs = await latest_runs_by_source(db)
    now = datetime.now(tz=UTC)
    items: list[dict[str, object]] = []
    for run in runs:
        completed = run.completed_at or run.started_at
        age_hours = (now - completed).total_seconds() / 3600
        stale = age_hours > settings.ingestion_staleness_hours and run.status != "RUNNING"
        items.append(
            {
                "source": run.source,
                "status": run.status,
                "document_count": run.document_count,
                "last_success_at": completed.isoformat(),
                "age_hours": round(age_hours, 1),
                "stale": stale,
                "error_message": run.error_message,
            }
        )
    return {
        "staleness_threshold_hours": settings.ingestion_staleness_hours,
        "sources": items,
    }


@router.get("/feedback/summary")
async def feedback_summary(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    since = datetime.now(tz=UTC) - timedelta(days=days)
    total = await db.scalar(
        select(func.count()).select_from(Feedback).where(Feedback.created_at >= since)
    )
    not_relevant = await db.scalar(
        select(func.count())
        .select_from(Feedback)
        .where(Feedback.created_at >= since, Feedback.rating == "NOT_RELEVANT")
    )
    helpful = await db.scalar(
        select(func.count())
        .select_from(Feedback)
        .where(Feedback.created_at >= since, Feedback.rating == "HELPFUL")
    )
    inaccurate = await db.scalar(
        select(func.count())
        .select_from(Feedback)
        .where(Feedback.created_at >= since, Feedback.rating == "INACCURATE")
    )
    total_count = int(total or 0)
    fp_count = int(not_relevant or 0)
    fp_rate = round(fp_count / max(1, total_count), 4)
    return {
        "period_days": days,
        "total_feedback": total_count,
        "helpful": int(helpful or 0),
        "not_relevant": fp_count,
        "inaccurate": int(inaccurate or 0),
        "false_positive_rate": fp_rate,
        "threshold_warning": fp_rate > 0.15,
    }


@router.get("/relevance/weights")
async def relevance_weights(db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    result = await db.execute(
        select(RelevanceWeight).order_by(RelevanceWeight.edge_type, RelevanceWeight.hop_depth)
    )
    items = [
        {
            "edge_type": row.edge_type,
            "hop_depth": row.hop_depth,
            "naics_code": row.naics_code,
            "weight": float(row.weight),
            "updated_at": row.updated_at.isoformat(),
        }
        for row in result.scalars().all()
    ]
    return {"items": items, "count": len(items)}
