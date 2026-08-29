"""
DataMorph Studio - Directed Acyclic Graph (DAG) Pipeline Orchestrator
Validates acyclicity, computes topological sort, and manages step graphs.
"""

from typing import Dict, List, Set, Optional, Any
from datamorph.pipeline.step import PipelineStep
from datamorph.core.exceptions import PipelineExecutionError


class PipelineDAG:
    """
    Maintains and validates the directed acyclic graph for pipeline execution.
    """
    def __init__(self, name: str = "PreprocessingPipeline", pipeline_id: Optional[str] = None):
        self.pipeline_id = pipeline_id or "pipe_" + name.lower().replace(" ", "_")
        self.name = name
        self.steps: Dict[str, PipelineStep] = {}

    def add_step(self, step: PipelineStep) -> "PipelineDAG":
        if step.step_id in self.steps:
            raise PipelineExecutionError(f"Duplicate step ID '{step.step_id}' in DAG", pipeline_id=self.pipeline_id)
        self.steps[step.step_id] = step
        self.validate()
        return self

    def remove_step(self, step_id: str):
        if step_id in self.steps:
            del self.steps[step_id]
            for step in self.steps.values():
                if step_id in step.depends_on:
                    step.depends_on.remove(step_id)

    def get_step(self, step_id: str) -> Optional[PipelineStep]:
        return self.steps.get(step_id)

    def validate(self):
        """Checks for missing dependencies and cycles."""
        for step in self.steps.values():
            for dep in step.depends_on:
                if dep not in self.steps:
                    raise PipelineExecutionError(
                        f"Step '{step.name}' depends on unknown step ID '{dep}'",
                        step_id=step.step_id, pipeline_id=self.pipeline_id
                    )
        self.topological_sort()

    def topological_sort(self) -> List[PipelineStep]:
        """Kahn's algorithm for topological ordering."""
        in_degree: Dict[str, int] = {s_id: 0 for s_id in self.steps}
        adj_list: Dict[str, List[str]] = {s_id: [] for s_id in self.steps}

        for step in self.steps.values():
            for dep in step.depends_on:
                adj_list[dep].append(step.step_id)
                in_degree[step.step_id] += 1

        queue = [s_id for s_id, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(self.steps[curr])
            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.steps):
            raise PipelineExecutionError("Cycle detected in pipeline DAG dependencies!", pipeline_id=self.pipeline_id)

        return order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "step_count": len(self.steps),
            "steps": [s.to_dict() for s in self.steps.values()]
        }
