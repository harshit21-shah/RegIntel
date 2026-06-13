"""SQS message publishing for async pipeline and re-evaluation jobs."""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

import boto3
from botocore.exceptions import ClientError

from services.api.config import Settings, get_settings
from services.ingestion.severity import ClassifiedChange

logger = logging.getLogger(__name__)


def _client(settings: Settings | None = None) -> Any:
    settings = settings or get_settings()
    return boto3.client("sqs", region_name=settings.aws_region)


def publish_message(payload: dict[str, Any], *, settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    if not settings.sqs_queue_url:
        logger.debug("SQS_QUEUE_URL not configured; skipping enqueue")
        return False
    try:
        _client(settings).send_message(
            QueueUrl=settings.sqs_queue_url,
            MessageBody=json.dumps(payload),
        )
        return True
    except ClientError:
        logger.exception("Failed to publish SQS message")
        return False


def enqueue_pipeline_change(classified: ClassifiedChange) -> bool:
    return publish_message(
        {
            "type": "pipeline",
            "classified_change": classified.model_dump(mode="json"),
        }
    )


def enqueue_relevance_recheck(*, client_id: UUID, tenant_id: UUID) -> bool:
    return publish_message(
        {
            "type": "relevance_recheck",
            "client_id": str(client_id),
            "tenant_id": str(tenant_id),
        }
    )
