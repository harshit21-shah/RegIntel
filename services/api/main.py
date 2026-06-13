"""FastAPI application entrypoint."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.config import get_settings
from services.api.handlers import register_exception_handlers
from services.api.middleware.request_id import RequestIdMiddleware
from services.api.middleware.security import LogScrubFilter, SecurityHeadersMiddleware
from services.api.routers.admin import router as admin_router
from services.api.routers.auth import router as auth_router
from services.api.routers.briefs import router as briefs_router
from services.api.routers.changes import router as changes_router
from services.api.routers.consultant import router as consultant_router
from services.api.routers.feedback import router as feedback_router
from services.api.routers.health import router as health_router
from services.api.routers.profiles import router as profiles_router
from services.api.routers.query import router as query_router
from services.api.services.bootstrap import schedule_search_bootstrap


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.getLogger().addFilter(LogScrubFilter())
    logging.basicConfig(level=settings.log_level)
    schedule_search_bootstrap()
    yield


app = FastAPI(
    title="RegIntel API",
    description="GraphRAG regulatory change-intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(query_router)
app.include_router(briefs_router)
app.include_router(changes_router)
app.include_router(feedback_router)
app.include_router(consultant_router)
app.include_router(admin_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "regintel-api", "docs": "/docs", "version": "1.0.0"}
