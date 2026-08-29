"""
DataMorph Studio - MinMax Scaler
Transforms features by scaling each feature to a given range [feature_range]: (x - min) / (max - min).
"""

from typing import List, Optional, Dict, Any, Tuple
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class MinMaxScaler(BaseTransformer):
    def __init__(self, feature_range: Tuple[float, float] = (0.0, 1.0),
                 columns: Optional[List[str]] = None, name: str = "MinMaxScaler"):
        super().__init__(columns=columns, name=name)
        self.feature_range = feature_range
        self.data_min_: Dict[str, float] = {}
        self.data_max_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MinMaxScaler":
        target_cols = self._resolve_columns(df)
        self.data_min_ = {}
        self.data_max_ = {}

        for col in target_cols:
            c_min = df[col].min()
            c_max = df[col].max()
            self.data_min_[col] = c_min if c_min is not None else 0.0
            self.data_max_[col] = c_max if c_max is not None else 1.0

        self._fitted_params = {"data_min": self.data_min_, "data_max": self.data_max_}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()
        low, high = self.feature_range

        for col in target_cols:
            c_min = self.data_min_.get(col, 0.0)
            c_max = self.data_max_.get(col, 1.0)
            diff = (c_max - c_min) if (c_max - c_min) != 0.0 else 1.0
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        v = float(val)
                        scaled = ((v - c_min) / diff) * (high - low) + low
                        new_vals.append(round(scaled, 6))
                    except (ValueError, TypeError):
                        new_vals.append(val)
            result.add_column(col, new_vals)

        return result
