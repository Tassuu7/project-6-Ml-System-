"""
DataMorph Studio - Ordinal Encoder
Encodes categorical features into ordered numeric integers (0 to k-1).
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class OrdinalEncoder(BaseTransformer):
    def __init__(self, mapping: Optional[Dict[str, Dict[str, int]]] = None,
                 handle_unknown: int = -1, columns: Optional[List[str]] = None, name: str = "OrdinalEncoder"):
        super().__init__(columns=columns, name=name)
        self.mapping = mapping or {}
        self.handle_unknown = handle_unknown
        self.categories_map_: Dict[str, Dict[str, int]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "OrdinalEncoder":
        target_cols = self._resolve_columns(df)
        self.categories_map_ = {}

        for col in target_cols:
            if col in self.mapping:
                self.categories_map_[col] = self.mapping[col]
            else:
                unique_cats = df[col].unique_values()
                self.categories_map_[col] = {str(cat): idx for idx, cat in enumerate(unique_cats)}

        self._fitted_params = {"mapping": self.categories_map_}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cat_map = self.categories_map_.get(col, {})
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(self.handle_unknown)
                else:
                    new_vals.append(cat_map.get(str(val), self.handle_unknown))
            result.add_column(col, new_vals)

        return result
