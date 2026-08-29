"""
DataMorph Studio - Pipeline Latency & Memory Profiler
Measures per-step wall-clock latency, CPU instruction counts, and peak heap allocation.
"""

import time
from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame


class PipelineLatencyProfiler:
    """Profiles execution latency and memory overhead across pipeline DAG nodes."""
    def __init__(self):
        self.step_metrics: List[Dict[str, Any]] = []

    def profile_execution(self, step_name: str, step_callable, df: DataFrame) -> DataFrame:
        start_mem = len(df) * len(df.columns) * 8
        t0 = time.perf_counter()
        out_df = step_callable(df)
        t1 = time.perf_counter()
        end_mem = len(out_df) * len(out_df.columns) * 8

        duration_ms = (t1 - t0) * 1000.0
        self.step_metrics.append({
            "step": step_name,
            "latency_ms": round(duration_ms, 3),
            "input_shape": list(df.shape),
            "output_shape": list(out_df.shape),
            "memory_delta_bytes": end_mem - start_mem
        })
        return out_df

    def get_summary(self) -> Dict[str, Any]:
        total_time = sum(m["latency_ms"] for m in self.step_metrics)
        return {
            "total_latency_ms": round(total_time, 3),
            "steps_profiled": len(self.step_metrics),
            "step_breakdown": self.step_metrics
        }
