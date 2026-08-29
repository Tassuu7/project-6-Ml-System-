"""
DataMorph Studio - Equal-Width Continuous Discretizer
Divides continuous numerical range into k equal-width discrete intervals.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class EqualWidthDiscretizer(BaseTransformer):
    def __init__(self, n_bins: int = 5, labels: Optional[List[str]] = None,
                 columns: Optional[List[str]] = None, name: str = "EqualWidthDiscretizer"):
        super().__init__(columns=columns, name=name)
        self.n_bins = max(2, n_bins)
        self.labels = labels
        self.bin_edges_: Dict[str, List[float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "EqualWidthDiscretizer":
        target_cols = self._resolve_columns(df)
        self.bin_edges_ = {}

        for col in target_cols:
            c_min = df[col].min() or 0.0
            c_max = df[col].max() or 1.0
            width = (c_max - c_min) / float(self.n_bins)
            edges = [c_min + i * width for i in range(self.n_bins + 1)]
            self.bin_edges_[col] = edges

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            edges = self.bin_edges_.get(col, [])
            binned = []
            for v in df[col].to_list():
                if v is None or v == "":
                    binned.append(None)
                    continue
                try:
                    val = float(v)
                    assigned_bin = self.n_bins - 1
                    for idx in range(len(edges) - 1):
                        if edges[idx] <= val < edges[idx + 1]:
                            assigned_bin = idx
                            break
                    if self.labels and assigned_bin < len(self.labels):
                        binned.append(self.labels[assigned_bin])
                    else:
                        binned.append(f"bin_{assigned_bin}")
                except Exception:
                    binned.append(None)
            result.add_column(f"{col}_binned", binned)

        return result
