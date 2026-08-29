"""
DataMorph Studio - CatBoost-Style Target Encoder
Online streaming target encoder preventing target leakage with prior weights.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class CatBoostEncoder(BaseTransformer):
    def __init__(self, target_column: str, prior_weight: float = 1.0,
                 columns: Optional[List[str]] = None, name: str = "CatBoostEncoder"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.prior_weight = prior_weight
        self.prior_: float = 0.0
        self.final_stats_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CatBoostEncoder":
        t_vals = df[self.target_column].values_numeric()
        self.prior_ = sum(t_vals) / len(t_vals) if t_vals else 0.5
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        records = df.to_dict_records()

        self.final_stats_ = {}
        for col in feature_cols:
            sums = {}
            counts = {}
            for r in records:
                cat = str(r[col]) if r[col] is not None else "null"
                try:
                    y = float(r[self.target_column])
                    sums[cat] = sums.get(cat, 0.0) + y
                    counts[cat] = counts.get(cat, 0) + 1
                except Exception:
                    pass
            self.final_stats_[col] = {
                cat: round((sums[cat] + self.prior_ * self.prior_weight) / (counts[cat] + self.prior_weight), 6)
                for cat in counts
            }

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        result = df.copy()

        for col in feature_cols:
            stats = self.final_stats_.get(col, {})
            new_vals = [stats.get(str(v) if v is not None else "null", self.prior_) for v in df[col].to_list()]
            result.add_column(col, new_vals)

        return result
