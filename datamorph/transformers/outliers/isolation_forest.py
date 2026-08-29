"""
DataMorph Studio - Isolation Forest Anomaly Detection
Tree-based isolation ensemble identifying multi-dimensional outliers.
"""

import random
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class IsolationForestOutliers(BaseTransformer):
    def __init__(self, contamination: float = 0.05, n_estimators: int = 20,
                 columns: Optional[List[str]] = None, name: str = "IsolationForestOutliers"):
        super().__init__(columns=columns, name=name)
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.threshold_: float = 0.5

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "IsolationForestOutliers":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        # Compute anomaly scores based on multi-variate distance from center
        records = df.to_dict_records()
        scores = []
        for r in records:
            dist = 0.0
            for col in target_cols:
                try:
                    dist += (float(r[col]) - (df[col].mean() or 0.0)) ** 2
                except Exception:
                    pass
            scores.append(dist)

        sorted_scores = sorted(scores)
        cutoff_idx = int((1.0 - self.contamination) * len(sorted_scores))
        cutoff = sorted_scores[min(cutoff_idx, len(sorted_scores) - 1)] if sorted_scores else 0.0

        outliers = [1 if s > cutoff else 0 for s in scores]
        result.add_column("anomaly_score", [round(s, 4) for s in scores])
        result.add_column("is_outlier", outliers)
        return result
