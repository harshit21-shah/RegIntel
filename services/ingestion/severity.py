"""Severity classification for clause diffs."""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from enum import StrEnum

from pydantic import BaseModel

from services.agents.llm_client import LLMClient
from services.ingestion.diff_engine import ChangeType, ClauseDiff

logger = logging.getLogger(__name__)

OBLIGATION_RE = re.compile(r"\b(shall|must|required by|deadline|no later than)\b", re.I)
DATE_RE = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2}|January|February|March|April|May|June|July|"
    r"August|September|October|November|December)\b",
    re.I,
)
THRESHOLD_RE = re.compile(r"\b\d+(\.\d+)?\s*(percent|%|mg|mcg|ppm)\b", re.I)


class Severity(StrEnum):
    COSMETIC = "COSMETIC"
    SUBSTANTIVE = "SUBSTANTIVE"
    CRITICAL = "CRITICAL"


class ClassifiedChange(BaseModel):
    document_id: str
    clause_id: str
    change_type: ChangeType
    severity: Severity
    old_text: str | None
    new_text: str | None
    effective_date: date | None
    source: str
    reason: str


def classify_rule_based(
    diff: ClauseDiff, *, document_id: str, source: str, effective_date: date
) -> ClassifiedChange | None:
    if diff.change_type == ChangeType.UNCHANGED:
        return None

    text = diff.new_text or diff.old_text or ""
    old_text = diff.old_text or ""
    new_text = diff.new_text or ""

    if diff.change_type == ChangeType.ADDED:
        if OBLIGATION_RE.search(text):
            severity = Severity.CRITICAL if DATE_RE.search(text) else Severity.SUBSTANTIVE
            reason = "New clause with obligation language"
        else:
            severity = Severity.SUBSTANTIVE
            reason = "New clause added"
    elif diff.change_type == ChangeType.REMOVED:
        severity = Severity.SUBSTANTIVE
        reason = "Clause removed"
    else:
        similarity = diff.semantic_similarity or 0.0
        if similarity >= 0.98:
            severity = Severity.COSMETIC
            reason = "Formatting or typo-only change"
        elif THRESHOLD_RE.search(new_text) and THRESHOLD_RE.search(old_text):
            severity = Severity.CRITICAL
            reason = "Numeric threshold change"
        elif DATE_RE.search(new_text) and new_text != old_text:
            severity = Severity.CRITICAL
            reason = "Effective date or deadline change"
        elif OBLIGATION_RE.search(new_text):
            severity = Severity.SUBSTANTIVE
            reason = "Obligation language modified"
        elif 0.85 <= similarity < 0.98:
            return None
        else:
            severity = Severity.SUBSTANTIVE
            reason = "Substantive text modification"

    return ClassifiedChange(
        document_id=document_id,
        clause_id=diff.clause_id,
        change_type=diff.change_type,
        severity=severity,
        old_text=diff.old_text,
        new_text=diff.new_text,
        effective_date=effective_date,
        source=source,
        reason=reason,
    )


async def classify_with_fallback(
    diff: ClauseDiff,
    *,
    document_id: str,
    source: str,
    effective_date: date,
    llm: LLMClient | None = None,
) -> ClassifiedChange | None:
    result = classify_rule_based(
        diff, document_id=document_id, source=source, effective_date=effective_date
    )
    if result is not None:
        return result

    similarity = diff.semantic_similarity or 0.0
    if not (0.85 <= similarity < 0.98) or llm is None:
        return classify_rule_based(
            diff,
            document_id=document_id,
            source=source,
            effective_date=effective_date,
        ) or ClassifiedChange(
            document_id=document_id,
            clause_id=diff.clause_id,
            change_type=diff.change_type,
            severity=Severity.SUBSTANTIVE,
            old_text=diff.old_text,
            new_text=diff.new_text,
            effective_date=effective_date,
            source=source,
            reason="Default substantive classification",
        )

    prompt = (
        "Classify this regulatory clause change severity as COSMETIC, SUBSTANTIVE, or CRITICAL.\n"
        f"Old text:\n{diff.old_text}\n\nNew text:\n{diff.new_text}\n\n"
        'Respond JSON: {"severity":"...", "reason":"..."}'
    )
    try:
        response = await llm.complete(prompt, tier="haiku", prompt_version="severity-v1")
        payload = json.loads(response.content)
        severity = Severity(payload["severity"])
        return ClassifiedChange(
            document_id=document_id,
            clause_id=diff.clause_id,
            change_type=diff.change_type,
            severity=severity,
            old_text=diff.old_text,
            new_text=diff.new_text,
            effective_date=effective_date,
            source=source,
            reason=str(payload.get("reason", "LLM classification")),
        )
    except Exception:
        logger.warning("Haiku severity fallback failed for %s", diff.clause_id, exc_info=True)
        return ClassifiedChange(
            document_id=document_id,
            clause_id=diff.clause_id,
            change_type=diff.change_type,
            severity=Severity.SUBSTANTIVE,
            old_text=diff.old_text,
            new_text=diff.new_text,
            effective_date=effective_date,
            source=source,
            reason="LLM fallback failed; defaulting to SUBSTANTIVE",
        )


def is_pipeline_trigger(severity: Severity) -> bool:
    return severity in {Severity.SUBSTANTIVE, Severity.CRITICAL}
