"""
DataMorph Studio - Winsorizer Transformer
Caps extreme values at specified lower and upper percentiles (e.g., 5th and 95th).
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class Winsorizer(BaseTransformer):
    def __init__(self, lower_quantile: float = 0.05, upper_quantile: float = 0.95,
                 columns: Optional[List[str]] = None, name: str = "Winsorizer"):
        super().__init__(columns=columns, name=name)
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.caps_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "Winsorizer":
        target_cols = self._resolve_columns(df)
        self.caps_ = {}

        for col in target_cols:
            low = df[col].quantile(self.lower_quantile)
            high = df[col].quantile(self.upper_quantile)
            self.caps_[col] = {
                "lower": low if low is not None else -999999.0,
                "upper": high if high is not None else 999999.0
            }

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cap = self.caps_.get(col, {"lower": -999999.0, "upper": 999999.0})
            result.add_column(col, result[col].clip(lower=cap["lower"], upper=cap["upper"]))

        return result
