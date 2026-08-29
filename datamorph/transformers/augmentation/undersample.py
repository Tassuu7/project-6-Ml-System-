"""
DataMorph Studio - Random Majority Under-Sampler
Balances class distribution by randomly down-sampling majority target classes.
"""

import random
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class RandomUnderSampler(BaseTransformer):
    def __init__(self, target_column: str, sampling_ratio: float = 1.0,
                 columns: Optional[List[str]] = None, name: str = "RandomUnderSampler"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.sampling_ratio = sampling_ratio

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "RandomUnderSampler":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        records = df.to_dict_records()
        if not records or self.target_column not in df.columns:
            return df.copy()

        classes = {}
        for r in records:
            y = str(r[self.target_column])
            classes.setdefault(y, []).append(r)

        min_len = min(len(rows) for rows in classes.values())
        target_len = int(min_len / self.sampling_ratio)

        sampled = []
        for y, rows in classes.items():
            if len(rows) > target_len:
                sampled.extend(random.sample(rows, target_len))
            else:
                sampled.extend(rows)

        random.shuffle(sampled)
        return DataFrame(sampled)
