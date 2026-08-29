"""
DataMorph Studio - Mixup Feature Augmentation
Constructs convex combinations of random pairs of training records: x = a*x1 + (1-a)*x2.
"""

import random
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class MixupAugmenter(BaseTransformer):
    def __init__(self, alpha: float = 0.2, n_synthetic: int = 100,
                 columns: Optional[List[str]] = None, name: str = "MixupAugmenter"):
        super().__init__(columns=columns, name=name)
        self.alpha = alpha
        self.n_synthetic = n_synthetic

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "MixupAugmenter":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        records = df.to_dict_records()
        if len(records) < 2:
            return df.copy()

        num_cols = df.numeric_columns()
        synthetic = []

        for _ in range(min(len(records), self.n_synthetic)):
            r1 = random.choice(records)
            r2 = random.choice(records)
            lam = random.betavariate(self.alpha, self.alpha) if self.alpha > 0 else 0.5

            mixed = dict(r1)
            for col in num_cols:
                try:
                    v1 = float(r1[col])
                    v2 = float(r2[col])
                    mixed[col] = round(lam * v1 + (1.0 - lam) * v2, 4)
                except Exception:
                    pass
            synthetic.append(mixed)

        return DataFrame(records + synthetic)
