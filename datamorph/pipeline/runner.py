"""
DataMorph Studio - Pipeline Execution Engine & Step Runner
Executes DAG pipelines with state isolation, caching, telemetry, and lineage recording.
"""

import time
from typing import Dict, Any, Optional
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.core.types import PipelineExecutionStatus
from datamorph.pipeline.dag import PipelineDAG
from datamorph.pipeline.lineage import LineageTracker
from datamorph.core.exceptions import PipelineExecutionError


class PipelineRunner:
    """
    Executes a PipelineDAG sequentially or step-by-step.
    """
    def __init__(self, lineage_tracker: Optional[LineageTracker] = None):
        self.lineage_tracker = lineage_tracker or LineageTracker()

    def run(self, dag: PipelineDAG, df: DataFrame,
            context: Optional[ExecutionContext] = None) -> DataFrame:
        ctx = context or ExecutionContext()
        ordered_steps = dag.topological_sort()
        current_df = df.copy()

        for step in ordered_steps:
            step.status = PipelineExecutionStatus.RUNNING
            telemetry = ctx.start_step(step.step_id, step.name, params=step.transformer.get_params())
            start_t = time.time()

            try:
                rows_in, cols_in = current_df.shape
                # Execute fit_transform on active DataFrame
                current_df = step.transformer.fit_transform(current_df, context=ctx)
                rows_out, cols_out = current_df.shape
                
                step.output_shape = (rows_out, cols_out)
                step.status = PipelineExecutionStatus.COMPLETED
                step.execution_time_ms = round((time.time() - start_t) * 1000.0, 2)
                
                ctx.complete_step(
                    step_id=step.step_id,
                    rows_in=rows_in, rows_out=rows_out,
                    cols_in=cols_in, cols_out=cols_out,
                    transformed_cols=step.transformer.columns
                )

                # Record Lineage
                for col in step.transformer.columns:
                    self.lineage_tracker.record_transformation(
                        output_col=col,
                        step_id=step.step_id,
                        transformer_type=step.transformer.__class__.__name__,
                        source_cols=[col]
                    )

            except Exception as e:
                step.status = PipelineExecutionStatus.FAILED
                step.error_message = str(e)
                ctx.fail_step(step.step_id, str(e))
                raise PipelineExecutionError(f"Step '{step.name}' failed: {e}", step_id=step.step_id, pipeline_id=dag.pipeline_id)

        return current_df
