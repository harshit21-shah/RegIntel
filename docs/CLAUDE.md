# CLAUDE.md — AI Agent Operating Guide for RegIntel

This file orients any AI coding assistant (Claude Code, Cursor, Copilot Workspace, etc.) working in this repository. Read this fully before making changes.

## 1. Project Summary

RegIntel is a GraphRAG-based regulatory change-intelligence platform. It ingests regulatory documents (FDA, SEC, EPA, EU/UK equivalents, state codes), models them as a knowledge graph, detects clause-level changes over time, and runs a multi-agent pipeline to determine which clients are affected and generate verified compliance briefs.

**Core invariant: every factual claim in a generated brief must be traceable to a verbatim source clause via citation. No citation = no claim.**

## 2. Repo Map (where to find / put things)

```
regintel/
├── docs/                  # All *.md docs (this folder's siblings)
├── services/
│   ├── ingestion/         # scrapers, parsers, diff engine
│   ├── graph/              # Neo4j schema, graph-build jobs
│   ├── retrieval/          # hybrid search, reranking
│   ├── agents/             # LangGraph agents (5 agents, see AGENTS.md)
│   ├── api/                # FastAPI app (see API_SPEC.md)
│   └── eval/               # evaluation harness, benchmark datasets
├── infra/                  # Terraform/CDK, Dockerfiles, k8s manifests
├── tests/                  # unit, integration, e2e
└── scripts/                # one-off / migration scripts
```

Always consult `ARCHITECTURE.md` before adding a new service or changing a data flow. Always consult `DATABASE_SCHEMA.md` before changing Postgres or Neo4j schemas — schema changes require a migration file in `services/graph/migrations/` or `services/api/migrations/`.

## 3. Coding Standards

- **Language**: Python 3.12 for all backend services. TypeScript (strict mode) for any frontend.
- **Style**: `ruff` + `black` (line length 100). Run `make lint` before committing.
- **Typing**: All functions must have type hints. `mypy --strict` must pass on `services/`.
- **Testing**: Every new module needs unit tests in `tests/unit/<mirror path>`. Agents need eval-set tests in `services/eval/`.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `eval:`, `docs:`). One logical change per commit.
- **No bare LLM calls**: All LLM calls go through `services/agents/llm_client.py`, which enforces logging, cost tracking, and routing (see TECH_STACK.md §LLM Routing).
- **No silent fallbacks on citation failure**: If the verification agent cannot confirm a citation, the pipeline must return a `LOW_CONFIDENCE` status, never a confident-sounding fabricated answer.

## 4. Environment & Secrets

- Use `.env.local` (gitignored) for local dev; template in `.env.example`.
- Never commit API keys. Secrets in production come from AWS Secrets Manager (see SECURITY.md).
- Local dev stack runs via `docker-compose.yml` (Postgres, Neo4j, Qdrant, Redis).

## 5. Before You Write Code — Checklist

1. Read `PRD.md` if the task touches product behavior.
2. Read `ARCHITECTURE.md` for the relevant subsystem diagram.
3. If touching agents, read `AGENTS.md` for the agent's contract (inputs/outputs/state schema).
4. If touching retrieval, read `DATA_PIPELINE.md` and `TECH_STACK.md`.
5. Check `TASKS.md` for the current sprint — don't start unscoped work.
6. Write/update tests alongside code. Add eval cases to `services/eval/` for any agent behavior change.

## 6. Definition of Done

- [ ] Code passes `make lint && make typecheck && make test`
- [ ] New/changed agent behavior has eval cases in `services/eval/datasets/`
- [ ] Citation-accuracy eval (`make eval-citations`) shows no regression
- [ ] Docs updated (especially `API_SPEC.md` for endpoint changes, `DATABASE_SCHEMA.md` for schema changes)
- [ ] PR description references the task ID from `TASKS.md`

## 7. Things That Will Get a PR Rejected

- Adding a new vector DB / graph DB / LLM provider without updating `TECH_STACK.md` and discussing in `ARCHITECTURE.md`.
- Any agent that produces a final brief without going through the Verification Agent.
- Hardcoded credentials, even "temporary" ones.
- Skipping the diff engine and re-ingesting full documents on every run (cost/perf).

## 8. Key Files to Read First (in order)

1. `PRD.md`
2. `ARCHITECTURE.md`
3. `AGENTS.md`
4. `DATABASE_SCHEMA.md`
5. `EVALUATION.md`
