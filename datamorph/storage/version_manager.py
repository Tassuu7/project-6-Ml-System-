"""
DataMorph Studio - Dataset Versioning & Schema Diff Engine
Tracks dataset version lineage, detects added/removed columns, type changes, and quality deltas.
"""

from typing import Dict, List, Any, Optional
from datamorph.core.dataframe import DataFrame

class DatasetVersionManager:
    """Manages version lineage and computes schema differences between dataset snapshots."""

    @staticmethod
    def compute_schema_diff(df_v1: DataFrame, df_v2: DataFrame) -> Dict[str, Any]:
        """Computes structural schema and dimension diffs between two DataFrame versions."""
        cols_v1 = set(df_v1.columns)
        cols_v2 = set(df_v2.columns)

        added_columns = list(cols_v2 - cols_v1)
        removed_columns = list(cols_v1 - cols_v2)
        common_columns = list(cols_v1.intersection(cols_v2))

        type_changes = []
        for col in common_columns:
            t1 = df_v1[col].dtype.value
            t2 = df_v2[col].dtype.value
            if t1 != t2:
                type_changes.append({"column": col, "from_type": t1, "to_type": t2})

        r1, c1 = df_v1.shape
        r2, c2 = df_v2.shape

        return {
            "version_comparison": {
                "base_shape": [r1, c1],
                "target_shape": [r2, c2],
                "row_delta": r2 - r1,
                "column_delta": c2 - c1
            },
            "added_columns": added_columns,
            "removed_columns": removed_columns,
            "type_changes": type_changes,
            "has_breaking_changes": len(removed_columns) > 0 or len(type_changes) > 0
        }
