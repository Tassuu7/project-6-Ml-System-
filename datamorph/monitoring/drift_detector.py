"""
DataMorph Studio - Statistical Data Drift & Distribution Shift Detector
Implements Population Stability Index (PSI), Kolmogorov-Smirnov 2-sample test,
and Jensen-Shannon Divergence for production feature monitoring.
"""

import math
from typing import Dict, List, Any, Optional
from datamorph.core.dataframe import DataFrame
from datamorph.utils.math_utils import mean, std_dev


class DriftDetector:
    """
    Computes distribution drift between baseline reference data and incoming inference data.
    """
    def __init__(self, psi_threshold: float = 0.2, ks_threshold: float = 0.05):
        self.psi_threshold = psi_threshold
        self.ks_threshold = ks_threshold

    def calculate_psi(self, baseline: List[float], current: List[float], n_bins: int = 10) -> float:
        """Calculates Population Stability Index across continuous feature distributions."""
        if not baseline or not current:
            return 0.0

        b_min, b_max = min(baseline), max(baseline)
        if b_min == b_max:
            return 0.0

        step = (b_max - b_min) / float(n_bins)
        edges = [b_min + i * step for i in range(n_bins + 1)]

        b_counts = [0] * n_bins
        c_counts = [0] * n_bins

        for x in baseline:
            for i in range(n_bins):
                if edges[i] <= x <= edges[i + 1]:
                    b_counts[i] += 1
                    break

        for x in current:
            for i in range(n_bins):
                if edges[i] <= x <= edges[i + 1]:
                    c_counts[i] += 1
                    break

        psi = 0.0
        n_b = len(baseline) or 1
        n_c = len(current) or 1

        for i in range(n_bins):
            p_b = max(1e-4, b_counts[i] / n_b)
            p_c = max(1e-4, c_counts[i] / n_c)
            psi += (p_c - p_b) * math.log(p_c / p_b)

        return round(psi, 4)

    def calculate_ks_statistic(self, baseline: List[float], current: List[float]) -> float:
        """Computes Kolmogorov-Smirnov max supremum divergence metric."""
        if not baseline or not current:
            return 0.0
        s_b = sorted(baseline)
        s_c = sorted(current)
        all_vals = sorted(list(set(s_b + s_c)))

        max_diff = 0.0
        n_b = len(s_b)
        n_c = len(s_c)

        for val in all_vals:
            cdf_b = sum(1 for x in s_b if x <= val) / n_b
            cdf_c = sum(1 for x in s_c if x <= val) / n_c
            diff = abs(cdf_b - cdf_c)
            if diff > max_diff:
                max_diff = diff

        return round(max_diff, 4)

    def compute_drift_report(self, baseline_df: DataFrame, current_df: DataFrame) -> Dict[str, Any]:
        """Analyzes drift across all matching numeric and categorical features."""
        common_cols = [c for c in baseline_df.columns if c in current_df.columns]
        report = {}
        drift_detected_count = 0

        for col in common_cols:
            b_vals = baseline_df[col].values_numeric()
            c_vals = current_df[col].values_numeric()

            if len(b_vals) > 5 and len(c_vals) > 5:
                psi = self.calculate_psi(b_vals, c_vals)
                ks = self.calculate_ks_statistic(b_vals, c_vals)
                is_drifted = (psi >= self.psi_threshold) or (ks >= 0.25)
                
                if is_drifted:
                    drift_detected_count += 1

                report[col] = {
                    "type": "numeric",
                    "psi": psi,
                    "ks_statistic": ks,
                    "drift_detected": is_drifted,
                    "severity": "HIGH" if psi > 0.25 else ("MEDIUM" if psi > 0.1 else "LOW"),
                    "baseline_mean": mean(b_vals),
                    "current_mean": mean(c_vals),
                    "baseline_std": std_dev(b_vals),
                    "current_std": std_dev(c_vals)
                }
            else:
                # Categorical drift via frequency divergence
                b_counts = baseline_df[col].value_counts()
                c_counts = current_df[col].value_counts()
                all_cats = set(b_counts.keys()).union(set(c_counts.keys()))
                cat_drift = 0.0
                for cat in all_cats:
                    p_b = b_counts.get(cat, 0) / max(1, len(baseline_df))
                    p_c = c_counts.get(cat, 0) / max(1, len(current_df))
                    cat_drift += abs(p_b - p_c)
                cat_drift = round(cat_drift / 2.0, 4)
                is_drifted = cat_drift > 0.15
                if is_drifted:
                    drift_detected_count += 1
                report[col] = {
                    "type": "categorical",
                    "total_variation_drift": cat_drift,
                    "drift_detected": is_drifted,
                    "severity": "HIGH" if cat_drift > 0.25 else ("MEDIUM" if cat_drift > 0.1 else "LOW")
                }

        return {
            "total_features_monitored": len(common_cols),
            "features_drifted_count": drift_detected_count,
            "overall_drift_status": "ALERT" if drift_detected_count > 0 else "STABLE",
            "feature_metrics": report
        }
