"""
DataMorph Studio - Binary Encoder
Encodes high-cardinality categorical features into binary digits.
"""

import math
from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class BinaryEncoder(BaseTransformer):
    def __init__(self, columns: Optional[List[str]] = None, name: str = "BinaryEncoder"):
        super().__init__(columns=columns, name=name)
        self.mappings_: Dict[str, Dict[str, str]] = {}
        self.digits_count_: Dict[str, int] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "BinaryEncoder":
        target_cols = self._resolve_columns(df)
        self.mappings_ = {}
        self.digits_count_ = {}

        for col in target_cols:
            cats = df[col].unique_values()
            n_cats = len(cats)
            n_digits = max(1, math.ceil(math.log2(n_cats + 1)))
            self.digits_count_[col] = n_digits

            cat_map = {}
            for idx, cat in enumerate(cats, start=1):
                bin_str = bin(idx)[2:].zfill(n_digits)
                cat_map[str(cat)] = bin_str
            self.mappings_[col] = cat_map

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cat_map = self.mappings_.get(col, {})
            n_digits = self.digits_count_.get(col, 1)
            zeros = "0" * n_digits
            
            raw_vals = [cat_map.get(str(v) if v is not None else "null", zeros) for v in df[col].to_list()]
            for bit_idx in range(n_digits):
                bit_col_name = f"{col}_bin_{bit_idx}"
                bits = [int(s[bit_idx]) for s in raw_vals]
                result.add_column(bit_col_name, bits)
            result = result.drop_column(col)

        return result
