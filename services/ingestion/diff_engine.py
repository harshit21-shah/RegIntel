"""Clause-level diff between parsed document versions."""

from __future__ import annotations

import difflib
from enum import StrEnum

from pydantic import BaseModel, Field

from services.ingestion.models import ParsedClause, ParsedDocument


class ChangeType(StrEnum):
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    MODIFIED = "MODIFIED"
    UNCHANGED = "UNCHANGED"


class ClauseDiff(BaseModel):
    clause_id: str
    change_type: ChangeType
    old_text: str | None = None
    new_text: str | None = None
    semantic_similarity: float | None = None
    text_diff_ratio: float | None = None


class DocumentDiff(BaseModel):
    document_id: str
    old_version_hash: str | None
    new_version_hash: str
    clause_diffs: list[ClauseDiff] = Field(default_factory=list)

    @property
    def material_changes(self) -> list[ClauseDiff]:
        return [d for d in self.clause_diffs if d.change_type != ChangeType.UNCHANGED]


def _similarity(old_text: str, new_text: str) -> float:
    return difflib.SequenceMatcher(None, old_text, new_text).ratio()


def diff_documents(
    previous: ParsedDocument | None,
    current: ParsedDocument,
) -> DocumentDiff:
    old_by_id: dict[str, ParsedClause] = {}
    if previous is not None:
        old_by_id = {clause.clause_id: clause for clause in previous.clauses}

    new_by_id = {clause.clause_id: clause for clause in current.clauses}
    all_ids = set(old_by_id) | set(new_by_id)
    clause_diffs: list[ClauseDiff] = []

    for clause_id in sorted(all_ids):
        old_clause = old_by_id.get(clause_id)
        new_clause = new_by_id.get(clause_id)

        if old_clause is None and new_clause is not None:
            clause_diffs.append(
                ClauseDiff(
                    clause_id=clause_id,
                    change_type=ChangeType.ADDED,
                    new_text=new_clause.text,
                )
            )
        elif new_clause is None and old_clause is not None:
            clause_diffs.append(
                ClauseDiff(
                    clause_id=clause_id,
                    change_type=ChangeType.REMOVED,
                    old_text=old_clause.text,
                )
            )
        elif old_clause is not None and new_clause is not None:
            if old_clause.text == new_clause.text:
                clause_diffs.append(
                    ClauseDiff(clause_id=clause_id, change_type=ChangeType.UNCHANGED)
                )
            else:
                ratio = _similarity(old_clause.text, new_clause.text)
                clause_diffs.append(
                    ClauseDiff(
                        clause_id=clause_id,
                        change_type=ChangeType.MODIFIED,
                        old_text=old_clause.text,
                        new_text=new_clause.text,
                        semantic_similarity=ratio,
                        text_diff_ratio=ratio,
                    )
                )

    return DocumentDiff(
        document_id=current.document_id,
        old_version_hash=previous.version_hash if previous else None,
        new_version_hash=current.version_hash,
        clause_diffs=clause_diffs,
    )
