"""
In-memory log store for hook execution events.
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Dict, List


class HookLogStore:
    """
    Thread-safe in-memory storage for hook execution logs.
    """

    _instance: "HookLogStore" | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._lock = Lock()
        self._entries: List[Dict[str, Any]] = []
        self._max_entries: int = 500
        self._initialized = True

    def set_max_entries(self, max_entries: int) -> None:
        if max_entries <= 0:
            return
        with self._lock:
            self._max_entries = max_entries
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries :]

    def add_entry(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max_entries:
                self._entries = self._entries[-self._max_entries :]

    def get_entries(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._entries)

    def clear(self) -> None:
        with self._lock:
            self._entries = []

