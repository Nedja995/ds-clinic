"""
Generic file-per-record JSON collection backed by a filesystem directory.

Each record is stored as  {record_id}.json
An _index.json file maintains lightweight metadata for fast listing without
loading full records.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_INDEX_FILE = "_index.json"

logger = logging.getLogger(__name__)


class JsonCollection(Generic[T]):
    """
    File-per-record JSON collection.

    Args:
        dir_path:      Directory where records are stored (created if missing).
        model_class:   Pydantic model class used for de/serialisation.
        index_fields:  Dot-separated field paths extracted into _index.json for
                       fast listing (e.g. ['report_date', 'content.patient_name']).
    """

    def __init__(
        self,
        dir_path: Path,
        model_class: Type[T],
        index_fields: list[str] | None = None,
    ) -> None:
        self._dir = dir_path
        self._model_class = model_class
        self._index_fields: list[str] = index_fields or []
        self._index_path = dir_path / _INDEX_FILE
        self._dir.mkdir(parents=True, exist_ok=True)
        if not self._index_path.exists():
            self._write_raw_index([])


    # ── Internal helpers ──────────────────────────────────────────────────────

    def _record_path(self, record_id: str) -> Path:
        return self._dir / f"{record_id}.json"

    def _load_raw_index(self) -> list[dict]:
        try:
            return json.loads(self._index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_raw_index(self, index: list[dict]) -> None:
        try:
            self._index_path.write_text(
                json.dumps(index, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
        except OSError as e:
            logger.error("Failed to write index file %s: %s", self._index_path, e, exc_info=True)
            raise

    def _build_index_entry(self, record_id: str, model: T) -> dict:
        """Extract a flat index entry from a model using dot-notation field paths."""
        data: dict = model.model_dump(mode="json")
        entry: dict = {"id": record_id}
        for field_path in self._index_fields:
            value = data
            for key in field_path.split("."):
                value = value.get(key) if isinstance(value, dict) else None
            # Store under a flat key: 'content.patient_name' → 'content_patient_name'
            entry[field_path.replace(".", "_")] = value
        return entry

    def _rebuild_index_from_disk(self) -> None:
        """Rebuild _index.json by scanning all .json records on disk."""
        entries: list[dict] = []
        for record_file in sorted(self._dir.glob("*.json")):
            if record_file.name == _INDEX_FILE:
                continue
            record_id = record_file.stem
            model = self.load(record_id)
            if model is not None:
                entries.append(self._build_index_entry(record_id, model))
        self._write_raw_index(entries)


    # ── Public API ────────────────────────────────────────────────────────────

    def save(self, record_id: str, model: T) -> None:
        """Insert or update a record (upsert)."""
        try:
            self._record_path(record_id).write_text(
                model.model_dump_json(indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            logger.error("Failed to write record %r to %s: %s", record_id, self._dir, e, exc_info=True)
            raise

        index = self._load_raw_index()
        entry = self._build_index_entry(record_id, model)
        # Replace existing entry or prepend new one
        index = [e for e in index if e.get("id") != record_id]
        index.insert(0, entry)
        self._write_raw_index(index)

    def load(self, record_id: str) -> Optional[T]:
        """Load a single record by id. Returns None if not found or unreadable."""
        path = self._record_path(record_id)
        if not path.exists():
            return None
        try:
            return self._model_class.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to read record file %s: %s", path, e, exc_info=True)
            return None
        except ValidationError as e:
            logger.error("Record %r failed schema validation: %s", record_id, e, exc_info=True)
            return None

    def delete(self, record_id: str) -> bool:
        """Delete a record. Returns True if deleted, False if not found."""
        path = self._record_path(record_id)
        if not path.exists():
            return False
        try:
            path.unlink()
        except OSError as e:
            logger.error("Failed to delete record file %s: %s", path, e, exc_info=True)
            raise
        index = [e for e in self._load_raw_index() if e.get("id") != record_id]
        self._write_raw_index(index)
        return True

    def exists(self, record_id: str) -> bool:
        return self._record_path(record_id).exists()

    def list_index(self) -> list[dict]:
        """Return lightweight index entries (fast — no record files opened)."""
        return self._load_raw_index()

    def list_all(self) -> list[T]:
        """Load and return all records (expensive — opens every file)."""
        records: list[T] = []
        for entry in self._load_raw_index():
            record = self.load(entry["id"])
            if record is not None:
                records.append(record)
        return records

    def count(self) -> int:
        return len(self._load_raw_index())
