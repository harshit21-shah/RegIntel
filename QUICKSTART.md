# RegIntel — 3 commands to a working demo

## Prerequisites

- Docker Desktop (running)
- Python 3.12+
- Node.js 20+

```powershell
pip install -e ".[dev]"
cd web && npm install && cd ..
```

Copy `.env.example` to `.env` and set at least `GROQ_API_KEY` (or `ANTHROPIC_API_KEY` for fallback).

## One-command bootstrap

```powershell
make up
```

This starts Postgres, Neo4j, Qdrant, and Redis; runs migrations; seeds the demo tenant; and embeds the reference glossary + SEC filings into Qdrant.

## Run the app

**Terminal 1 — API**

```powershell
make run-api
```

On first start the API also auto-embeds the reference corpus if Qdrant is empty.

**Terminal 2 — Web**

```powershell
make run-web
```

Open **http://localhost:3000**

| Field    | Value                    |
|----------|--------------------------|
| Email    | `admin@regintel.dev`     |
| Password | `RegIntel-Demo-2025!`    |

## Try these queries

In **Query**, ask:

- What is the FDA?
- What are SEC filings?
- What is EDGAR?

Each answer includes verbatim citations from indexed sources.

## Health checks

| Endpoint   | Purpose                          |
|------------|----------------------------------|
| `/healthz` | Liveness                         |
| `/readyz`  | Postgres, Neo4j, Qdrant, Redis |

## Windows setup script

```powershell
.\scripts\setup_local.ps1
```

Equivalent to `make up` plus optional API/web launch.

## Deploy on AWS (beginner)

See **[docs/AWS_BEGINNER_DEPLOY.md](docs/AWS_BEGINNER_DEPLOY.md)** — one EC2 instance + Docker Compose (~30–60 min).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Login 500 | Ensure API is on `:8000` and web uses the built-in proxy (`/api/...`) |
| Query returns LOW_CONFIDENCE | Run `make embed-sources` or restart API (auto-bootstrap) |
| Postgres connection refused | Docker Postgres is on port **5433** (see `docker-compose.yml`) |
