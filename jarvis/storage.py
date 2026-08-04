"""Tiny JSON-file persistence used by the notes/reminders/contacts skills.

No database, no network: everything lives in a single JSON file on disk so
the assistant keeps working with zero setup and zero external services.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path.home() / ".jarvis" / "memory.json"


class Storage:
    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except json.JSONDecodeError:
                return {}
        return {}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2, default=str))

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value
            self._save()
