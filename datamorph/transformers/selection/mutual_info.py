"""
DataMorph Studio - Mutual Information Feature Selector
Ranks and selects top K features based on entropy and mutual information with target.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import entropy


class MutualInformationSelector(BaseTransformer):
    def __init__(self, target_column: str, k: int = 10,
                 columns: Optional[List[str]] = None, name: str = "MutualInformationSelector"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.k = k
        self.scores_: Dict[str, float] = {}
        self.top_features_: List[str] = []

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MutualInformationSelector":
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        target_vals = df[self.target_column].to_list()
        h_y = entropy(target_vals)
        self.scores_ = {}

        for col in feature_cols:
            col_vals = df[col].to_list()
            h_x = entropy(col_vals)
            # Joint entropy
            joint_pairs = [f"{col_vals[i]}_{target_vals[i]}" for i in range(len(col_vals))]
            h_xy = entropy(joint_pairs)
            mi = max(0.0, h_x + h_y - h_xy)
            self.scores_[col] = round(mi, 4)

        sorted_feats = sorted(self.scores_.keys(), key=lambda c: self.scores_[c], reverse=True)
        self.top_features_ = sorted_feats[:self.k]
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = DataFrame()
        for col in self.top_features_:
            if col in df.columns:
                result.add_column(col, df[col].to_list())
        if self.target_column in df.columns:
            result.add_column(self.target_column, df[self.target_column].to_list())
        return result
