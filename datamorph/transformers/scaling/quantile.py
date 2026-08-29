"""
DataMorph Studio - Quantile Transformer
Maps data to uniform or normal distribution using empirical quantiles.
"""

import math
from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class QuantileTransformer(BaseTransformer):
    def __init__(self, n_quantiles: int = 100, output_distribution: str = "uniform",
                 columns: Optional[List[str]] = None, name: str = "QuantileTransformer"):
        super().__init__(columns=columns, name=name)
        self.n_quantiles = n_quantiles
        self.output_distribution = output_distribution
        self.quantiles_: Dict[str, List[float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "QuantileTransformer":
        target_cols = self._resolve_columns(df)
        for col in target_cols:
            vals = sorted(df[col].values_numeric())
            if vals:
                step = len(vals) / float(self.n_quantiles)
                self.quantiles_[col] = [vals[min(int(i * step), len(vals) - 1)] for i in range(self.n_quantiles)]
            else:
                self.quantiles_[col] = [0.0] * self.n_quantiles
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            q_list = self.quantiles_.get(col, [])
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        v = float(val)
                        # calculate rank
                        rank = sum(1 for q in q_list if q <= v) / float(len(q_list))
                        if self.output_distribution == "normal":
                            # approximate probit transformation
                            rank = max(0.001, min(0.999, rank))
                            norm_val = math.sqrt(2.0) * math.erf(2.0 * rank - 1.0)
                            new_vals.append(round(norm_val, 6))
                        else:
                            new_vals.append(round(rank, 6))
                    except Exception:
                        new_vals.append(val)
            result.add_column(col, new_vals)
        return result
