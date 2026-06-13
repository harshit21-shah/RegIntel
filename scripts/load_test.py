"""Load test harness — 100 client profiles across 3+ regulatory sources.

Usage:
    python scripts/load_test.py --base-url http://localhost:8000 --profiles 100
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from dataclasses import dataclass

import httpx

SOURCES = ("ecfr", "ca_food_code", "sec_edgar")


@dataclass
class LoadResult:
    profile_requests: int
    change_requests: int
    successes: int
    failures: int
    p50_ms: float
    p95_ms: float


async def _create_profile(client: httpx.AsyncClient, index: int) -> tuple[bool, float]:
    start = time.perf_counter()
    try:
        response = await client.post(
            "/api/v1/profiles",
            json={
                "name": f"Load Test Co {index}",
                "naics_codes": ["311412"],
                "states_of_operation": ["CA", "TX"],
                "product_categories": ["frozen seafood"],
                "supply_chain_jurisdictions": ["US"],
            },
        )
        ok = response.status_code == 201
    except httpx.HTTPError:
        ok = False
    return ok, (time.perf_counter() - start) * 1000


async def _list_changes(client: httpx.AsyncClient, source: str) -> tuple[bool, float]:
    start = time.perf_counter()
    try:
        response = await client.get("/api/v1/changes", params={"source": source, "page_size": 5})
        ok = response.status_code == 200
    except httpx.HTTPError:
        ok = False
    return ok, (time.perf_counter() - start) * 1000


async def run_load(base_url: str, *, profiles: int, concurrency: int) -> LoadResult:
    sem = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    successes = 0
    failures = 0

    async def run_profile(i: int) -> tuple[bool, float]:
        async with sem:
            return await _create_profile(client, i)

    async def run_source(source: str) -> tuple[bool, float]:
        async with sem:
            return await _list_changes(client, source)

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        profile_tasks = [run_profile(i) for i in range(profiles)]
        source_tasks = [run_source(source) for source in SOURCES]
        results = await asyncio.gather(*profile_tasks, *source_tasks)

    for ok, elapsed_ms in results:
        latencies.append(elapsed_ms)
        if ok:
            successes += 1
        else:
            failures += 1

    latencies.sort()
    return LoadResult(
        profile_requests=profiles,
        change_requests=len(SOURCES),
        successes=successes,
        failures=failures,
        p50_ms=statistics.median(latencies),
        p95_ms=latencies[int(len(latencies) * 0.95) - 1],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="RegIntel production load test")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--profiles", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    result = asyncio.run(
        run_load(args.base_url, profiles=args.profiles, concurrency=args.concurrency)
    )
    total = result.profile_requests + result.change_requests
    print(f"Profile creates: {result.profile_requests}")
    print(f"Source queries ({', '.join(SOURCES)}): {result.change_requests}")
    print(f"Total requests: {total}")
    print(f"Successes: {result.successes}  Failures: {result.failures}")
    print(f"Latency p50={result.p50_ms:.1f}ms p95={result.p95_ms:.1f}ms")

    if result.failures > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
