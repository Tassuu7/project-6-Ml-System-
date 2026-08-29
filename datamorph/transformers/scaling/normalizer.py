"""
DataMorph Studio - Vector Normalizer
Normalizes row sample vectors individually to unit norm (L1, L2, or max).
"""

import math
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class VectorNormalizer(BaseTransformer):
    def __init__(self, norm: str = "l2", columns: Optional[List[str]] = None, name: str = "VectorNormalizer"):
        super().__init__(columns=columns, name=name)
        self.norm = norm.lower()

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "VectorNormalizer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()
        records = result.to_dict_records()

        for row in records:
            vals = []
            for col in target_cols:
                try:
                    vals.append(float(row[col]) if row[col] is not None else 0.0)
                except Exception:
                    vals.append(0.0)
            
            if self.norm == "l1":
                denom = sum(abs(x) for x in vals) or 1.0
            elif self.norm == "max":
                denom = max(abs(x) for x in vals) or 1.0
            else:  # L2
                denom = math.sqrt(sum(x ** 2 for x in vals)) or 1.0
            
            for idx, col in enumerate(target_cols):
                row[col] = round(vals[idx] / denom, 6)

        for col in target_cols:
            result.add_column(col, [r[col] for r in records])

        return result
