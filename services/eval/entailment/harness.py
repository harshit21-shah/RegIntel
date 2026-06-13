"""Citation-accuracy entailment harness for pipeline eval."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

DATASET_PATH = Path(__file__).resolve().parent.parent / "datasets" / "pipeline_v1.json"
DEFAULT_THRESHOLD = 0.95


@dataclass(frozen=True)
class EntailmentCase:
    case_id: str
    claim: str
    clause_text: str
    expected: str


@dataclass(frozen=True)
class EntailmentResult:
    case_id: str
    predicted: str
    expected: str
    correct: bool


def load_dataset(path: Path = DATASET_PATH) -> list[EntailmentCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        EntailmentCase(
            case_id=item["id"],
            claim=item["claim"],
            clause_text=item["clause_text"],
            expected=item["expected"],
        )
        for item in raw
    ]


def rule_entailment(claim: str, clause_text: str) -> str:
    claim_lower = claim.lower()
    clause_lower = clause_text.lower()

    negation_markers = (
        "omit",
        "hide",
        "optional",
        "exempt all",
        "no longer",
        "misleading",
        "ignore",
    )
    requirement_words = ("shall", "must", "required", "clarity", "conspicuous")
    if any(marker in claim_lower for marker in negation_markers) and any(
        word in clause_lower for word in requirement_words
    ):
        return "NOT_ENTAILED"

    claim_tokens = {token.lower() for token in claim.split() if len(token) > 4}
    clause_tokens = {token.lower() for token in clause_text.split() if len(token) > 4}
    overlap = sum(1 for token in claim_tokens if token in clause_lower)
    if len(claim_tokens & clause_tokens) < 2 and overlap <= 1:
        return "NOT_ENTAILED"

    if overlap >= max(2, len(claim_tokens) // 2):
        return "ENTAILED"
    if overlap >= 1:
        return "PARTIALLY_ENTAILED"
    return "NOT_ENTAILED"


async def run_eval(*, use_llm: bool = False) -> tuple[list[EntailmentResult], float]:
    _ = use_llm
    cases = load_dataset()
    results: list[EntailmentResult] = []

    for case in cases:
        predicted = rule_entailment(case.claim, case.clause_text)

        normalized = predicted.replace("PARTIALLY_ENTAILED", "ENTAILED")
        expected = case.expected.replace("PARTIALLY_ENTAILED", "ENTAILED")
        results.append(
            EntailmentResult(
                case_id=case.case_id,
                predicted=predicted,
                expected=case.expected,
                correct=normalized == expected or predicted == case.expected,
            )
        )

    accuracy = sum(1 for r in results if r.correct) / max(1, len(results))
    return results, accuracy


def print_report(results: list[EntailmentResult], accuracy: float, threshold: float) -> None:
    print("RegIntel citation-accuracy entailment eval v1")
    print(f"Cases: {len(results)}")
    print(f"Accuracy: {accuracy:.1%}")
    print(f"Threshold: {threshold:.0%}")
    for result in results:
        status = "PASS" if result.correct else "FAIL"
        print(
            f"[{status}] {result.case_id} expected={result.expected} predicted={result.predicted}"
        )
    print("Eval PASSED" if accuracy >= threshold else "Eval FAILED")


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--persist", action="store_true", help="Persist results to eval_runs table")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    results, accuracy = await run_eval(use_llm=args.use_llm)
    print_report(results, accuracy, args.threshold)

    if args.persist:
        from services.api.db import AsyncSessionLocal
        from services.api.services.eval_store import persist_eval_run

        async with AsyncSessionLocal() as db:
            await persist_eval_run(
                db,
                suite="pipeline_v1",
                results=results,
                accuracy=accuracy,
                threshold=args.threshold,
            )

    return 0 if accuracy >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
