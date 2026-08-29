"""
DataMorph Studio - Symbolic Non-Linear Feature Synthesizer
Generates non-linear transformations: log1p, sqrt, reciprocal, sigmoid, tanh, softplus.
"""

import math
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class SymbolicFeatureSynthesizer(BaseTransformer):
    def __init__(self, functions: List[str] = ["log1p", "sqrt", "reciprocal", "sigmoid"],
                 columns: Optional[List[str]] = None, name: str = "SymbolicFeatureSynthesizer"):
        super().__init__(columns=columns, name=name)
        self.functions = functions

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SymbolicFeatureSynthesizer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()

        for col in target_cols:
            raw = df[col].to_list()
            for fn in self.functions:
                feat_name = f"{col}_{fn}"
                new_vals = []
                for v in raw:
                    if v is None or v == "":
                        new_vals.append(None)
                        continue
                    try:
                        x = float(v)
                        if fn == "log1p":
                            val = math.log(max(1e-12, x + 1.0)) if x >= -1.0 else None
                        elif fn == "sqrt":
                            val = math.sqrt(x) if x >= 0 else None
                        elif fn == "reciprocal":
                            val = (1.0 / x) if x != 0 else None
                        elif fn == "sigmoid":
                            val = 1.0 / (1.0 + math.exp(-min(50.0, max(-50.0, x))))
                        elif fn == "tanh":
                            val = math.tanh(min(50.0, max(-50.0, x)))
                        else:
                            val = x
                        new_vals.append(round(val, 6) if val is not None else None)
                    except Exception:
                        new_vals.append(None)
                result.add_column(feat_name, new_vals)

        return result
