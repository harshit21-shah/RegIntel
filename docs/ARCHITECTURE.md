# ARCHITECTURE.md

## 1. System Overview

RegIntel is composed of five major subsystems:

1. **Ingestion & Diff Engine** — pulls regulatory documents, versions them, computes clause-level diffs.
2. **Knowledge Layer** — Neo4j knowledge graph (regulations, clauses, agencies, business categories) + Qdrant vector store (chunk embeddings) + Postgres (client profiles, metadata, audit logs).
3. **Agentic Reasoning Layer** — LangGraph multi-agent pipeline (5 agents, see AGENTS.md).
4. **API & Application Layer** — FastAPI backend, dashboard frontend, alerting (email/Slack).
5. **Evaluation & Monitoring Layer** — citation accuracy eval, hallucination eval, cost/latency dashboards.

## 2. End-to-End Data Flow

```mermaid
flowchart TD
    subgraph Sources
        S1[Federal Register API]
        S2[eCFR API]
        S3[SEC EDGAR]
        S4[State Legislature Feeds]
        S5[EUR-Lex]
    end

    subgraph Ingestion
        SC[Scrapers / API Pollers]
        PARSE[Document Parsers]
        DIFF[Clause-Level Diff Engine]
        VER[Versioned Doc Store - S3]
    end

    subgraph Knowledge
        GB[Graph Builder]
        NEO[(Neo4j Knowledge Graph)]
        EMB[Embedding Pipeline]
        QD[(Qdrant Vector Store)]
        PG[(Postgres: profiles, metadata, audit)]
    end

    subgraph Agents [LangGraph Multi-Agent Pipeline]
        A1[Change-Detector Agent]
        A2[Relevance Agent]
        A3[Impact-Analysis Agent]
        A4[Verification Agent]
        A5[Brief-Generation Agent]
    end

    subgraph App
        API[FastAPI]
        DASH[Dashboard]
        ALERT[Alerting: Email/Slack]
    end

    subgraph Eval [Evaluation & Monitoring]
        EVALH[Hallucination/Citation Eval]
        MON[Latency/Cost Dashboards]
        FB[Feedback Store]
    end

    S1 & S2 & S3 & S4 & S5 --> SC --> PARSE --> DIFF
    DIFF --> VER
    DIFF --> GB
    PARSE --> EMB
    GB --> NEO
    EMB --> QD

    DIFF -->|change event| A1
    A1 --> A2
    NEO --> A2
    PG --> A2
    A2 --> A3
    NEO & QD --> A3
    A3 --> A4
    QD & NEO --> A4
    A4 --> A5
    A5 --> API
    API --> DASH
    API --> ALERT
    A4 --> EVALH
    API --> FB --> A2
    A1 & A2 & A3 & A4 & A5 --> MON
```

## 3. Subsystem Detail

### 3.1 Ingestion & Diff Engine
- Scheduled pollers (Dagster) per source, respecting rate limits / robots.txt.
- Each fetched document is hashed; if hash changes, parse and run clause-level diff against previous version (stored in S3, versioned).
- Diff output: list of `(clause_id, change_type, old_text, new_text, severity)`.
- Severity classification: rule-based heuristics (effective date changes, numeric threshold changes = high severity) + LLM classifier for ambiguous cases.
- Full detail: see `DATA_PIPELINE.md`.

### 3.2 Knowledge Layer
- **Neo4j**: nodes = `Regulation`, `Clause`, `Agency`, `BusinessCategory` (NAICS), `Jurisdiction`, `ClientProfile`. Edges = `AMENDS`, `REFERENCES`, `SUPERSEDES`, `APPLIES_TO`, `OPERATES_IN`.
- **Qdrant**: dense + sparse (hybrid) embeddings of clause-level chunks, with metadata filters (jurisdiction, agency, effective_date, regulation_id).
- **Postgres**: client profiles, users, alert history, feedback, audit trail of agent runs.
- Full schema: see `DATABASE_SCHEMA.md`.

### 3.3 Agentic Reasoning Layer
See `AGENTS.md` for full contracts. High-level flow per detected change:

```mermaid
sequenceDiagram
    participant Diff as Diff Engine
    participant CD as Change-Detector
    participant RA as Relevance Agent
    participant IA as Impact-Analysis Agent
    participant VA as Verification Agent
    participant BG as Brief-Generation Agent
    participant DB as Postgres/Neo4j

    Diff->>CD: change event (clause diff + severity)
    CD->>RA: classified change object
    RA->>DB: query client profiles via graph traversal
    RA->>IA: list of (client_profile, affected_clauses, hop_path)
    IA->>DB: retrieve related/downstream regulations (multi-hop)
    IA->>VA: draft impact analysis + citations
    VA->>DB: re-retrieve & verify each citation
    alt all citations verified
        VA->>BG: verified impact analysis
        BG->>DB: store brief + audit trace
        BG-->>App: emit brief
    else verification fails
        VA->>DB: mark LOW_CONFIDENCE, route to human review queue
    end
```

### 3.4 API & Application Layer
- FastAPI exposes REST endpoints (see `API_SPEC.md`) for profiles, briefs, ad-hoc Q&A, feedback.
- Dashboard (React/Next.js) — out of scope for backend-focused MVP but stubbed.
- Alerting via email (SES) and Slack webhook.

### 3.5 Evaluation & Monitoring
- Citation-accuracy benchmark run on every agent-pipeline change (CI gate).
- Langfuse/LangSmith tracing of all agent runs.
- Cost/latency dashboards (per-agent token usage, $ per brief).
- See `EVALUATION.md`.

## 4. Deployment Topology (summary — see DEPLOYMENT.md)

```mermaid
flowchart LR
    subgraph AWS
        ALB[Application Load Balancer]
        ECS_API[ECS: FastAPI service]
        ECS_AGENTS[ECS: Agent worker pool]
        LAMBDA[Lambda: Scrapers - scheduled]
        RDS[(RDS Postgres)]
        NEO4J[Neo4j Aura]
        QDRANT[Qdrant Cloud]
        S3[(S3: doc store)]
        SQS[SQS: change-event queue]
        SECRETS[Secrets Manager]
    end
    Users-->ALB-->ECS_API
    ECS_API<-->RDS
    ECS_API-->SQS-->ECS_AGENTS
    ECS_AGENTS<-->NEO4J
    ECS_AGENTS<-->QDRANT
    ECS_AGENTS<-->RDS
    LAMBDA-->S3
    LAMBDA-->SQS
    ECS_API & ECS_AGENTS-->SECRETS
```

## 5. Key Architectural Decisions (ADR summary)

| Decision | Rationale | Alternatives Considered |
|---|---|---|
| Neo4j for regulation graph | Native multi-hop traversal, Cypher expressiveness for "amends/references" chains | Postgres recursive CTEs (too slow for deep traversal), RDF triple store (overkill) |
| Qdrant for vectors | Hybrid search (dense+sparse) support, self-hostable, good filtering | Pinecone (cost at scale), Weaviate (similar, Qdrant chosen for simpler ops) |
| LangGraph for agents | Explicit state machine, conditional routing, good for audit trails | CrewAI/AutoGen (less control over state/branching) |
| Diffing at clause level, not document level | Reduces noise, enables severity classification, dramatically cuts re-embedding cost | Whole-document re-embed on any change (expensive, noisy) |
| Verification Agent as hard gate (non-bypassable) | Citation accuracy is the core product guarantee | Trusting single-pass generation (unacceptable hallucination risk) |
