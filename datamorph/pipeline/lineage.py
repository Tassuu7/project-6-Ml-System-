"""
DataMorph Studio - Data Lineage & Provenance Tracker
Tracks column creation, mutations, and step ancestors for audit compliance.
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class LineageNode:
    column_name: str
    created_by_step: str
    source_columns: List[str] = field(default_factory=list)
    transformer_applied: str = ""
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LineageTracker:
    """
    Maintains graph of dataset transformations and column provenance.
    """
    def __init__(self):
        self._lineage_graph: Dict[str, List[LineageNode]] = {}

    def record_transformation(self, output_col: str, step_id: str,
                              transformer_type: str, source_cols: List[str] = None):
        node = LineageNode(
            column_name=output_col,
            created_by_step=step_id,
            source_columns=source_cols or [],
            transformer_applied=transformer_type
        )
        self._lineage_graph.setdefault(output_col, []).append(node)

    def get_column_history(self, column_name: str) -> List[Dict[str, Any]]:
        nodes = self._lineage_graph.get(column_name, [])
        return [
            {
                "column": n.column_name,
                "step_id": n.created_by_step,
                "transformer": n.transformer_applied,
                "source_columns": n.source_columns,
                "timestamp": n.timestamp
            }
            for n in nodes
        ]

    def get_full_graph(self) -> Dict[str, Any]:
        return {
            col: [
                {
                    "step_id": n.created_by_step,
                    "transformer": n.transformer_applied,
                    "sources": n.source_columns
                }
                for n in nodes
            ]
            for col, nodes in self._lineage_graph.items()
        }
