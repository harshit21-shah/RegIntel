"""Agent pipeline configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env.local", ".env"), extra="ignore")

    verification_threshold: float = 0.9
    retrieval_top_k: int = 5
    corrective_rag_max_rounds: int = 2
    relevance_min_score: float = 0.3
    max_cost_per_brief_usd: float = 0.50
    citation_accuracy_threshold: float = 0.95


def get_agent_settings() -> AgentSettings:
    return AgentSettings()
