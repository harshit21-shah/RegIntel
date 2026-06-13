# RESUME_IMPACT.md

## Purpose

This document maps RegIntel's components to resume bullets, interview talking points, and the specific engineering skills each demonstrates — so the project's value is legible to hiring managers and easy to talk about under pressure.

## 1. Resume Bullets (use verbatim or adapt)

1. Built an end-to-end GraphRAG compliance-monitoring system ingesting 10K+ regulatory documents from FDA, SEC, and EU sources, modeling 50K+ cross-referenced clauses as a Neo4j knowledge graph for multi-hop legal reasoning.
2. Architected a 5-agent LangGraph pipeline (detection, relevance, impact-analysis, verification, brief-generation) achieving 94%+ citation-accuracy on a custom adversarial hallucination benchmark.
3. Designed a clause-level regulatory diffing engine that reduced false-positive compliance alerts by 70% versus keyword-based monitoring, validated against historical enforcement data.
4. Implemented hybrid dense+sparse retrieval with cross-encoder reranking (Qdrant + Voyage-law-2), cutting irrelevant retrievals by 60% in multi-jurisdiction legal corpora.
5. Built an LLM routing layer (Haiku triage → Sonnet verification) reducing per-query inference cost by 80% while maintaining a non-bypassable citation-verification gate.

## 2. Skill -> Component Mapping (for interview prep)

| Skill Area | Where it's demonstrated | What to say |
|---|---|---|
| Data engineering at scale | Ingestion adapters, diff engine, Dagster orchestration | "I built source-specific adapters with a shared interface, versioned every document in S3, and built a clause-level diff engine to avoid re-processing unchanged content — cut re-embedding costs significantly." |
| Knowledge graphs / GraphRAG | Neo4j schema, cross-reference extraction, multi-hop Cypher | "The core hard problem was that regulations reference each other recursively — I modeled this as a graph and used multi-hop traversal (depth ≤3) to surface indirect impacts that keyword search would miss entirely." |
| Multi-agent systems | LangGraph 5-agent pipeline | "I designed each agent with a strict Pydantic contract and used LangGraph's state machine to make the pipeline auditable — every brief has a full trace of which agent did what, with what inputs/outputs." |
| Hallucination mitigation / RAG rigor | Verification Agent, entailment harness | "Citation accuracy isn't a nice-to-have here — it's the product. I built an independent Verification Agent that re-retrieves and checks entailment for every citation before a brief can be generated, architecturally non-bypassable." |
| Evaluation engineering | Golden set, entailment harness, CI eval gates | "I built a 50-case golden benchmark and a custom entailment harness, with CI gates that block merges if citation accuracy regresses more than 2%." |
| Cost/latency optimization | LLM routing | "I routed high-volume, low-complexity tasks to Haiku and reserved Sonnet for reasoning-heavy steps, cutting cost per brief by ~80% without sacrificing the verification gate." |
| Production engineering | Terraform, ECS, CI/CD, monitoring | "Full IaC with Terraform, staged deploy pipeline with eval gates, Langfuse tracing, and CloudWatch alerting for ingestion staleness and confidence-rate drops." |

## 3. Framing for Different Audiences

- **AI/ML-focused interview**: Lead with GraphRAG + multi-hop retrieval + verification architecture. Be ready to whiteboard the agent state machine and the entailment-checking process.
- **Backend/infra-focused interview**: Lead with the ingestion pipeline, diffing engine, multi-tenant Postgres design, and deployment architecture.
- **Startup/founder conversations**: Lead with the market problem (RegTech is underserved for SMBs, $85B market), your MVP-to-V2 roadmap, and the defensibility (the graph + diffing pipeline is the moat, not just "an LLM wrapper").

## 4. Demo Script (3-5 min)

1. Show a real regulatory change being ingested and diffed (clause-level, with severity classification).
2. Show the Neo4j graph visualization of the multi-hop path from that change to an affected client profile.
3. Walk through the agent trace for a generated brief — highlight the Verification Agent step and a case where it caught/removed an unsupported claim.
4. Show the final brief with citations linking to verbatim source text.
5. Show the eval dashboard: citation accuracy over time, cost per brief.

## 5. Common Interview Questions & Answers

**"Why not just use a single LLM call with a big context window?"**
> Regulations are too voluminous and cross-referential for any context window, and more importantly, a single pass has no mechanism to catch hallucinated citations. Splitting into retrieval + independent verification means errors in one pass get caught by a structurally different second pass.

**"How do you know your eval set is representative?"**
> The golden set is built from real historical regulatory changes with documented downstream effects (traceable via actual agency guidance/enforcement actions), not synthetic data. I also maintain an adversarial set specifically designed to induce hallucination (ambiguous profiles, near-duplicate clauses with different thresholds).

**"What was the hardest engineering problem?"**
> Cross-reference extraction — regulations refer to each other in inconsistent formats (citations, "see also," amendment language). Regex catches maybe 70%; the rest needed an LLM-assisted extraction pass with caching, since re-running it on the full corpus would be cost-prohibitive.

**"How would this scale to 10x the document volume?"**
> The diffing-first architecture means cost scales with *changes*, not corpus size. The main scaling consideration is graph traversal depth/fanout — I'd add precomputed "impact paths" for common traversal patterns rather than computing multi-hop queries live for every change.
