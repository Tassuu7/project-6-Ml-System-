"""
DataMorph Studio - Interquartile Range (IQR) Outlier Remover / Clipper
Applies Tukey's fence rule: [Q1 - k*IQR, Q3 + k*IQR].
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class IQROutlierRemover(BaseTransformer):
    def __init__(self, factor: float = 1.5, action: str = "clip",
                 columns: Optional[List[str]] = None, name: str = "IQROutlierRemover"):
        super().__init__(columns=columns, name=name)
        self.factor = factor
        self.action = action
        self.fences_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "IQROutlierRemover":
        target_cols = self._resolve_columns(df)
        self.fences_ = {}

        for col in target_cols:
            q1 = df[col].quantile(0.25) or 0.0
            q3 = df[col].quantile(0.75) or 0.0
            iqr = q3 - q1
            self.fences_[col] = {
                "lower": q1 - self.factor * iqr,
                "upper": q3 + self.factor * iqr
            }

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            f = self.fences_.get(col, {"lower": -999999, "upper": 999999})
            if self.action == "clip":
                result.add_column(col, result[col].clip(lower=f["lower"], upper=f["upper"]))
            else:
                flags = [1 if (v is not None and (float(v) < f["lower"] or float(v) > f["upper"])) else 0
                         for v in df[col].to_list()]
                result.add_column(f"{col}_iqr_outlier", flags)

        return result
