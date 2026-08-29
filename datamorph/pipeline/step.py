"""
DataMorph Studio - Pipeline Step (DAG Node)
Encapsulates a single transformer execution node with dependencies and metadata.
"""

import uuid
from typing import Dict, List, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.types import PipelineExecutionStatus


class PipelineStep:
    """
    Represents an atomic execution step in a data preprocessing pipeline DAG.
    """
    def __init__(self, name: str, transformer: BaseTransformer,
                 depends_on: Optional[List[str]] = None, step_id: Optional[str] = None):
        self.step_id = step_id or str(uuid.uuid4())[:8]
        self.name = name
        self.transformer = transformer
        self.depends_on: List[str] = depends_on or []
        self.status: PipelineExecutionStatus = PipelineExecutionStatus.PENDING
        self.execution_time_ms: float = 0.0
        self.error_message: Optional[str] = None
        self.output_shape: Optional[tuple] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "transformer_type": self.transformer.__class__.__name__,
            "transformer_name": self.transformer.name,
            "columns": self.transformer.columns,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "output_shape": list(self.output_shape) if self.output_shape else None,
            "params": self.transformer.get_params()
        }
