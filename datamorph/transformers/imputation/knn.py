"""
DataMorph Studio - K-Nearest Neighbors (KNN) Imputation Transformer
Estimates missing feature values based on Euclidean distance across feature space.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import euclidean_distance, mean


class KNNImputer(BaseTransformer):
    def __init__(self, n_neighbors: int = 5, columns: Optional[List[str]] = None, name: str = "KNNImputer"):
        super().__init__(columns=columns, name=name)
        self.n_neighbors = max(1, n_neighbors)
        self.train_matrix_: List[List[float]] = []
        self.col_means_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "KNNImputer":
        target_cols = self._resolve_columns(df)
        self.col_means_ = {col: df[col].mean() or 0.0 for col in target_cols}
        
        matrix = []
        for i in range(len(df)):
            row = []
            has_missing = False
            for col in target_cols:
                val = df[col][i]
                if val is None or val == "":
                    has_missing = True
                    break
                try:
                    row.append(float(val))
                except (ValueError, TypeError):
                    has_missing = True
                    break
            if not has_missing:
                matrix.append(row)
        
        self.train_matrix_ = matrix[:1000]  # Cap reference matrix for performance
        self._fitted_params = {"n_neighbors": self.n_neighbors, "train_rows": len(self.train_matrix_)}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        if not self.train_matrix_:
            for col in target_cols:
                result.add_column(col, result[col].fillna(self.col_means_.get(col, 0.0)))
            return result

        records = result.to_dict_records()
        for i, row in enumerate(records):
            for col_idx, col in enumerate(target_cols):
                val = row.get(col)
                if val is None or val == "":
                    # Find k-nearest complete records
                    distances = []
                    for ref_row in self.train_matrix_:
                        # calculate distance on known attributes
                        dist = 0.0
                        known_count = 0
                        for other_idx, other_col in enumerate(target_cols):
                            if other_col != col and row.get(other_col) is not None:
                                try:
                                    v = float(row[other_col])
                                    dist += (v - ref_row[other_idx]) ** 2
                                    known_count += 1
                                except Exception:
                                    pass
                        if known_count > 0:
                            distances.append((dist, ref_row[col_idx]))
                    
                    if distances:
                        distances.sort(key=lambda x: x[0])
                        k_nearest = [val for dist, val in distances[:self.n_neighbors]]
                        imputed_val = mean(k_nearest)
                        row[col] = imputed_val
                    else:
                        row[col] = self.col_means_.get(col, 0.0)

        for col in target_cols:
            result.add_column(col, [r[col] for r in records])
        return result
