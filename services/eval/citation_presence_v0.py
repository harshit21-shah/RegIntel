"""Citation-presence eval v0 for Phase 1 MVP retrieval quality."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from services.retrieval.search import ClauseRetriever

logger = logging.getLogger(__name__)

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "query_v0.json"
DEFAULT_TOP_K = 5
DEFAULT_THRESHOLD = 0.80


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    question: str
    expected_clause_ids: list[str]


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    hit: bool
    retrieved_clause_ids: list[str]
    expected_clause_ids: list[str]


def load_dataset(path: Path = DATASET_PATH) -> list[EvalCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvalCase(
            case_id=item["id"],
            question=item["question"],
            expected_clause_ids=item["expected_clause_ids"],
        )
        for item in raw
    ]


async def run_eval(*, top_k: int = DEFAULT_TOP_K) -> tuple[list[EvalResult], float]:
    retriever = ClauseRetriever()
    dataset = load_dataset()
    results: list[EvalResult] = []

    for case in dataset:
        retrieved = await retriever.search(case.question, top_k=top_k)
        retrieved_ids = [item.clause_id for item in retrieved]
        hit = any(expected in retrieved_ids for expected in case.expected_clause_ids)
        results.append(
            EvalResult(
                case_id=case.case_id,
                hit=hit,
                retrieved_clause_ids=retrieved_ids,
                expected_clause_ids=case.expected_clause_ids,
            )
        )

    recall = sum(1 for result in results if result.hit) / max(1, len(results))
    return results, recall


def print_report(results: list[EvalResult], recall: float, threshold: float) -> None:
    print("RegIntel citation-presence eval v0 (retrieval recall)")
    print(f"Cases: {len(results)}")
    print(f"Retrieval recall@{DEFAULT_TOP_K}: {recall:.1%}")
    print(f"Threshold: {threshold:.0%}")
    print()
    for result in results:
        status = "PASS" if result.hit else "FAIL"
        print(f"[{status}] {result.case_id}")
        if not result.hit:
            print(f"  expected: {result.expected_clause_ids}")
            print(f"  retrieved: {result.retrieved_clause_ids}")
    print()
    if recall >= threshold:
        print("Eval PASSED")
    else:
        print("Eval FAILED")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run RegIntel eval v0")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    results, recall = await run_eval(top_k=args.top_k)
    print_report(results, recall, args.threshold)
    return 0 if recall >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
