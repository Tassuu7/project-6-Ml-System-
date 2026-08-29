"""
DataMorph Studio - Execution Context & State Management
Provides thread-safe state tracking, parameter passing, and telemetry recording
during data preprocessing workflows.
"""

import time
import uuid
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class StepTelemetry:
    """Execution telemetry recorded for a single transformer step."""
    step_id: str
    step_name: str
    start_time: float
    end_time: float = 0.0
    duration_ms: float = 0.0
    rows_in: int = 0
    rows_out: int = 0
    cols_in: int = 0
    cols_out: int = 0
    memory_delta_bytes: int = 0
    status: str = "pending"
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    transformed_columns: List[str] = field(default_factory=list)


class ExecutionContext:
    """
    Thread-safe context passed through pipeline execution graph.
    Maintains run ID, configuration, cache, and execution telemetry.
    """
    def __init__(self, run_id: Optional[str] = None, user_id: str = "system", enable_profiling: bool = True):
        self.run_id = run_id or str(uuid.uuid4())
        self.user_id = user_id
        self.enable_profiling = enable_profiling
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self._lock = threading.RLock()
        self._telemetry: Dict[str, StepTelemetry] = {}
        self._artifacts: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._logs: List[Dict[str, Any]] = []

    def start_step(self, step_id: str, step_name: str, params: Dict[str, Any] = None) -> StepTelemetry:
        with self._lock:
            telemetry = StepTelemetry(
                step_id=step_id,
                step_name=step_name,
                start_time=time.time(),
                status="running",
                parameters=params or {}
            )
            self._telemetry[step_id] = telemetry
            self.log_event("INFO", f"Started step '{step_name}' ({step_id})")
            return telemetry

    def complete_step(self, step_id: str, rows_in: int, rows_out: int, cols_in: int, cols_out: int,
                      transformed_cols: List[str] = None):
        with self._lock:
            if step_id in self._telemetry:
                t = self._telemetry[step_id]
                t.end_time = time.time()
                t.duration_ms = round((t.end_time - t.start_time) * 1000.0, 2)
                t.rows_in = rows_in
                t.rows_out = rows_out
                t.cols_in = cols_in
                t.cols_out = cols_out
                t.transformed_columns = transformed_cols or []
                t.status = "completed"
                self.log_event("INFO", f"Completed step '{t.step_name}' in {t.duration_ms}ms (Shape: {rows_out}x{cols_out})")

    def fail_step(self, step_id: str, error_message: str):
        with self._lock:
            if step_id in self._telemetry:
                t = self._telemetry[step_id]
                t.end_time = time.time()
                t.duration_ms = round((t.end_time - t.start_time) * 1000.0, 2)
                t.status = "failed"
                t.error_message = error_message
                self.log_event("ERROR", f"Failed step '{t.step_name}': {error_message}")

    def put_artifact(self, key: str, artifact: Any):
        with self._lock:
            self._artifacts[key] = artifact

    def get_artifact(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._artifacts.get(key, default)

    def set_metadata(self, key: str, value: Any):
        with self._lock:
            self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._metadata.get(key, default)

    def log_event(self, level: str, message: str, extra: Dict[str, Any] = None):
        with self._lock:
            self._logs.append({
                "timestamp": time.time(),
                "level": level,
                "message": message,
                "extra": extra or {}
            })

    def get_execution_summary(self) -> Dict[str, Any]:
        with self._lock:
            total_duration = round((time.time() - self.start_time) * 1000.0, 2)
            steps_list = [
                {
                    "step_id": t.step_id,
                    "step_name": t.step_name,
                    "duration_ms": t.duration_ms,
                    "status": t.status,
                    "rows_in": t.rows_in,
                    "rows_out": t.rows_out,
                    "cols_in": t.cols_in,
                    "cols_out": t.cols_out,
                    "transformed_columns": t.transformed_columns,
                    "error": t.error_message,
                    "parameters": t.parameters
                }
                for t in self._telemetry.values()
            ]
            return {
                "run_id": self.run_id,
                "user_id": self.user_id,
                "total_duration_ms": total_duration,
                "step_count": len(self._telemetry),
                "steps": steps_list,
                "log_count": len(self._logs),
                "metadata": self._metadata
            }
