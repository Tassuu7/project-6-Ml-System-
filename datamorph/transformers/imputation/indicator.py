"""
DataMorph Studio - Missing Indicator Transformer
Creates binary indicator columns marking the presence of missing values.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class MissingIndicator(BaseTransformer):
    def __init__(self, prefix: str = "missing_", columns: Optional[List[str]] = None, name: str = "MissingIndicator"):
        super().__init__(columns=columns, name=name)
        self.prefix = prefix

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MissingIndicator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            missing_flags = [1 if x else 0 for x in df[col].is_null()]
            indicator_col = f"{self.prefix}{col}"
            result.add_column(indicator_col, missing_flags)

        return result
