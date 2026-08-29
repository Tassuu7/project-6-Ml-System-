"""
DataMorph Studio - Chi-Square (X2) Feature Selector
Calculates chi-square contingency scores for categorical feature selection.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class ChiSquareSelector(BaseTransformer):
    def __init__(self, target_column: str, k: int = 5,
                 columns: Optional[List[str]] = None, name: str = "ChiSquareSelector"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.k = k
        self.chi2_scores_: Dict[str, float] = {}
        self.top_features_: List[str] = []

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "ChiSquareSelector":
        feature_cols = [c for c in self._resolve_columns(df) if c != self.target_column]
        records = df.to_dict_records()
        self.chi2_scores_ = {}

        for col in feature_cols:
            contingency = {}
            for r in records:
                x_val = str(r[col])
                y_val = str(r[self.target_column])
                contingency[x_val] = contingency.get(x_val, {})
                contingency[x_val][y_val] = contingency.get(x_val, {}).get(y_val, 0) + 1

            chi2 = 0.0
            total_n = len(records) or 1
            for x_val, y_map in contingency.items():
                row_sum = sum(y_map.values())
                for y_val, obs in y_map.items():
                    col_sum = sum(contingency[other_x].get(y_val, 0) for other_x in contingency)
                    exp = (row_sum * col_sum) / float(total_n)
                    if exp > 0:
                        chi2 += ((obs - exp) ** 2) / exp
            self.chi2_scores_[col] = round(chi2, 4)

        sorted_feats = sorted(self.chi2_scores_.keys(), key=lambda c: self.chi2_scores_[c], reverse=True)
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
