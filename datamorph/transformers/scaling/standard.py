"""
DataMorph Studio - Standard Scaler (Z-Score Normalization)
Transforms features by removing the mean and scaling to unit variance: z = (x - u) / s.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class StandardScaler(BaseTransformer):
    def __init__(self, with_mean: bool = True, with_std: bool = True,
                 columns: Optional[List[str]] = None, name: str = "StandardScaler"):
        super().__init__(columns=columns, name=name)
        self.with_mean = with_mean
        self.with_std = with_std
        self.means_: Dict[str, float] = {}
        self.stds_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "StandardScaler":
        target_cols = self._resolve_columns(df)
        self.means_ = {}
        self.stds_ = {}

        for col in target_cols:
            m = df[col].mean()
            s = df[col].std()
            self.means_[col] = m if m is not None else 0.0
            self.stds_[col] = s if s is not None and s > 0.0 else 1.0

        self._fitted_params = {"means": self.means_, "stds": self.stds_}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            m = self.means_.get(col, 0.0) if self.with_mean else 0.0
            s = self.stds_.get(col, 1.0) if self.with_std else 1.0
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        v = float(val)
                        new_vals.append(round((v - m) / s, 6))
                    except (ValueError, TypeError):
                        new_vals.append(val)
            result.add_column(col, new_vals)

        return result
