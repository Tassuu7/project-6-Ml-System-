"""
DataMorph Studio - Equal-Frequency (Quantile) Discretizer
Divides continuous numerical feature into bins with approximately equal sample count.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class EqualFrequencyDiscretizer(BaseTransformer):
    def __init__(self, n_bins: int = 5, columns: Optional[List[str]] = None, name: str = "EqualFrequencyDiscretizer"):
        super().__init__(columns=columns, name=name)
        self.n_bins = max(2, n_bins)
        self.quantiles_: Dict[str, List[float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "EqualFrequencyDiscretizer":
        target_cols = self._resolve_columns(df)
        self.quantiles_ = {}

        for col in target_cols:
            q_edges = []
            for i in range(self.n_bins + 1):
                q = i / float(self.n_bins)
                q_val = df[col].quantile(q)
                q_edges.append(q_val if q_val is not None else 0.0)
            self.quantiles_[col] = q_edges

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            edges = self.quantiles_.get(col, [])
            binned = []
            for v in df[col].to_list():
                if v is None or v == "":
                    binned.append(None)
                    continue
                try:
                    val = float(v)
                    b = self.n_bins - 1
                    for idx in range(len(edges) - 1):
                        if edges[idx] <= val <= edges[idx + 1]:
                            b = idx
                            break
                    binned.append(f"qbin_{b}")
                except Exception:
                    binned.append(None)
            result.add_column(f"{col}_qbin", binned)

        return result
