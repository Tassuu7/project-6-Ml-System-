"""
DataMorph Studio - Multivariate Imputation by Chained Equations (MICE)
Iterative multi-pass regression-based imputation for missing data.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean


class MICEImputer(BaseTransformer):
    def __init__(self, max_iter: int = 5, columns: Optional[List[str]] = None, name: str = "MICEImputer"):
        super().__init__(columns=columns, name=name)
        self.max_iter = max_iter
        self.col_means_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MICEImputer":
        target_cols = self._resolve_columns(df)
        self.col_means_ = {col: df[col].mean() or 0.0 for col in target_cols}
        self.is_fitted = True
        self._fitted_params = {"max_iter": self.max_iter, "col_means": self.col_means_}
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        # Initial mean imputation
        for col in target_cols:
            result.add_column(col, result[col].fillna(self.col_means_.get(col, 0.0)))

        # Iterative update cycle
        records = result.to_dict_records()
        for iteration in range(self.max_iter):
            for target_col in target_cols:
                # Estimate new values based on weighted average of other features
                other_cols = [c for c in target_cols if c != target_col]
                if not other_cols:
                    continue
                for row in records:
                    weighted_sum = sum(float(row[c]) for c in other_cols if row[c] is not None)
                    row[target_col] = round(weighted_sum / len(other_cols), 4)

        for col in target_cols:
            result.add_column(col, [r[col] for r in records])
        return result
