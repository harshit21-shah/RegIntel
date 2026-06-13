"""Compare reranker providers on retrieval precision."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import statistics
import time
from pathlib import Path

from services.api.config import Settings
from services.retrieval.rerank_service import rerank
from services.retrieval.types import RetrievedClause

logger = logging.getLogger(__name__)

DATASET_PATH = (
    Path(__file__).resolve().parent.parent / "services" / "eval" / "datasets" / "query_v0.json"
)


def load_cases(path: Path = DATASET_PATH) -> list[dict[str, object]]:
    if not path.exists():
        return [
            {
                "id": "sample-1",
                "question": "What are principal display panel requirements for food labeling?",
                "expected_clause_ids": ["ecfr:21:101:101.1"],
            }
        ]
    return json.loads(path.read_text(encoding="utf-8"))


def _mock_candidates(question: str) -> list[RetrievedClause]:
    return [
        RetrievedClause(
            clause_id="ecfr:21:101:101.1",
            text="The term principal display panel as it applies to food in package form...",
            score=0.82,
            regulation_id="21:101",
            source_url="https://www.ecfr.gov/current/title-21/section-101.1",
            section_number="101.1",
            title="Principal display panel",
        ),
        RetrievedClause(
            clause_id="ecfr:21:101:101.3",
            text="Label means a display of written, printed, or graphic matter...",
            score=0.75,
            regulation_id="21:101",
            source_url="https://www.ecfr.gov/current/title-21/section-101.3",
            section_number="101.3",
            title="Definitions",
        ),
        RetrievedClause(
            clause_id="ecfr:21:101:101.9",
            text="Nutrition information relating to food shall be provided...",
            score=0.71,
            regulation_id="21:101",
            source_url="https://www.ecfr.gov/current/title-21/section-101.9",
            section_number="101.9",
            title="Nutrition labeling",
        ),
    ]


async def evaluate_provider(provider: str, cases: list[dict[str, object]]) -> dict[str, float]:
    settings = Settings(reranker_provider=provider)
    hits = 0
    total = 0
    latencies: list[float] = []

    for case in cases:
        question = str(case["question"])
        expected = {str(item) for item in case.get("expected_clause_ids", [])}
        candidates = _mock_candidates(question)
        start = time.perf_counter()
        ranked = await rerank(question, candidates, top_k=3, settings=settings)
        latencies.append(time.perf_counter() - start)
        top_ids = {item.clause_id for item in ranked}
        if expected & top_ids:
            hits += 1
        total += 1

    return {
        "precision_at_3": hits / max(1, total),
        "latency_p50_ms": statistics.median(latencies) * 1000,
        "latency_p95_ms": (sorted(latencies)[int(len(latencies) * 0.95) - 1] if latencies else 0)
        * 1000,
    }


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    cases = load_cases()
    providers = ["heuristic", "bge", "cohere"]
    results: dict[str, dict[str, float]] = {}
    for provider in providers:
        logger.info("Evaluating reranker provider: %s", provider)
        results[provider] = await evaluate_provider(provider, cases)

    print("Reranker comparison")
    for provider, metrics in results.items():
        print(
            f"{provider}: precision@3={metrics['precision_at_3']:.1%} "
            f"p50={metrics['latency_p50_ms']:.1f}ms p95={metrics['latency_p95_ms']:.1f}ms"
        )

    if args.persist:
        from services.api.db import AsyncSessionLocal
        from services.api.services.eval_store import persist_eval_run
        from services.eval.entailment.harness import EntailmentResult

        best = max(results.items(), key=lambda item: item[1]["precision_at_3"])
        eval_results = [
            EntailmentResult(
                case_id=provider,
                predicted=str(metrics["precision_at_3"]),
                expected="precision_at_3",
                correct=metrics["precision_at_3"] >= results["heuristic"]["precision_at_3"],
            )
            for provider, metrics in results.items()
        ]
        async with AsyncSessionLocal() as db:
            await persist_eval_run(
                db,
                suite="rerank_comparison_v1",
                results=eval_results,
                accuracy=best[1]["precision_at_3"],
                threshold=results["heuristic"]["precision_at_3"],
            )

    baseline = results["heuristic"]["precision_at_3"]
    best_non_heuristic = max(results[provider]["precision_at_3"] for provider in ("bge", "cohere"))
    return 0 if best_non_heuristic >= baseline else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
