# TASKS.md

Task IDs format: `REG-<phase>-<num>`. Reference these in commits/PRs (per CLAUDE.md).

## Phase 0 — Foundations

- [ ] `REG-0-01` Scaffold repo structure (services/, infra/, tests/, docs/) per CLAUDE.md
- [ ] `REG-0-02` `docker-compose.yml`: Postgres, Neo4j, Qdrant, Redis
- [ ] `REG-0-03` Postgres schema v1 (tenants, users, client_profiles, change_events, briefs, brief_citations, feedback, agent_traces, llm_usage) + Alembic init
- [ ] `REG-0-04` Neo4j constraints/indexes migration script
- [ ] `REG-0-05` Qdrant collection setup script (`clauses_v1`, hybrid dense+sparse)
- [ ] `REG-0-06` `llm_client.py`: provider routing (Anthropic primary, OpenAI fallback), cost logging to `llm_usage`
- [ ] `REG-0-07` CI: lint/typecheck/unit-test workflow
- [ ] `REG-0-08` `.env.example`, Makefile targets

## Phase 1 — MVP

- [ ] `REG-1-01` eCFR API adapter (`services/ingestion/adapters/ecfr.py`) — fetch Title 21 Part 101 + Part 1
- [ ] `REG-1-02` Federal Register API adapter
- [ ] `REG-1-03` CFR document parser → clause-level `ParsedDocument` (Pydantic models)
- [ ] `REG-1-04` Embedding pipeline: chunk → voyage-law-2 → Qdrant upsert
- [ ] `REG-1-05` Basic hybrid retrieval function (`services/retrieval/search.py`)
- [ ] `REG-1-06` `/query` endpoint: retrieval + Sonnet generation + citation tags (no verification agent yet)
- [ ] `REG-1-07` Client profile CRUD endpoints + Postgres model
- [ ] `REG-1-08` Golden eval set v0: 20 Q&A pairs for food labeling (Title 21 Part 101)
- [ ] `REG-1-09` Citation-presence eval script (`make eval-citations-v0`)

## Phase 2 — V1

- [ ] `REG-2-01` Clause-level diff engine (`services/ingestion/diff_engine.py`)
- [ ] `REG-2-02` Severity classifier (rule-based + Haiku fallback)
- [ ] `REG-2-03` Neo4j graph builder: Regulation/Clause/Agency nodes + PART_OF edges
- [ ] `REG-2-04` Cross-reference extraction (regex first pass) → REFERENCES/AMENDS edges
- [ ] `REG-2-05` BusinessCategory seed data (NAICS codes for food mfg) + APPLIES_TO edges (manual seed)
- [ ] `REG-2-06` ClientProfile graph mirroring (Postgres -> Neo4j sync job)
- [ ] `REG-2-07` Change-Detector Agent (LangGraph node)
- [ ] `REG-2-08` Relevance Agent: Cypher multi-hop traversal query + scoring
- [ ] `REG-2-09` Impact-Analysis Agent w/ Corrective RAG reformulation loop
- [ ] `REG-2-10` Verification Agent: independent re-retrieval + entailment check + LOW_CONFIDENCE routing
- [ ] `REG-2-11` Brief-Generation Agent: structured output schema + disclaimer injection
- [ ] `REG-2-12` Full pipeline wiring in LangGraph (state machine per AGENTS.md)
- [ ] `REG-2-13` Golden eval set v1: expand to 50 historical changes w/ gold briefs
- [ ] `REG-2-14` Citation-accuracy entailment harness (`services/eval/entailment/`)
- [ ] `REG-2-15` CA food safety code adapter + parser (second jurisdiction)
- [ ] `REG-2-16` `/briefs`, `/changes`, feedback endpoints

## Phase 3 — V2

- [ ] `REG-3-01` SEC EDGAR or EUR-Lex adapter (vertical/jurisdiction expansion)
- [ ] `REG-3-02` Feedback-driven relevance weight adjustment (heuristic v1)
- [ ] `REG-3-03` LightGBM ranking model for relevance scoring (replaces heuristic)
- [ ] `REG-3-04` LLM routing cost optimization pass + cost dashboards
- [ ] `REG-3-05` Multi-tenant consultant view endpoints
- [ ] `REG-3-06` Raise citation-accuracy target to 95%, tune retrieval/reranking accordingly
- [ ] `REG-3-07` Prompt-injection adversarial eval set + defenses

## Phase 4 — Production

- [ ] `REG-4-01` Terraform: network, RDS, ECS, SQS, S3, secrets modules
- [ ] `REG-4-02` Dockerfiles per service + ECR push pipeline
- [ ] `REG-4-03` Staging deploy pipeline + smoke/e2e tests
- [ ] `REG-4-04` Production deploy pipeline (manual approval gate)
- [ ] `REG-4-05` Langfuse self-hosted setup + dashboards
- [ ] `REG-4-06` CloudWatch alarms + PagerDuty/Slack integration
- [ ] `REG-4-07` Load testing (100 client profiles, 3+ sources)
- [ ] `REG-4-08` Security review checklist completion (SECURITY.md)
- [ ] `REG-4-09` Demo video + README polish + portfolio write-up
