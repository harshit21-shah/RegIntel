"""Health and readiness endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from neo4j import AsyncGraphDatabase
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.config import Settings, get_settings
from services.api.db import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    checks: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["postgres"] = f"error: {exc}"

    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )
    try:
        async with driver.session() as session:
            await session.run("RETURN 1")
        checks["neo4j"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["neo4j"] = f"error: {exc}"
    finally:
        await driver.close()

    qdrant = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        collections = await qdrant.get_collections()
        names = {collection.name for collection in collections.collections}
        if settings.qdrant_collection in names:
            info = await qdrant.get_collection(settings.qdrant_collection)
            points = int(info.points_count or 0)
            checks["qdrant"] = "ok" if points > 0 else f"empty ({points} points)"
        else:
            checks["qdrant"] = "collection missing"
    except Exception as exc:  # noqa: BLE001
        checks["qdrant"] = f"error: {exc}"
    finally:
        await qdrant.close()

    redis = Redis.from_url(settings.redis_url)
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc}"
    finally:
        await redis.close()

    all_ok = all(value == "ok" for value in checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
