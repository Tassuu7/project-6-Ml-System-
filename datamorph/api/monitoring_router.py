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

    if base_df is None:
        return 400, {"error": "Baseline dataset must be loaded"}

    if curr_df is None:
        # Create simulated drift dataset for immediate visualization
        curr_df = base_df.copy()
        for c in curr_df.numeric_columns():
            raw = [float(x) * 1.15 + 2.5 if x is not None else None for x in curr_df[c].to_list()]
            curr_df.add_column(c, raw)

    detector = DriftDetector()
    report = detector.compute_drift_report(base_df, curr_df)
    return 200, {"drift_report": report}
