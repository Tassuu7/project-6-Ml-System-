"""
DataMorph Studio - Frequency (Count) Encoder
Replaces categorical values with their frequency or normalized count in the dataset.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class FrequencyEncoder(BaseTransformer):
    def __init__(self, normalize: bool = True, columns: Optional[List[str]] = None, name: str = "FrequencyEncoder"):
        super().__init__(columns=columns, name=name)
        self.normalize = normalize
        self.freq_maps_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "FrequencyEncoder":
        target_cols = self._resolve_columns(df)
        total_rows = len(df) or 1
        self.freq_maps_ = {}

        for col in target_cols:
            counts = df[col].value_counts()
            if self.normalize:
                self.freq_maps_[col] = {cat: round(cnt / total_rows, 6) for cat, cnt in counts.items()}
            else:
                self.freq_maps_[col] = {cat: float(cnt) for cat, cnt in counts.items()}

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            f_map = self.freq_maps_.get(col, {})
            new_vals = [f_map.get(str(v) if v is not None else "null", 0.0) for v in df[col].to_list()]
            result.add_column(col, new_vals)

        return result
