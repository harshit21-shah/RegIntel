"""AWS Lambda handler for scheduled ingestion."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict[str, object], _context: object) -> dict[str, object]:
    """Run ingestion for configured sources (EventBridge cron)."""
    sources = os.environ.get("INGEST_SOURCES", "ecfr,federal_register,sec_edgar").split(",")
    parts = os.environ.get("INGEST_PARTS", "1,101").split(",")
    cmd = [
        sys.executable,
        "scripts/ingest_sources.py",
        "--sources",
        *sources,
        "--parts",
        *parts,
    ]
    logger.info("Starting ingestion: %s", " ".join(cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    logger.info("stdout: %s", completed.stdout[-2000:])
    if completed.returncode != 0:
        logger.error("stderr: %s", completed.stderr[-2000:])
        raise RuntimeError(f"Ingestion failed with code {completed.returncode}")
    return {
        "statusCode": 200,
        "body": json.dumps({"sources": sources, "status": "ok"}),
    }
