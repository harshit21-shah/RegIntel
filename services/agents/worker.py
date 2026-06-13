"""SQS consumer for the LangGraph agent pipeline and async jobs."""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import signal
import uuid
from typing import Any

import boto3
from botocore.exceptions import ClientError
from pydantic import ValidationError

from services.agents.config import get_agent_settings
from services.agents.llm_client import LLMClient
from services.agents.pipeline import run_pipeline
from services.api.config import get_settings
from services.api.db import AsyncSessionLocal
from services.api.deps import set_rls_tenant
from services.graph.sync_profiles import sync_client_profile_by_id
from services.ingestion.severity import ClassifiedChange

logger = logging.getLogger(__name__)


def parse_message(body: str) -> dict[str, Any]:
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("SQS message body must be a JSON object")
    return payload


async def process_pipeline_message(payload: dict[str, Any]) -> None:
    change_payload = payload.get("classified_change", payload)
    classified = ClassifiedChange.model_validate(change_payload)
    agent_settings = get_agent_settings()
    llm = LLMClient(max_cost_usd=agent_settings.max_cost_per_brief_usd)

    async with AsyncSessionLocal() as db:
        result = await run_pipeline(classified, db=db, llm=llm)
        logger.info(
            "Pipeline complete change_event_id=%s status=%s briefs=%d",
            result.change_event_id,
            result.status,
            len(result.brief_ids),
        )


async def process_relevance_recheck(payload: dict[str, Any]) -> None:
    client_id = uuid.UUID(str(payload["client_id"]))
    tenant_id = uuid.UUID(str(payload["tenant_id"]))
    async with AsyncSessionLocal() as db:
        await set_rls_tenant(db, tenant_id)
        await sync_client_profile_by_id(db, client_id)
        logger.info("Relevance re-check completed for client %s", client_id)


async def process_message(body: str) -> None:
    payload = parse_message(body)
    message_type = payload.get("type", "pipeline")
    if message_type == "relevance_recheck":
        await process_relevance_recheck(payload)
        return
    await process_pipeline_message(payload)


async def poll_queue(*, queue_url: str, region: str, wait_seconds: int = 20) -> None:
    client = boto3.client("sqs", region_name=region)
    logger.info("Agent worker polling %s", queue_url)

    while True:
        try:
            response = client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=wait_seconds,
                VisibilityTimeout=900,
            )
        except ClientError:
            logger.exception("Failed to receive SQS messages")
            await asyncio.sleep(5)
            continue

        messages = response.get("Messages", [])
        if not messages:
            await asyncio.sleep(0)
            continue

        for message in messages:
            receipt = message["ReceiptHandle"]
            body = message.get("Body", "{}")
            try:
                await process_message(body)
                client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)
            except (ValidationError, ValueError, json.JSONDecodeError):
                logger.exception("Poison message; deleting to prevent infinite retries")
                client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt)
            except Exception:
                logger.exception("Failed to process message; leaving on queue for retry")
                client.change_message_visibility(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt,
                    VisibilityTimeout=60,
                )


def main() -> None:
    logging.basicConfig(level=get_settings().log_level)
    settings = get_settings()
    if not settings.sqs_queue_url:
        raise SystemExit("SQS_QUEUE_URL is required for the agent worker")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            loop.add_signal_handler(sig, loop.stop)

    try:
        loop.run_until_complete(
            poll_queue(
                queue_url=settings.sqs_queue_url,
                region=settings.aws_region,
            )
        )
    finally:
        loop.close()


if __name__ == "__main__":
    main()
