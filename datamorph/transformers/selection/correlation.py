"""
DataMorph Studio - Correlation Filter Feature Selector
Removes collinear / redundant features with absolute Pearson correlation above threshold.
"""

from typing import List, Optional, Dict, Set
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import pearson_correlation


class CorrelationFilterSelector(BaseTransformer):
    def __init__(self, threshold: float = 0.85, columns: Optional[List[str]] = None, name: str = "CorrelationFilterSelector"):
        super().__init__(columns=columns, name=name)
        self.threshold = threshold
        self.to_drop_: Set[str] = set()

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CorrelationFilterSelector":
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        self.to_drop_ = set()
        n = len(target_cols)

        for i in range(n):
            col_i = target_cols[i]
            if col_i in self.to_drop_:
                continue
            for j in range(i + 1, n):
                col_j = target_cols[j]
                if col_j in self.to_drop_:
                    continue
                corr = pearson_correlation(df[col_i].values_numeric(), df[col_j].values_numeric())
                if corr is not None and abs(corr) >= self.threshold:
                    self.to_drop_.add(col_j)

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()
        for col in self.to_drop_:
            result = result.drop_column(col)
        return result
