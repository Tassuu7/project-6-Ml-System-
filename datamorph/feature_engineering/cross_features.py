"""
DataMorph Studio - Categorical Cross-Product Feature Synthesizer
Generates Cartesian cross-product combinations across multiple categorical dimensions.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class CategoricalCrossProductGenerator(BaseTransformer):
    def __init__(self, separator: str = "__X__", columns: Optional[List[str]] = None,
                 name: str = "CategoricalCrossProductGenerator"):
        super().__init__(columns=columns, name=name)
        self.separator = separator

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CategoricalCrossProductGenerator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()
        n = len(target_cols)

        for i in range(n):
            col_i = target_cols[i]
            for j in range(i + 1, n):
                col_j = target_cols[j]
                cross_name = f"{col_i}{self.separator}{col_j}"
                crossed_vals = [
                    f"{a}{self.separator}{b}" if a is not None and b is not None else None
                    for a, b in zip(df[col_i].to_list(), df[col_j].to_list())
                ]
                result.add_column(cross_name, crossed_vals)

        return result
