"""
DataMorph Studio - Pipeline Cron Scheduler & Distributed Task Runner
Manages recurring preprocessing executions, backfills, and error retry state machines.
"""

import time
from typing import Dict, List, Callable, Any, Optional


class CronJob:
    """Encapsulates a scheduled DAG execution workflow."""
    def __init__(self, job_id: str, dag_name: str, interval_seconds: int, callback: Optional[Callable] = None):
        self.job_id = job_id
        self.dag_name = dag_name
        self.interval = interval_seconds
        self.callback = callback
        self.last_run_timestamp: float = 0.0
        self.total_runs: int = 0
        self.failure_count: int = 0
        self.is_active: bool = True

    def should_run(self, current_time: float) -> bool:
        return self.is_active and (current_time - self.last_run_timestamp >= self.interval)

    def execute(self) -> Dict[str, Any]:
        self.last_run_timestamp = time.time()
        self.total_runs += 1
        status = "SUCCESS"
        error_msg = None
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                status = "FAILED"
                error_msg = str(e)
                self.failure_count += 1

        return {
            "job_id": self.job_id,
            "dag_name": self.dag_name,
            "run_number": self.total_runs,
            "status": status,
            "timestamp": self.last_run_timestamp,
            "error": error_msg
        }


class PipelineScheduler:
    """Production Cron Job Execution Engine."""
    def __init__(self):
        self.jobs: Dict[str, CronJob] = {}

    def schedule(self, job_id: str, dag_name: str, interval_seconds: int = 3600, callback: Optional[Callable] = None) -> CronJob:
        job = CronJob(job_id, dag_name, interval_seconds, callback)
        self.jobs[job_id] = job
        return job

    def run_due_jobs(self) -> List[Dict[str, Any]]:
        now = time.time()
        results = []
        for job in self.jobs.values():
            if job.should_run(now):
                res = job.execute()
                results.append(res)
        return results
