"""Application configuration from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "postgresql+asyncpg://regintel:regintel@localhost:5433/regintel"
    auto_bootstrap_search: bool = True
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "regintel"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "clauses_v1"
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""
    voyage_api_key: str = ""

    llm_primary_provider: str = "groq"
    llm_fallback_provider: str = "anthropic"
    llm_haiku_model: str = "llama-3.1-8b-instant"
    llm_sonnet_model: str = "llama-3.3-70b-versatile"
    llm_fallback_haiku_model: str = "claude-3-5-haiku-20241022"
    llm_fallback_sonnet_model: str = "claude-3-5-sonnet-20241022"

    aws_region: str = "us-east-1"
    sqs_queue_url: str = ""
    s3_documents_bucket: str = ""

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    jwt_secret_key: str = "dev-only-change-me-before-production-deploy-32b"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    rate_limit_query_per_minute: int = 30
    rate_limit_bulk_per_minute: int = 100
    tenant_daily_cost_cap_usd: float = 50.0
    global_daily_cost_cap_usd: float = 500.0
    ingestion_staleness_hours: int = 48

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    reranker_provider: str = "heuristic"
    rerank_top_n: int = 25
    cohere_api_key: str = ""

    slack_webhook_url: str = ""
    ses_from_email: str = ""
    app_base_url: str = "http://localhost:3000"
    alert_channels: str = "slack,email"

    @property
    def require_auth(self) -> bool:
        return self.app_env in ("staging", "production")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def alert_channel_list(self) -> list[str]:
        return [ch.strip() for ch in self.alert_channels.split(",") if ch.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
