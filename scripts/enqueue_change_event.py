"""Publish a classified change to the SQS change-event queue."""

from __future__ import annotations

import argparse
import json

import boto3

from services.api.config import get_settings
from services.ingestion.severity import ClassifiedChange


def main() -> None:
    parser = argparse.ArgumentParser(description="Enqueue a change event for the agent pipeline")
    parser.add_argument("--payload", required=True, help="Path to JSON file with ClassifiedChange")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.sqs_queue_url:
        raise SystemExit("SQS_QUEUE_URL is required")

    with open(args.payload, encoding="utf-8") as handle:
        payload = json.load(handle)
    change = ClassifiedChange.model_validate(payload)

    client = boto3.client("sqs", region_name=settings.aws_region)
    client.send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=change.model_dump_json(),
    )
    print(f"Enqueued change for clause {change.clause_id}")


if __name__ == "__main__":
    main()
