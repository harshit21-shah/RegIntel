# TECH_STACK.md

## 1. LLMs & Routing

| Use Case | Model | Notes |
|---|---|---|
| High-volume summarization/classification (Change-Detector severity, hop_path explanations) | Claude Haiku | Cheap, fast |
| Reasoning over retrieved context (Impact-Analysis, Verification, Brief-Generation) | Claude Sonnet | Best cost/quality for structured reasoning + tool use |
| Escalation for low-confidence/complex cases (V2) | Claude Opus | Only invoked when Sonnet confidence < threshold, capped per day for cost control |
| Fallback provider | GPT-4o (via OpenAI API) | Configured as failover if Anthropic API unavailable; routing config in `services/agents/llm_client.py` |

**LLM Client wrapper** (`services/agents/llm_client.py`) handles: provider routing, retries/backoff, token/cost logging (to Postgres `llm_usage` table), prompt-version tagging (for eval traceability).

## 2. Embedding Models

- Primary: `voyage-law-2` (Voyage AI) — domain-tuned for legal/regulatory text, strong on clause-level semantic similarity.
- Fallback/local option: `BAAI/bge-large-en-v1.5` (self-hosted via sentence-transformers, for cost-sensitive dev/test environments).
- Embedding dimension: 1024 (voyage-law-2) — Qdrant collection configured accordingly.

## 3. Vector Database — Qdrant

- Hybrid search: dense (voyage-law-2) + sparse (BM25 via Qdrant's sparse vector support).
- Collections: `clauses` (one per environment: dev/staging/prod).
- Payload fields used as filters: `jurisdiction`, `agency`, `regulation_id`, `effective_date`, `version_hash`, `business_categories[]`.
- Reranking: env-configurable via `RERANKER_PROVIDER` — `heuristic` (keyword fusion), `bge` (`BAAI/bge-reranker-v2-m3`), or `cohere` (`rerank-v3.5`) applied to top-N hybrid results → top-5.

## 4. Graph Database — Neo4j

- Neo4j Aura (managed) for staging/prod; local Neo4j via Docker for dev.
- APOC plugin enabled for advanced graph algorithms (path-finding, similarity).
- Indexes: on `Clause.clause_id`, `Regulation.regulation_id`, `ClientProfile.client_id`, `BusinessCategory.naics_code`.

## 5. Relational Database — Postgres

- AWS RDS Postgres 16.
- Stores: client profiles, users/auth, briefs (denormalized copy for fast API reads), feedback, audit traces, LLM usage logs, eval results metadata.
- ORM: SQLAlchemy 2.0 (async) + Alembic for migrations.

## 6. Orchestration

- **Dagster**: ingestion pipelines (scheduled polling, parsing, diffing, graph-building, embedding).
- **LangGraph**: agent state machine (the 5-agent pipeline).
- **Redis**: caching (embedding cache, rate-limit counters), Celery/RQ broker for async API tasks if needed.
- **SQS**: change-event queue between ingestion and agent pipeline (decoupling, retry semantics).

## 7. API & App Layer

- **FastAPI** (Python 3.12, async) — REST API, see `API_SPEC.md`.
- **Pydantic v2** for all schema validation.
- Frontend (out of MVP critical path): Next.js + Tailwind, consumes REST API.
- Auth: JWT (via `fastapi-users` or Auth0 integration) — multi-tenant aware.

## 8. Cloud Infrastructure — AWS

| Component | Service |
|---|---|
| Compute (API, agent workers) | ECS Fargate |
| Scheduled scrapers | Lambda + EventBridge |
| Queue | SQS |
| Relational DB | RDS Postgres |
| Object storage (raw docs, versioned) | S3 (versioning enabled) |
| Secrets | Secrets Manager |
| Graph DB | Neo4j Aura (managed, outside AWS but VPC-peered) |
| Vector DB | Qdrant Cloud (or self-hosted on ECS for cost control in early stages) |
| Observability | CloudWatch + Langfuse (self-hosted on ECS) |
| CI/CD | GitHub Actions |
| IaC | Terraform |

## 9. Evaluation Frameworks

- **Ragas** — faithfulness, context precision/recall metrics.
- **Custom entailment harness** (`services/eval/entailment/`) — clause-level citation verification.
- **LangSmith or Langfuse** — tracing, prompt versioning, dataset management (Langfuse preferred for self-hosted/cost control).
- **pytest / pytest-benchmark** — unit + perf testing.

## 10. Dev Tooling

- `ruff`, `black`, `mypy --strict`, `pre-commit`.
- `docker-compose.yml` for local Postgres, Neo4j, Qdrant, Redis.
- `Makefile` with standard targets: `install`, `lint`, `typecheck`, `test`, `eval-citations`, `eval-pipeline`, `run-api`, `migrate`, `seed-demo`.

## 11. Versioning & Reproducibility

- All prompts versioned in `services/agents/prompts/` with semantic version tags; agent code references prompt versions explicitly (no inline prompt strings).
- Eval results stored with `{model_version, prompt_version, retrieval_config_hash}` for full reproducibility.
