"""Redis-backed rate limiting with in-memory fallback for local/test."""

from __future__ import annotations

import logging
import time
from collections import defaultdict

from redis.asyncio import Redis

from services.api.config import Settings, get_settings
from services.api.exceptions import RateLimitError

logger = logging.getLogger(__name__)

_memory_buckets: dict[str, list[float]] = defaultdict(list)


async def _redis_check(key: str, limit: int, window_seconds: int, redis: Redis) -> bool:  # type: ignore[type-arg]
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window_seconds)
    return int(count) <= limit


def _memory_check(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    bucket = _memory_buckets[key]
    _memory_buckets[key] = [ts for ts in bucket if now - ts < window_seconds]
    if len(_memory_buckets[key]) >= limit:
        return False
    _memory_buckets[key].append(now)
    return True


async def check_rate_limit(
    *,
    tenant_id: str,
    bucket: str,
    limit: int,
    window_seconds: int = 60,
    request_id: str | None = None,
) -> None:
    settings = get_settings()
    key = f"ratelimit:{bucket}:{tenant_id}"

    try:
        redis = Redis.from_url(settings.redis_url)
        allowed = await _redis_check(key, limit, window_seconds, redis)
        await redis.close()
    except Exception:
        logger.debug("Redis unavailable; using in-memory rate limiter", exc_info=True)
        allowed = _memory_check(key, limit, window_seconds)

    if not allowed:
        raise RateLimitError(request_id=request_id)


def query_limit(settings: Settings | None = None) -> int:
    return (settings or get_settings()).rate_limit_query_per_minute


def bulk_limit(settings: Settings | None = None) -> int:
    return (settings or get_settings()).rate_limit_bulk_per_minute
