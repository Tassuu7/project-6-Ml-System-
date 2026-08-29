"""
DataMorph Studio - Custom Edge Bin Discretizer
Applies user-defined manual cut points and category labels.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class CustomBinDiscretizer(BaseTransformer):
    def __init__(self, cuts: Dict[str, List[float]], labels: Optional[Dict[str, List[str]]] = None,
                 columns: Optional[List[str]] = None, name: str = "CustomBinDiscretizer"):
        super().__init__(columns=columns, name=name)
        self.cuts = cuts
        self.labels = labels or {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CustomBinDiscretizer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            if col not in self.cuts:
                continue
            edges = sorted(self.cuts[col])
            col_labels = self.labels.get(col, [f"bin_{i}" for i in range(len(edges) - 1)])
            binned = []
            for v in df[col].to_list():
                if v is None or v == "":
                    binned.append(None)
                else:
                    try:
                        val = float(v)
                        bin_idx = len(col_labels) - 1
                        for i in range(len(edges) - 1):
                            if edges[i] <= val < edges[i + 1]:
                                bin_idx = i
                                break
                        binned.append(col_labels[min(bin_idx, len(col_labels) - 1)])
                    except Exception:
                        binned.append(None)
            result.add_column(f"{col}_custom_bin", binned)

        return result
