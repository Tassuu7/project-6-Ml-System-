"""
DataMorph Studio - Weight of Evidence (WoE) & Information Value (IV) Encoder
Credit risk & binary classification feature engineering transformer.
"""

import math
from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.core.exceptions import TransformerError


class WeightOfEvidenceEncoder(BaseTransformer):
    def __init__(self, target_column: str, columns: Optional[List[str]] = None, name: str = "WeightOfEvidenceEncoder"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.woe_map_: Dict[str, Dict[str, float]] = {}
        self.iv_scores_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "WeightOfEvidenceEncoder":
        if self.target_column not in df.columns:
            raise TransformerError(f"Target column '{self.target_column}' missing", transformer_name=self.name)

        target_vals = df[self.target_column].to_list()
        total_pos = sum(1 for y in target_vals if y in (1, "1", 1.0, "true", "True", True))
        total_neg = len(target_vals) - total_pos
        total_pos = max(1, total_pos)
        total_neg = max(1, total_neg)

        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        self.woe_map_ = {}
        self.iv_scores_ = {}
        records = df.to_dict_records()

        for col in feature_cols:
            cat_pos = {}
            cat_neg = {}
            for r in records:
                cat = str(r[col]) if r[col] is not None else "null"
                y = r[self.target_column]
                is_pos = (y in (1, "1", 1.0, "true", "True", True))
                if is_pos:
                    cat_pos[cat] = cat_pos.get(cat, 0) + 1
                else:
                    cat_neg[cat] = cat_neg.get(cat, 0) + 1

            all_cats = set(cat_pos.keys()).union(set(cat_neg.keys()))
            col_woe = {}
            col_iv = 0.0

            for cat in all_cats:
                pos = cat_pos.get(cat, 0.5)
                neg = cat_neg.get(cat, 0.5)
                dist_pos = pos / total_pos
                dist_neg = neg / total_neg
                woe = math.log(max(1e-6, dist_pos) / max(1e-6, dist_neg))
                col_woe[cat] = round(woe, 4)
                col_iv += (dist_pos - dist_neg) * woe

            self.woe_map_[col] = col_woe
            self.iv_scores_[col] = round(col_iv, 4)

        self.is_fitted = True
        self._fitted_params = {"woe_map": self.woe_map_, "iv_scores": self.iv_scores_}
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        result = df.copy()

        for col in feature_cols:
            woe_dict = self.woe_map_.get(col, {})
            new_vals = [woe_dict.get(str(v) if v is not None else "null", 0.0) for v in df[col].to_list()]
            result.add_column(col, new_vals)

        return result
