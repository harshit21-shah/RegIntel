"""Wait for local Docker services before migrations."""

from __future__ import annotations

import socket
import sys
import time

TARGETS: list[tuple[str, str, int]] = [
    ("postgres", "localhost", 5433),
    ("qdrant", "localhost", 6333),
    ("redis", "localhost", 6379),
    ("neo4j", "localhost", 7687),
]


def port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> None:
    deadline = time.time() + 120
    pending = list(TARGETS)
    while pending and time.time() < deadline:
        still_pending: list[tuple[str, str, int]] = []
        for name, host, port in pending:
            if port_open(host, port):
                print(f"  {name} ready on {host}:{port}")
            else:
                still_pending.append((name, host, port))
        pending = still_pending
        if pending:
            time.sleep(2)
    if pending:
        names = ", ".join(name for name, _, _ in pending)
        print(f"Timed out waiting for: {names}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
