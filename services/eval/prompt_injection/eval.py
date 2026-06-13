"""Prompt-injection adversarial eval."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from services.agents.prompts.sanitize import detect_injection, wrap_for_agent

DATASET = Path(__file__).resolve().parent.parent / "datasets" / "prompt_injection.json"


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=1.0)
    args = parser.parse_args()

    cases = json.loads(DATASET.read_text(encoding="utf-8"))
    passed = 0
    for case in cases:
        detected = detect_injection(case["content"])
        wrapped = wrap_for_agent(case["content"])
        ok = detected == case["should_detect"] and "<source_document>" in wrapped
        if ok:
            passed += 1
        else:
            print(f"FAIL {case['id']}: detected={detected} expected={case['should_detect']}")

    accuracy = passed / max(1, len(cases))
    print(f"Prompt injection eval: {accuracy:.1%} ({passed}/{len(cases)})")
    return 0 if accuracy >= args.threshold else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
