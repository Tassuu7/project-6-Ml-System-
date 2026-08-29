"""
DataMorph Studio - Embedded JSON Database
Lightweight file-backed document store for users, datasets, pipelines, and audit logs.
"""

import json
import os
import threading
from typing import Dict, List, Any, Optional


class Database:
    """Thread-safe persistent JSON document storage."""
    def __init__(self, db_path: str = "data/datamorph_db.json"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {
            "users": {},
            "datasets": {},
            "pipelines": {},
            "execution_history": [],
            "audit_logs": []
        }
        self._load()

    def _load(self):
        with self._lock:
            if os.path.exists(self.db_path):
                try:
                    with open(self.db_path, "r", encoding="utf-8") as f:
                        self._data = json.load(f)
                except Exception:
                    pass

    def _save(self):
        with self._lock:
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)

    def set(self, collection: str, key: str, value: Any):
        with self._lock:
            self._data.setdefault(collection, {})[key] = value
            self._save()

    def get(self, collection: str, key: str) -> Optional[Any]:
        with self._lock:
            return self._data.get(collection, {}).get(key)

    def get_all(self, collection: str) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data.get(collection, {}))

    def delete(self, collection: str, key: str):
        with self._lock:
            if key in self._data.get(collection, {}):
                del self._data[collection][key]
                self._save()

    def append(self, collection: str, item: Any):
        with self._lock:
            self._data.setdefault(collection, []).append(item)
            self._save()
