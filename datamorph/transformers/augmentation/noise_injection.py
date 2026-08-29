"""
DataMorph Studio - Gaussian Noise Injection Transformer
Injects controllable normal noise into continuous features for model regularization.
"""

import random
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class GaussianNoiseInjector(BaseTransformer):
    def __init__(self, noise_std: float = 0.05, columns: Optional[List[str]] = None, name: str = "GaussianNoiseInjector"):
        super().__init__(columns=columns, name=name)
        self.noise_std = noise_std

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "GaussianNoiseInjector":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()

        for col in target_cols:
            s = df[col].std() or 1.0
            scale = self.noise_std * s
            new_vals = []
            for v in df[col].to_list():
                if v is None or v == "":
                    new_vals.append(None)
                else:
                    try:
                        noise = random.gauss(0.0, scale)
                        new_vals.append(round(float(v) + noise, 6))
                    except Exception:
                        new_vals.append(v)
            result.add_column(col, new_vals)

        return result
