"""
DataMorph Studio - Rolling Window Statistics Aggregator
Calculates rolling mean, std, min, and max across sequential windows.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean, std_dev


class RollingWindowAggregator(BaseTransformer):
    def __init__(self, window_size: int = 5, operations: List[str] = ["mean", "std", "min", "max"],
                 columns: Optional[List[str]] = None, name: str = "RollingWindowAggregator"):
        super().__init__(columns=columns, name=name)
        self.window_size = max(2, window_size)
        self.operations = operations

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "RollingWindowAggregator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            raw = [float(x) if (x is not None and x != "") else 0.0 for x in df[col].to_list()]
            n = len(raw)
            if "mean" in self.operations:
                roll_mean = []
                for i in range(n):
                    window = raw[max(0, i - self.window_size + 1):i + 1]
                    roll_mean.append(round(mean(window) or 0.0, 4))
                result.add_column(f"{col}_roll_mean_{self.window_size}", roll_mean)
            
            if "std" in self.operations:
                roll_std = []
                for i in range(n):
                    window = raw[max(0, i - self.window_size + 1):i + 1]
                    roll_std.append(round(std_dev(window) or 0.0, 4))
                result.add_column(f"{col}_roll_std_{self.window_size}", roll_std)

        return result
