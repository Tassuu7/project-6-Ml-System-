"""
DataMorph Studio - Monitoring & Drift API Router
Calculates real-time PSI, KS statistics, and quality score diagnostics.
"""

from datamorph.monitoring.drift_detector import DriftDetector
from datamorph.api.dataset_router import ACTIVE_DATASETS


def handle_drift_analysis(body: dict) -> tuple:
    baseline_id = body.get("baseline_dataset_id")
    current_id = body.get("current_dataset_id")

    base_df = ACTIVE_DATASETS.get(baseline_id)
    curr_df = ACTIVE_DATASETS.get(current_id)

    if base_df is None or curr_df is None:
        return 400, {"error": "Both baseline and current datasets must be loaded"}

    detector = DriftDetector()
    report = detector.compute_drift_report(base_df, curr_df)
    return 200, {"drift_report": report}
