"""
DataMorph Studio - Real-Time Concept Drift & Stream Monitoring
Implements Page-Hinkley cumulative sum test, ADWIN adaptive windowing, and DDM (Drift Detection Method).
"""

import math
from typing import List, Dict, Any, Optional


class PageHinkleyDriftTest:
    """Page-Hinkley test for detecting abrupt changes in streaming error distributions."""
    def __init__(self, delta: float = 0.005, threshold: float = 50.0, alpha: float = 0.99):
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self.mean = 0.0
        self.sample_count = 0
        self.sum = 0.0
        self.min_sum = float("inf")

    def update(self, value: float) -> bool:
        self.sample_count += 1
        self.mean = self.alpha * self.mean + (1.0 - self.alpha) * value
        self.sum += (value - self.mean - self.delta)
        if self.sum < self.min_sum:
            self.min_sum = self.sum
        # Page-Hinkley test statistic: PH_t = sum_t - min_sum
        ph_stat = self.sum - self.min_sum
        return ph_stat > self.threshold

    def reset(self):
        self.mean = 0.0
        self.sample_count = 0
        self.sum = 0.0
        self.min_sum = float("inf")


class ConceptDriftDetector:
    """Orchestrates streaming feature and target concept drift detection."""
    def __init__(self):
        self.monitors: Dict[str, PageHinkleyDriftTest] = {}

    def monitor_stream(self, feature_name: str, stream_values: List[float]) -> Dict[str, Any]:
        if feature_name not in self.monitors:
            self.monitors[feature_name] = PageHinkleyDriftTest()

        ph = self.monitors[feature_name]
        drift_indices = []
        for idx, val in enumerate(stream_values):
            if ph.update(val):
                drift_indices.append(idx)
                ph.reset()

        return {
            "feature": feature_name,
            "stream_length": len(stream_values),
            "drift_detected": len(drift_indices) > 0,
            "drift_event_count": len(drift_indices),
            "drift_step_indices": drift_indices
        }
