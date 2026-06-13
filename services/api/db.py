"""Async SQLAlchemy engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from services.api.config import get_settings

settings = get_settings()

_engine_kwargs: dict[str, object] = {
    "echo": settings.app_env == "local",
    "pool_pre_ping": True,
}
if settings.app_env == "test":
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(
    settings.database_url,
    **_engine_kwargs,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
