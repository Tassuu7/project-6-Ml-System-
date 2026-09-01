"""
DataMorph Studio - Pipeline Runs API Router
Tracks execution history, step breakdown metrics, duration, rows/cols processed, and statuses.
"""

import time
from typing import Dict, List, Any, Optional

def record_pipeline_run(db, run_data: Dict[str, Any]):
    """Saves a pipeline run execution log to the database."""
    run_id = run_data.get("run_id") or f"run_{int(time.time() * 1000)}"
    run_data["run_id"] = run_id
    run_data.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    
    # Store in execution history
    db.append("execution_history", run_data)
    return run_id

def handle_get_runs(db, query_params: Optional[Dict[str, Any]] = None) -> tuple:
    """Returns all pipeline runs or a specific run by ID."""
    query_params = query_params or {}
    run_id = query_params.get("id", [None])[0] if isinstance(query_params.get("id"), list) else query_params.get("id")
    
    history = db.get_all("execution_history")
    if isinstance(history, dict):
        history = list(history.values())
    elif not isinstance(history, list):
        history = []
    
    if run_id:
        for r in history:
            if r.get("run_id") == run_id:
                return 200, {"status": "success", "run": r}
        return 404, {"error": f"Run '{run_id}' not found"}
    
    # Return all runs sorted newest first
    sorted_runs = sorted(history, key=lambda x: x.get("created_at", ""), reverse=True)
    return 200, {
        "status": "success",
        "runs": sorted_runs,
        "total_runs": len(sorted_runs)
    }
