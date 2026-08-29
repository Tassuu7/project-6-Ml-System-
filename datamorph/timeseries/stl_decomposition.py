"""
DataMorph Studio - Seasonal-Trend Decomposition using LOESS / Moving Averages
Separates time-series signals into additive or multiplicative Trend, Seasonality, and Residual components.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean


class SeasonalTrendDecomposer(BaseTransformer):
    def __init__(self, period: int = 7, model: str = "additive",
                 columns: Optional[List[str]] = None, name: str = "SeasonalTrendDecomposer"):
        super().__init__(columns=columns, name=name)
        self.period = max(2, period)
        self.model = model.lower()

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SeasonalTrendDecomposer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()
        n = len(df)

        for col in target_cols:
            raw = [float(x) if x is not None else 0.0 for x in df[col].to_list()]
            
            # Trend via centered moving average
            trend = []
            half = self.period // 2
            for i in range(n):
                window = raw[max(0, i - half):min(n, i + half + 1)]
                trend.append(round(mean(window) or 0.0, 4))

            # Detrended
            detrended = [r - t for r, t in zip(raw, trend)]
            
            # Seasonal averages per period index
            seasonal_profile = [0.0] * self.period
            counts = [0] * self.period
            for i in range(n):
                idx = i % self.period
                seasonal_profile[idx] += detrended[i]
                counts[idx] += 1
            seasonal_profile = [round(s / max(1, c), 4) for s, c in zip(seasonal_profile, counts)]

            seasonal = [seasonal_profile[i % self.period] for i in range(n)]
            residual = [round(r - t - s, 4) for r, t, s in zip(raw, trend, seasonal)]

            result.add_column(f"{col}_trend", trend)
            result.add_column(f"{col}_seasonal", seasonal)
            result.add_column(f"{col}_residual", residual)

        return result
