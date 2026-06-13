"""SQS enqueue helper tests."""

from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

from services.api.config import Settings
from services.api.services.sqs_queue import enqueue_pipeline_change, enqueue_relevance_recheck
from services.ingestion.diff_engine import ChangeType
from services.ingestion.severity import ClassifiedChange, Severity


def test_enqueue_pipeline_change_skips_without_queue_url() -> None:
    settings = Settings(sqs_queue_url="")
    classified = ClassifiedChange(
        document_id="ecfr-21-101",
        clause_id="ecfr:21:101:101.1",
        change_type=ChangeType.MODIFIED,
        severity=Severity.SUBSTANTIVE,
        old_text="Old",
        new_text="New",
        effective_date=date(2025, 1, 1),
        source="ecfr",
        reason="test",
    )
    with patch("services.api.services.sqs_queue.get_settings", return_value=settings):
        assert enqueue_pipeline_change(classified) is False


def test_enqueue_relevance_recheck_publishes_message() -> None:
    settings = Settings(sqs_queue_url="https://sqs.us-east-1.amazonaws.com/123/queue")
    mock_client = MagicMock()
    client_id = uuid.uuid4()
    tenant_id = uuid.uuid4()

    with (
        patch("services.api.services.sqs_queue.get_settings", return_value=settings),
        patch("services.api.services.sqs_queue._client", return_value=mock_client),
    ):
        ok = enqueue_relevance_recheck(client_id=client_id, tenant_id=tenant_id)

    assert ok is True
    mock_client.send_message.assert_called_once()
    body = mock_client.send_message.call_args.kwargs["MessageBody"]
    assert "relevance_recheck" in body
    assert str(client_id) in body
