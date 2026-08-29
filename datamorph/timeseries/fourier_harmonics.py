"""
DataMorph Studio - Fourier Terms Harmonic Feature Synthesizer
Generates multi-frequency Sine and Cosine harmonic pairs for seasonal time series.
"""

import math
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class FourierHarmonicsGenerator(BaseTransformer):
    def __init__(self, periods: List[float] = [7.0, 30.4, 365.25], n_harmonics: int = 2,
                 columns: Optional[List[str]] = None, name: str = "FourierHarmonicsGenerator"):
        super().__init__(columns=columns, name=name)
        self.periods = periods
        self.n_harmonics = n_harmonics

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "FourierHarmonicsGenerator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()
        n = len(df)

        for period in self.periods:
            for k in range(1, self.n_harmonics + 1):
                sin_vals = []
                cos_vals = []
                for t in range(n):
                    angle = 2.0 * math.pi * k * t / float(period)
                    sin_vals.append(round(math.sin(angle), 6))
                    cos_vals.append(round(math.cos(angle), 6))
                result.add_column(f"fourier_sin_p{int(period)}_k{k}", sin_vals)
                result.add_column(f"fourier_cos_p{int(period)}_k{k}", cos_vals)

        return result
