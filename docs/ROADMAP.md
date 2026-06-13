# ROADMAP.md

## Phase 0 — Foundations (Week 1-2)
- Repo scaffolding (structure per CLAUDE.md), CI skeleton, docker-compose local stack.
- Postgres schema + Alembic migrations (core tables).
- Neo4j schema constraints/indexes.
- Qdrant collection setup.
- `llm_client.py` with routing + cost logging.

**Exit criteria**: `make install && make migrate && make run-api` works locally; `/healthz` green.

## Phase 1 — MVP (Week 3-6)
**Scope**: Single vertical (food manufacturing), single jurisdiction (US federal — eCFR Title 21 + Federal Register), no graph yet.

- eCFR + Federal Register source adapters.
- Document parser (clause-level structuring for CFR format).
- Basic vector RAG: chunk, embed, store in Qdrant.
- Simple Q&A endpoint (`/query`) — single-hop retrieval, Sonnet generation, basic citation (no independent verification yet).
- Minimal client profile model (naics_codes, states — single state for MVP).
- Eval: build initial 20-item golden Q&A set, basic citation-presence check.

**Exit criteria**: Can answer "does X regulation apply to Y product" with at least one citation, ≥80% citation presence.

## Phase 2 — V1: Graph + Diffing + Agentic Pipeline (Week 7-14)
- Clause-level diff engine + severity classification.
- Neo4j knowledge graph build (Regulation/Clause/BusinessCategory/ClientProfile nodes, AMENDS/REFERENCES/APPLIES_TO edges).
- Full 5-agent LangGraph pipeline (Change-Detector → Relevance → Impact-Analysis → Verification → Brief-Generation).
- Verification Agent as hard gate; LOW_CONFIDENCE routing.
- Expand golden eval set to 50 historical changes; implement citation-accuracy entailment harness.
- Add one state jurisdiction (e.g., California food safety code).
- Feedback endpoint + storage (no weight-adjustment yet).

**Exit criteria**: Citation accuracy ≥90% on golden set; end-to-end pipeline runs on a real detected change and produces a brief with ≥0.9 confidence for at least 3 test client profiles.

## Phase 3 — V2: Multi-Jurisdiction, Feedback Loop, Cost Optimization (Week 15-22)
- Add SEC EDGAR (fintech vertical) or EU/UK source (EUR-Lex) — pick based on demo/target audience.
- Corrective RAG reformulation loop fully implemented and evaluated.
- Feedback-driven relevance-weight adjustment (heuristic, then LightGBM ranking model).
- LLM routing optimization (Haiku/Sonnet split tuned via cost-per-brief tracking); cost target <$0.50/brief.
- Multi-tenant consultant view (`/changes/{id}/affected-profiles`).
- Citation accuracy target raised to ≥95%.

**Exit criteria**: Citation accuracy ≥95%; cost/brief <$0.50; multi-tenant + 2 jurisdictions live in staging.

## Phase 4 — Production Hardening & Deployment (Week 23-28)
- Full Terraform infra, CI/CD pipelines (staging + prod), rolling deploys.
- Security review (SECURITY.md checklist), prompt-injection eval pass.
- Monitoring dashboards (Langfuse + CloudWatch), alerting configured.
- Load testing (target: 100 concurrent client profiles, daily change-volume from 3+ sources).
- Documentation finalization, demo video, public README polish.

**Exit criteria**: Production deployment live, monitored, with documented SLOs (citation accuracy, latency, staleness) being met for 2 consecutive weeks.

## Future (Post-V2 / Startup Track)
- Additional verticals (medical devices, fintech compliance, environmental/EPA).
- Self-serve onboarding (NAICS auto-classification from company website via LLM).
- Opus escalation tier for complex multi-jurisdiction conflicts.
- API product for compliance consultancies (B2B2B).
