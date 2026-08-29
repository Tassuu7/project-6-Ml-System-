"""
DataMorph Studio - Pairwise Feature Ratio & Difference Synthesizer
Generates financial and scientific ratio features x_i / (x_j + eps) and relative percentage diffs.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class FeatureRatioGenerator(BaseTransformer):
    def __init__(self, epsilon: float = 1e-6, columns: Optional[List[str]] = None,
                 name: str = "FeatureRatioGenerator"):
        super().__init__(columns=columns, name=name)
        self.epsilon = epsilon

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "FeatureRatioGenerator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()
        n = len(target_cols)

        for i in range(n):
            for j in range(i + 1, n):
                c1, c2 = target_cols[i], target_cols[j]
                ratio_name = f"ratio_{c1}_div_{c2}"
                ratios = []
                for v1, v2 in zip(df[c1].to_list(), df[c2].to_list()):
                    try:
                        f1, f2 = float(v1), float(v2)
                        ratios.append(round(f1 / (f2 + self.epsilon), 6))
                    except Exception:
                        ratios.append(None)
                result.add_column(ratio_name, ratios)

        return result
