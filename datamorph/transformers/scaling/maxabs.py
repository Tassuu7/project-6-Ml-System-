"""
DataMorph Studio - MaxAbs Scaler
Scale each feature by its maximum absolute value without destroying sparsity.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class MaxAbsScaler(BaseTransformer):
    def __init__(self, columns: Optional[List[str]] = None, name: str = "MaxAbsScaler"):
        super().__init__(columns=columns, name=name)
        self.max_abs_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MaxAbsScaler":
        target_cols = self._resolve_columns(df)
        for col in target_cols:
            vals = df[col].values_numeric()
            if vals:
                max_val = max(abs(x) for x in vals)
                self.max_abs_[col] = max_val if max_val > 0.0 else 1.0
            else:
                self.max_abs_[col] = 1.0
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            denom = self.max_abs_.get(col, 1.0)
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        v = float(val)
                        new_vals.append(round(v / denom, 6))
                    except (ValueError, TypeError):
                        new_vals.append(val)
            result.add_column(col, new_vals)

        return result
