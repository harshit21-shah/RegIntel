# RegIntel

**Real-time regulatory change-intelligence for regulated SMBs, powered by GraphRAG and a verified multi-agent pipeline.**

RegIntel continuously monitors regulatory sources (FDA, SEC, EPA, OSHA, EU/UK, state agencies), detects clause-level changes, traces multi-hop implications across interlinked regulations using a knowledge graph, and produces compliance briefs with every claim grounded in a verifiable citation.

## Why RegIntel

> "We found out about the new FDA labeling rule three weeks after the deadline — from a fine notice."

Enterprise compliance tooling (Bloomberg Law, Thomson Reuters) costs $50K–$500K/year and is built for legal teams, not operators. SMBs — 33M+ in the US alone — get nothing. RegIntel closes that gap with an AI system that reasons over regulatory graphs the way a compliance lawyer would, but continuously and at a fraction of the cost.

## High-Level Architecture

```mermaid
flowchart LR
    A[Regulatory Sources] -->|scrapers/APIs| B[Ingestion & Diff Engine]
    B --> C[(Document Store / S3)]
    B --> D[(Knowledge Graph - Neo4j)]
    B --> E[(Vector Store - Qdrant)]
    D & E --> F[Multi-Agent Pipeline]
    F --> G[Compliance Brief]
    F --> H[(Client Profile Graph)]
    G --> I[Client Dashboard / Alerts]
    F -->|eval & feedback| J[Evaluation & Monitoring]
```

## Documentation Index

| Doc | Purpose |
|---|---|
| [CLAUDE.md](./CLAUDE.md) | AI coding agent operating guide |
| [PRD.md](./PRD.md) | Product requirements & user stories |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design, diagrams, data flow |
| [DATA_PIPELINE.md](./DATA_PIPELINE.md) | Ingestion, diffing, graph-build |
| [AGENTS.md](./AGENTS.md) | Multi-agent design & contracts |
| [EVALUATION.md](./EVALUATION.md) | Eval framework, benchmarks |
| [TECH_STACK.md](./TECH_STACK.md) | Technology choices & rationale |
| [API_SPEC.md](./API_SPEC.md) | REST API reference |
| [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) | Postgres + Neo4j + Vector schemas |
| [SECURITY.md](./SECURITY.md) | Threat model, secrets, compliance |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Infra, CI/CD, environments |
| [ROADMAP.md](./ROADMAP.md) | MVP → V1 → V2 → Production |
| [TASKS.md](./TASKS.md) | Sprint-level task breakdown |
| [RESUME_IMPACT.md](./RESUME_IMPACT.md) | Framing this project for hiring |

## Quickstart

```bash
git clone <repo>
cd regintel
cp .env.example .env.local
docker compose up -d        # Postgres, Neo4j, Qdrant, Redis
make install
make migrate
make seed-demo               # loads a small sample regulation corpus
make run-api
```

Visit `http://localhost:8000/docs` for the API explorer.

## License

Proprietary (or MIT for portfolio mode — set in `LICENSE`).
