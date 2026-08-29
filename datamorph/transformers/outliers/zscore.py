"""
DataMorph Studio - Z-Score Outlier Detector
Flags or remediates samples beyond threshold standard deviations from the mean.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class ZScoreOutlierDetector(BaseTransformer):
    def __init__(self, threshold: float = 3.0, action: str = "clip",
                 columns: Optional[List[str]] = None, name: str = "ZScoreOutlierDetector"):
        super().__init__(columns=columns, name=name)
        self.threshold = threshold
        self.action = action  # "clip", "flag", "nan"
        self.bounds_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "ZScoreOutlierDetector":
        target_cols = self._resolve_columns(df)
        self.bounds_ = {}

        for col in target_cols:
            m = df[col].mean() or 0.0
            s = df[col].std() or 1.0
            self.bounds_[col] = {
                "lower": m - self.threshold * s,
                "upper": m + self.threshold * s,
                "mean": m,
                "std": s
            }

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            b = self.bounds_.get(col, {"lower": -999999, "upper": 999999})
            if self.action == "clip":
                result.add_column(col, result[col].clip(lower=b["lower"], upper=b["upper"]))
            elif self.action == "flag":
                flags = []
                for v in df[col].to_list():
                    try:
                        fv = float(v)
                        flags.append(1 if (fv < b["lower"] or fv > b["upper"]) else 0)
                    except Exception:
                        flags.append(0)
                result.add_column(f"{col}_outlier", flags)
            elif self.action == "nan":
                new_vals = []
                for v in df[col].to_list():
                    try:
                        fv = float(v)
                        new_vals.append(None if (fv < b["lower"] or fv > b["upper"]) else v)
                    except Exception:
                        new_vals.append(v)
                result.add_column(col, new_vals)

        return result
