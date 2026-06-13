# Product Requirements Document (PRD) — RegIntel

## 1. Vision

Give every regulated SMB an always-on compliance analyst: a system that knows every regulation relevant to their business, watches for changes 24/7, understands second- and third-order implications, and tells them exactly what to do — with sources, not vibes.

## 2. Target Users

| Persona | Description | Primary Need |
|---|---|---|
| **Compliance Owner (SMB)** | Ops manager / founder at a 10-200 person regulated business (food mfg, med device, fintech) wearing the compliance hat part-time | "Tell me what changed that affects ME, and what to do about it" |
| **Compliance Consultant** | Independent consultant serving multiple SMB clients | Needs multi-tenant view, ability to triage alerts across clients |
| **Internal Compliance Analyst (mid-market)** | Works at a 200-1000 person company, currently uses expensive enterprise tools | Wants faster, cheaper, more precise alerts; willing to pay for API access |

## 3. Problem Statement (recap)

Regulatory bodies publish high-volume, cross-referencing changes. Keyword-alert tools (current SMB-affordable options, if any) produce high false-positive rates and miss multi-hop implications (Rule A amends Rule B, which a state code references, which applies to the client's product category). Generic LLM chat tools hallucinate citations — a documented liability risk.

## 4. Goals / Non-Goals

### Goals (V1)
- Ingest and version-control regulations from at least 3 sources (FDA/eCFR, Federal Register, one state code) for one vertical (food manufacturing).
- Build a knowledge graph connecting regulations to each other and to NAICS-coded business profiles.
- Detect clause-level diffs and classify severity (cosmetic / substantive / critical).
- For each client profile, run the multi-agent pipeline to determine relevance and generate a cited brief.
- Achieve ≥95% citation-accuracy on the eval benchmark (every cited clause must exist verbatim in source).
- Deliver briefs via dashboard + email/Slack alert.

### Non-Goals (V1)
- Not a general legal-research tool (no case law, no litigation prediction).
- Not providing legal advice — output is framed as "informational compliance intelligence," with disclaimers (see SECURITY.md / legal disclaimers).
- No automated filing/submission to agencies.

## 5. User Stories

1. **As a compliance owner**, I receive a weekly digest of regulatory changes filtered to my business profile (state, NAICS code, product categories), so I don't have to monitor the Federal Register myself.
2. **As a compliance owner**, when a critical change is detected, I receive an immediate alert with: what changed, why it affects me (with the reasoning chain across regulations), the deadline, and recommended actions — each backed by a direct citation I can click to view the source clause.
3. **As a consultant**, I manage multiple client profiles and see a triaged, cross-client view of which clients are affected by a given change.
4. **As an analyst**, I can ask ad-hoc questions ("Does the new FSMA rule on traceability apply to our frozen seafood SKUs in Texas and California?") and get a grounded multi-hop answer.
5. **As an admin**, I can mark an alert as a false positive, which feeds back into the relevance-agent's graph-traversal weighting.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-1 | System ingests documents from configured regulatory sources on a schedule | P0 |
| FR-2 | System computes clause-level diffs between document versions | P0 |
| FR-3 | System maintains a graph of regulation-to-regulation relationships (amends, references, supersedes) | P0 |
| FR-4 | System maintains client business profiles mapped to relevant regulation graph nodes | P0 |
| FR-5 | Relevance Agent identifies which client profiles are affected by a detected change, via multi-hop graph traversal | P0 |
| FR-6 | Impact-Analysis Agent retrieves downstream/related regulations and surfaces conflicts or additional obligations | P0 |
| FR-7 | Verification Agent confirms every citation against source text before brief is finalized | P0 |
| FR-8 | Brief-Generation Agent produces a structured, cited compliance memo | P0 |
| FR-9 | Users can ask ad-hoc natural-language questions against the system (chat interface) | P1 |
| FR-10 | Feedback (thumbs up/down, false-positive marking) is captured and used to adjust relevance scoring | P1 |
| FR-11 | Multi-tenant support for consultants managing multiple client profiles | P1 |
| FR-12 | Support for additional jurisdictions (EU/UK) | P2 |

## 7. Non-Functional Requirements

- **Citation accuracy**: ≥95% on benchmark; system must abstain (LOW_CONFIDENCE) rather than guess below threshold.
- **Latency**: Ad-hoc Q&A responses < 15s p95. Scheduled brief generation can be async/batch.
- **Freshness**: New regulatory documents reflected in graph within 24 hours of publication.
- **Auditability**: Every brief stores the full agent trace (retrieved chunks, graph paths, verification results) for audit.
- **Cost**: Per-brief inference cost should trend toward < $0.50 via LLM routing.

## 8. Success Metrics

- Citation accuracy ≥ 95% (eval benchmark)
- False-positive alert rate < 10% (validated via user feedback)
- Time-to-detect (publication → client alert) < 24h
- Cost per brief < $0.50 at V2

## 9. Out of Scope / Risks

- **Legal liability**: Output must be framed as informational; ToS includes disclaimers; no "legal advice" language. See SECURITY.md.
- **Source availability/rate limits**: Some agencies rate-limit scrapers — need polite crawling + caching.
- **Graph staleness**: If ingestion pipeline fails silently, graph goes stale — monitoring required (see EVALUATION.md / Monitoring).
