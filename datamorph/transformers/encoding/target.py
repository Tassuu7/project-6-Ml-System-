"""
DataMorph Studio - Target (Mean) Encoder
Encodes categorical values based on target mean with empirical Bayes smoothing.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.core.exceptions import TransformerError


class TargetEncoder(BaseTransformer):
    def __init__(self, target_column: str, smoothing: float = 10.0,
                 columns: Optional[List[str]] = None, name: str = "TargetEncoder"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.smoothing = smoothing
        self.global_mean_: float = 0.0
        self.encoding_map_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TargetEncoder":
        if self.target_column not in df.columns:
            raise TransformerError(f"Target column '{self.target_column}' not found in DataFrame", transformer_name=self.name)

        target_vals = df[self.target_column].values_numeric()
        self.global_mean_ = sum(target_vals) / len(target_vals) if target_vals else 0.0
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        self.encoding_map_ = {}

        records = df.to_dict_records()
        for col in feature_cols:
            cat_target_sums: Dict[str, float] = {}
            cat_counts: Dict[str, int] = {}
            for r in records:
                cat = str(r[col]) if r[col] is not None else "null"
                try:
                    t_val = float(r[self.target_column])
                    cat_target_sums[cat] = cat_target_sums.get(cat, 0.0) + t_val
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
                except Exception:
                    pass

            enc_map = {}
            for cat, count in cat_counts.items():
                cat_mean = cat_target_sums[cat] / count
                # Empirical Bayes smoothed target encoding
                smoothed_val = (count * cat_mean + self.smoothing * self.global_mean_) / (count + self.smoothing)
                enc_map[cat] = round(smoothed_val, 6)
            self.encoding_map_[col] = enc_map

        self.is_fitted = True
        self._fitted_params = {"global_mean": self.global_mean_, "encoding_map": self.encoding_map_}
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        result = df.copy()

        for col in feature_cols:
            enc_map = self.encoding_map_.get(col, {})
            new_vals = [
                enc_map.get(str(v) if v is not None else "null", self.global_mean_)
                for v in df[col].to_list()
            ]
            result.add_column(col, new_vals)

        return result
