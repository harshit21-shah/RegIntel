"""Centralized LLM client with provider routing, retries, and cost logging."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
from uuid import UUID

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from services.agents.config import get_agent_settings
from services.api.config import Settings, get_settings

logger = logging.getLogger(__name__)

ModelTier = Literal["haiku", "sonnet"]
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int
    cost_usd: Decimal


# Approximate USD per 1M tokens (input, output) — update as pricing changes.
COST_TABLE: dict[str, tuple[float, float]] = {
    "claude-3-5-haiku-20241022": (0.80, 4.00),
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "llama-3.1-8b-instant": (0.05, 0.08),
    "llama-3.3-70b-versatile": (0.59, 0.79),
}


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> Decimal:
    input_rate, output_rate = COST_TABLE.get(model, (1.0, 3.0))
    cost = (tokens_in * input_rate + tokens_out * output_rate) / 1_000_000
    return Decimal(str(round(cost, 6)))


class LLMClient:
    """Routes LLM calls through the configured primary provider with automatic fallback."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        max_cost_usd: float | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._anthropic: AsyncAnthropic | None = None
        self._openai: AsyncOpenAI | None = None
        self._groq: AsyncOpenAI | None = None
        self.max_cost_usd = max_cost_usd or get_agent_settings().max_cost_per_brief_usd
        self.accumulated_cost_usd: float = 0.0

    @property
    def budget_remaining_usd(self) -> float | None:
        if self.max_cost_usd is None:
            return None
        return max(0.0, self.max_cost_usd - self.accumulated_cost_usd)

    @property
    def anthropic(self) -> AsyncAnthropic:
        if self._anthropic is None:
            if not self.settings.anthropic_api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not configured")
            self._anthropic = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        return self._anthropic

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            if not self.settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY is not configured")
            self._openai = AsyncOpenAI(api_key=self.settings.openai_api_key)
        return self._openai

    @property
    def groq(self) -> AsyncOpenAI:
        if self._groq is None:
            if not self.settings.groq_api_key:
                raise RuntimeError("GROQ_API_KEY is not configured")
            self._groq = AsyncOpenAI(api_key=self.settings.groq_api_key, base_url=GROQ_BASE_URL)
        return self._groq

    def _resolve_model(self, tier: ModelTier) -> tuple[str, str]:
        if tier == "haiku":
            return self.settings.llm_primary_provider, self.settings.llm_haiku_model
        return self.settings.llm_primary_provider, self.settings.llm_sonnet_model

    def _resolve_fallback_model(self, tier: ModelTier) -> tuple[str, str]:
        provider = self.settings.llm_fallback_provider
        if tier == "haiku":
            return provider, self.settings.llm_fallback_haiku_model
        return provider, self.settings.llm_fallback_sonnet_model

    async def complete(
        self,
        prompt: str,
        *,
        tier: ModelTier = "sonnet",
        system: str | None = None,
        max_tokens: int = 4096,
        prompt_version: str = "v0",
        tenant_id: str | None = None,
    ) -> LLMResponse:
        if (
            self.max_cost_usd is not None
            and self.budget_remaining_usd is not None
            and self.budget_remaining_usd <= 0
        ):
            from services.api.exceptions import LLMBudgetExceededError

            raise LLMBudgetExceededError("Per-request LLM budget exhausted")

        provider, model = self._resolve_model(tier)
        start = time.perf_counter()

        try:
            response = await self._call_provider(provider, model, prompt, system, max_tokens)
        except Exception:
            logger.warning("Primary provider %s failed; trying fallback", provider, exc_info=True)
            fallback_provider, fallback_model = self._resolve_fallback_model(tier)
            response = await self._call_provider(
                fallback_provider, fallback_model, prompt, system, max_tokens
            )

        latency_ms = int((time.perf_counter() - start) * 1000)
        response.latency_ms = latency_ms
        self.accumulated_cost_usd += float(response.cost_usd)

        from services.api.services.cost_tracker import check_and_add_cost

        await check_and_add_cost(
            float(response.cost_usd),
            tenant_id=tenant_id,
            settings=self.settings,
        )

        logger.info(
            "llm.complete provider=%s model=%s tier=%s prompt_version=%s latency_ms=%d",
            response.provider,
            response.model,
            tier,
            prompt_version,
            latency_ms,
        )
        from services.api.tracing.langfuse import trace_generation

        trace_generation(
            self.settings,
            name=f"llm.{tier}",
            prompt=prompt[:4000],
            response=response.content[:4000],
            model=response.model,
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            latency_ms=latency_ms,
            metadata={"prompt_version": prompt_version, "provider": response.provider},
        )
        return response

    async def _call_openai_compatible(
        self,
        client: AsyncOpenAI,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
    ) -> tuple[str, int, int]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        else:
            messages.append(
                {"role": "system", "content": "You are a regulatory compliance assistant."}
            )
        messages.append({"role": "user", "content": prompt})
        completion = await client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,  # type: ignore[arg-type]
        )
        content = completion.choices[0].message.content or ""
        tokens_in = completion.usage.prompt_tokens if completion.usage else 0
        tokens_out = completion.usage.completion_tokens if completion.usage else 0
        return content, tokens_in, tokens_out

    async def _call_provider(
        self,
        provider: str,
        model: str,
        prompt: str,
        system: str | None,
        max_tokens: int,
    ) -> LLMResponse:
        if provider == "anthropic":
            message = await self.anthropic.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system or "You are a regulatory compliance assistant.",
                messages=[{"role": "user", "content": prompt}],
            )
            content = ""
            for block in message.content:
                if block.type == "text":
                    content += block.text
            tokens_in = message.usage.input_tokens
            tokens_out = message.usage.output_tokens
        elif provider == "groq":
            content, tokens_in, tokens_out = await self._call_openai_compatible(
                self.groq, model, prompt, system, max_tokens
            )
        elif provider == "openai":
            content, tokens_in, tokens_out = await self._call_openai_compatible(
                self.openai, model, prompt, system, max_tokens
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return LLMResponse(
            content=content,
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=0,
            cost_usd=estimate_cost(model, tokens_in, tokens_out),
        )

    async def log_usage(
        self,
        db: AsyncSession,
        *,
        trace_id: UUID,
        response: LLMResponse,
    ) -> None:
        """Persist LLM cost to llm_usage table (called after agent trace is created)."""
        from services.api.models import LLMUsage

        usage = LLMUsage(
            trace_id=trace_id,
            provider=response.provider,
            model=response.model,
            cost_usd=response.cost_usd,
        )
        db.add(usage)
        await db.commit()
