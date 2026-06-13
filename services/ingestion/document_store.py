"""Local versioned document store for diffing."""

from __future__ import annotations

from pathlib import Path

from services.ingestion.models import ParsedDocument

DEFAULT_STORE_DIR = Path("data/document_store")


def store_path(document_id: str, base_dir: Path = DEFAULT_STORE_DIR) -> Path:
    return base_dir / f"{document_id}.json"


def load_previous(document_id: str, base_dir: Path = DEFAULT_STORE_DIR) -> ParsedDocument | None:
    path = store_path(document_id, base_dir)
    if not path.exists():
        return None
    return ParsedDocument.model_validate_json(path.read_text(encoding="utf-8"))


def save_document(document: ParsedDocument, base_dir: Path = DEFAULT_STORE_DIR) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    path = store_path(document.document_id, base_dir)
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")
