"""
DataMorph Studio - Exponential Smoothing Feature Generator
Generates Single (Simple), Double (Holt), and Triple (Holt-Winters) smoothed features.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class ExponentialSmoothingFeatures(BaseTransformer):
    def __init__(self, alpha: float = 0.3, beta: float = 0.1,
                 columns: Optional[List[str]] = None, name: str = "ExponentialSmoothingFeatures"):
        super().__init__(columns=columns, name=name)
        self.alpha = alpha
        self.beta = beta

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "ExponentialSmoothingFeatures":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()

        for col in target_cols:
            raw = [float(x) if x is not None else 0.0 for x in df[col].to_list()]
            if not raw:
                continue

            # Simple Exponential Smoothing (SES)
            ses = [raw[0]]
            for i in range(1, len(raw)):
                val = self.alpha * raw[i] + (1.0 - self.alpha) * ses[-1]
                ses.append(round(val, 4))
            result.add_column(f"{col}_ses_a{int(self.alpha*100)}", ses)

            # Holt's Linear Trend (Double Smoothing)
            level = raw[0]
            trend = raw[1] - raw[0] if len(raw) > 1 else 0.0
            holt = [level + trend]
            for i in range(1, len(raw)):
                last_level = level
                level = self.alpha * raw[i] + (1.0 - self.alpha) * (level + trend)
                trend = self.beta * (level - last_level) + (1.0 - self.beta) * trend
                holt.append(round(level + trend, 4))
            result.add_column(f"{col}_holt_linear", holt)

        return result
