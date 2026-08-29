"""
DataMorph Studio - Synthetic Minority Over-sampling Technique (SMOTE)
Synthesizes new instances along feature line segments between minority neighbors.
"""

import random
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class SyntheticMinorityOverSampler(BaseTransformer):
    def __init__(self, target_column: str, sampling_ratio: float = 1.0, k_neighbors: int = 5,
                 columns: Optional[List[str]] = None, name: str = "SyntheticMinorityOverSampler"):
        super().__init__(columns=columns, name=name)
        self.target_column = target_column
        self.sampling_ratio = sampling_ratio
        self.k_neighbors = k_neighbors

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SyntheticMinorityOverSampler":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        records = df.to_dict_records()
        if not records or self.target_column not in df.columns:
            return df.copy()

        # Identify minority class
        target_counts = df[self.target_column].value_counts()
        if len(target_counts) < 2:
            return df.copy()

        minority_class = min(target_counts, key=target_counts.get)
        majority_count = max(target_counts.values())
        minority_records = [r for r in records if str(r[self.target_column]) == str(minority_class)]

        target_synth = int(majority_count * self.sampling_ratio) - len(minority_records)
        target_synth = max(0, min(1000, target_synth))

        synthetic_rows = []
        numeric_cols = df.numeric_columns()

        for _ in range(target_synth):
            base_row = random.choice(minority_records)
            neighbor_row = random.choice(minority_records)
            diff_ratio = random.random()

            new_row = dict(base_row)
            for col in numeric_cols:
                try:
                    v1 = float(base_row[col])
                    v2 = float(neighbor_row[col])
                    new_row[col] = round(v1 + diff_ratio * (v2 - v1), 4)
                except Exception:
                    pass
            synthetic_rows.append(new_row)

        all_records = records + synthetic_rows
        return DataFrame(all_records)
