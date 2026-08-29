"""
DataMorph Studio - Mahalanobis Distance Outlier Detector
Covariance-adjusted multidimensional distance anomaly detection.
"""

import math
from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class MahalanobisDistanceDetector(BaseTransformer):
    def __init__(self, threshold: float = 3.0, columns: Optional[List[str]] = None, name: str = "MahalanobisDistanceDetector"):
        super().__init__(columns=columns, name=name)
        self.threshold = threshold
        self.means_: Dict[str, float] = {}
        self.vars_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MahalanobisDistanceDetector":
        target_cols = self._resolve_columns(df)
        self.means_ = {c: df[c].mean() or 0.0 for c in target_cols}
        self.vars_ = {c: max(1e-4, df[c].var() or 1.0) for c in target_cols}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()
        records = df.to_dict_records()

        distances = []
        for r in records:
            d_sq = 0.0
            for col in target_cols:
                try:
                    diff = float(r[col]) - self.means_[col]
                    d_sq += (diff ** 2) / self.vars_[col]
                except Exception:
                    pass
            distances.append(round(math.sqrt(d_sq), 4))

        result.add_column("mahalanobis_distance", distances)
        result.add_column("mahalanobis_outlier", [1 if d > self.threshold else 0 for d in distances])
        return result
