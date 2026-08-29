"""
DataMorph Studio - Statistical Dataset Profiler
Generates statistical distributions, histograms, percentiles, and correlations.
"""

from typing import Dict, Any, List
from datamorph.core.dataframe import DataFrame
from datamorph.utils.math_utils import pearson_correlation


class DatasetProfiler:
    """Profiles tabular datasets generating summary charts and metrics."""

    def profile(self, df: DataFrame) -> Dict[str, Any]:
        stats = df.describe()
        num_cols = df.numeric_columns()
        
        # Calculate correlation matrix
        corr_matrix = {}
        for c1 in num_cols:
            corr_matrix[c1] = {}
            for c2 in num_cols:
                if c1 == c2:
                    corr_matrix[c1][c2] = 1.0
                else:
                    corr = pearson_correlation(df[c1].values_numeric(), df[c2].values_numeric())
                    corr_matrix[c1][c2] = round(corr, 4) if corr is not None else 0.0

        # Histograms
        histograms = {}
        for c in num_cols:
            vals = df[c].values_numeric()
            if vals:
                c_min, c_max = min(vals), max(vals)
                n_bins = 10
                step = (c_max - c_min) / float(n_bins) if c_max > c_min else 1.0
                bins = [0] * n_bins
                for v in vals:
                    b_idx = min(int((v - c_min) / step), n_bins - 1)
                    bins[b_idx] += 1
                histograms[c] = {
                    "counts": bins,
                    "bin_edges": [round(c_min + i * step, 2) for i in range(n_bins + 1)]
                }

        return {
            "row_count": len(df),
            "col_count": len(df.columns),
            "column_stats": stats,
            "correlation_matrix": corr_matrix,
            "histograms": histograms
        }
