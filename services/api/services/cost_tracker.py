"""Track daily LLM spend per tenant in Redis."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from redis.asyncio import Redis

from services.api.config import Settings, get_settings
from services.api.exceptions import LLMBudgetExceededError

logger = logging.getLogger(__name__)

_memory_costs: dict[str, float] = {}


def _day_key(tenant_id: str | None) -> str:
    day = datetime.now(tz=UTC).strftime("%Y%m%d")
    tenant = tenant_id or "global"
    return f"llm_cost:{day}:{tenant}"


async def check_and_add_cost(
    amount_usd: float,
    *,
    tenant_id: str | None = None,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    tenant_key = _day_key(tenant_id)
    global_key = _day_key(None)

    try:
        redis = Redis.from_url(settings.redis_url)
        tenant_total = float(await redis.incrbyfloat(tenant_key, amount_usd))
        global_total = float(await redis.incrbyfloat(global_key, amount_usd))
        if tenant_id:
            await redis.expire(tenant_key, 86400)
        await redis.expire(global_key, 86400)
        await redis.close()
    except Exception:
        logger.debug("Redis unavailable for cost tracking; using in-memory fallback", exc_info=True)
        _memory_costs[tenant_key] = _memory_costs.get(tenant_key, 0.0) + amount_usd
        _memory_costs[global_key] = _memory_costs.get(global_key, 0.0) + amount_usd
        tenant_total = _memory_costs[tenant_key]
        global_total = _memory_costs[global_key]

    if tenant_id and tenant_total > settings.tenant_daily_cost_cap_usd:
        raise LLMBudgetExceededError(
            f"Tenant daily cost cap exceeded ({settings.tenant_daily_cost_cap_usd} USD)"
        )
    if global_total > settings.global_daily_cost_cap_usd:
        raise LLMBudgetExceededError(
            f"Global daily cost cap exceeded ({settings.global_daily_cost_cap_usd} USD)"
        )
