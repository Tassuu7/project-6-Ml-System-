"""
DataMorph Studio - Cyclical Date-Time Feature Transformer
Encodes periodic time features (hour, day of week, month) using Sine and Cosine trigonometrics.
"""

import math
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class CyclicalDateTimeEncoder(BaseTransformer):
    def __init__(self, period_map: Optional[dict] = None,
                 columns: Optional[List[str]] = None, name: str = "CyclicalDateTimeEncoder"):
        super().__init__(columns=columns, name=name)
        # default periods: hour=24, day_of_week=7, month=12
        self.period_map = period_map or {"hour": 24.0, "day": 31.0, "month": 12.0, "weekday": 7.0}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CyclicalDateTimeEncoder":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            period = self.period_map.get(col, 24.0)
            sin_vals = []
            cos_vals = []
            for v in df[col].to_list():
                try:
                    val = float(v)
                    sin_vals.append(round(math.sin(2 * math.pi * val / period), 6))
                    cos_vals.append(round(math.cos(2 * math.pi * val / period), 6))
                except Exception:
                    sin_vals.append(None)
                    cos_vals.append(None)
            result.add_column(f"{col}_sin", sin_vals)
            result.add_column(f"{col}_cos", cos_vals)

        return result
