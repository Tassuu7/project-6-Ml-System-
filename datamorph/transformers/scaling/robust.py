"""
DataMorph Studio - Robust Scaler
Scale features using statistics that are robust to outliers (median and IQR).
"""

from typing import List, Optional, Dict, Any, Tuple
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class RobustScaler(BaseTransformer):
    def __init__(self, quantile_range: Tuple[float, float] = (25.0, 75.0),
                 columns: Optional[List[str]] = None, name: str = "RobustScaler"):
        super().__init__(columns=columns, name=name)
        self.quantile_range = quantile_range
        self.center_: Dict[str, float] = {}
        self.scale_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "RobustScaler":
        target_cols = self._resolve_columns(df)
        q_low, q_high = self.quantile_range[0] / 100.0, self.quantile_range[1] / 100.0

        for col in target_cols:
            med = df[col].median()
            q1 = df[col].quantile(q_low)
            q3 = df[col].quantile(q_high)
            iqr = (q3 - q1) if (q3 is not None and q1 is not None and (q3 - q1) > 0.0) else 1.0
            self.center_[col] = med if med is not None else 0.0
            self.scale_[col] = iqr

        self.is_fitted = True
        self._fitted_params = {"center": self.center_, "scale": self.scale_}
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            med = self.center_.get(col, 0.0)
            scale = self.scale_.get(col, 1.0)
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        v = float(val)
                        new_vals.append(round((v - med) / scale, 6))
                    except (ValueError, TypeError):
                        new_vals.append(val)
            result.add_column(col, new_vals)

        return result
