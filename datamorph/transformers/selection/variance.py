"""
DataMorph Studio - Variance Threshold Feature Selector
Removes low-variance (quasi-constant) features below a configurable threshold.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class VarianceThresholdSelector(BaseTransformer):
    def __init__(self, threshold: float = 0.0, columns: Optional[List[str]] = None, name: str = "VarianceThresholdSelector"):
        super().__init__(columns=columns, name=name)
        self.threshold = threshold
        self.variances_: Dict[str, float] = {}
        self.selected_columns_: List[str] = []

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "VarianceThresholdSelector":
        target_cols = self._resolve_columns(df)
        self.variances_ = {}
        self.selected_columns_ = []

        for col in target_cols:
            v = df[col].var()
            var_val = v if v is not None else 0.0
            self.variances_[col] = var_val
            if var_val > self.threshold:
                self.selected_columns_.append(col)

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = DataFrame()
        for col in self.selected_columns_:
            if col in df.columns:
                result.add_column(col, df[col].to_list())
        # Preserve columns that were not part of target selection
        for col in df.columns:
            if col not in self.columns and col not in result.columns:
                result.add_column(col, df[col].to_list())
        return result
