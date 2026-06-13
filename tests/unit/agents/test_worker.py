"""Tests for SQS worker message parsing."""

import json

import pytest
from pydantic import ValidationError

from services.agents.worker import parse_message
from services.ingestion.diff_engine import ChangeType
from services.ingestion.severity import ClassifiedChange, Severity


def test_parse_pipeline_message() -> None:
    payload = {
        "type": "pipeline",
        "classified_change": {
            "document_id": "ecfr-21-101",
            "clause_id": "ecfr:21:101:101.1",
            "change_type": "MODIFIED",
            "severity": "SUBSTANTIVE",
            "old_text": "Old",
            "new_text": "New",
            "effective_date": "2025-01-01",
            "source": "ecfr",
            "reason": "test",
        },
    }
    parsed = parse_message(json.dumps(payload))
    assert parsed["type"] == "pipeline"
    change = ClassifiedChange.model_validate(parsed["classified_change"])
    assert change.change_type == ChangeType.MODIFIED


def test_parse_legacy_pipeline_body() -> None:
    payload = {
        "document_id": "ecfr-21-101",
        "clause_id": "ecfr:21:101:101.1",
        "change_type": "MODIFIED",
        "severity": "SUBSTANTIVE",
        "old_text": "Old",
        "new_text": "New",
        "effective_date": "2025-01-01",
        "source": "ecfr",
        "reason": "test",
    }
    parsed = parse_message(json.dumps(payload))
    change = ClassifiedChange.model_validate(parsed)
    assert change.severity == Severity.SUBSTANTIVE


def test_parse_relevance_recheck_message() -> None:
    payload = {
        "type": "relevance_recheck",
        "client_id": "00000000-0000-0000-0000-000000000001",
        "tenant_id": "00000000-0000-0000-0000-000000000002",
    }
    parsed = parse_message(json.dumps(payload))
    assert parsed["type"] == "relevance_recheck"


def test_invalid_json_raises() -> None:
    with pytest.raises(json.JSONDecodeError):
        parse_message("not-json")


def test_invalid_payload_raises() -> None:
    with pytest.raises(ValidationError):
        ClassifiedChange.model_validate({"document_id": "x"})
