"""Optional Langfuse tracing integration."""

from __future__ import annotations

import logging
from typing import Any

from services.api.config import Settings

logger = logging.getLogger(__name__)
_langfuse_client: Any = None


def get_langfuse(settings: Settings) -> Any | None:
    global _langfuse_client
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None
    if _langfuse_client is None:
        try:
            from langfuse import Langfuse

            _langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
        except ImportError:
            logger.warning("langfuse package not installed; tracing disabled")
            return None
    return _langfuse_client


def trace_generation(
    settings: Settings,
    *,
    name: str,
    prompt: str,
    response: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
    metadata: dict[str, object] | None = None,
) -> None:
    langfuse = get_langfuse(settings)
    if langfuse is None:
        return
    try:
        trace = langfuse.trace(name=name, metadata=metadata or {})
        trace.generation(
            name=name,
            model=model,
            input=prompt,
            output=response,
            usage={"input": tokens_in, "output": tokens_out},
            metadata={"latency_ms": latency_ms},
        )
    except Exception:
        logger.warning("Langfuse trace failed", exc_info=True)
