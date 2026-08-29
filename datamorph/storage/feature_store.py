"""
DataMorph Studio - In-Memory Feature Store
Manages feature entities, versioned feature sets, and online/offline retrieval.
"""

import time
from typing import Dict, List, Any, Optional
from datamorph.core.dataframe import DataFrame


class FeatureStore:
    """Central store for curated ML features and entity lookups."""
    def __init__(self):
        self._feature_views: Dict[str, Dict[str, Any]] = {}

    def register_feature_view(self, name: str, df: DataFrame, entity_key: str,
                              description: str = "", tags: List[str] = None):
        self._feature_views[name] = {
            "name": name,
            "entity_key": entity_key,
            "description": description,
            "tags": tags or [],
            "features": df.columns,
            "data": df.to_dict_records(),
            "created_at": time.time(),
            "row_count": len(df)
        }

    def get_feature_view(self, name: str) -> Optional[Dict[str, Any]]:
        return self._feature_views.get(name)

    def list_feature_views(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": v["name"],
                "entity_key": v["entity_key"],
                "description": v["description"],
                "tags": v["tags"],
                "feature_count": len(v["features"]),
                "row_count": v["row_count"],
                "created_at": v["created_at"]
            }
            for v in self._feature_views.values()
        ]
