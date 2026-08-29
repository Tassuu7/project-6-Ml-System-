"""
DataMorph Studio - One-Hot Encoder
Encodes categorical features as a one-hot numeric array with handle_unknown options.
"""

from typing import List, Optional, Dict, Set, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class OneHotEncoder(BaseTransformer):
    def __init__(self, drop_first: bool = False, max_categories: int = 50,
                 prefix_sep: str = "_", columns: Optional[List[str]] = None, name: str = "OneHotEncoder"):
        super().__init__(columns=columns, name=name)
        self.drop_first = drop_first
        self.max_categories = max_categories
        self.prefix_sep = prefix_sep
        self.categories_: Dict[str, List[str]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "OneHotEncoder":
        target_cols = self._resolve_columns(df)
        self.categories_ = {}

        for col in target_cols:
            counts = df[col].value_counts()
            top_cats = [k for k in counts.keys() if k != "null"][:self.max_categories]
            if self.drop_first and len(top_cats) > 1:
                top_cats = top_cats[1:]
            self.categories_[col] = top_cats

        self._fitted_params = {"categories": self.categories_}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cats = self.categories_.get(col, [])
            raw_vals = [str(x) if x is not None else "null" for x in df[col].to_list()]
            for cat in cats:
                new_col_name = f"{col}{self.prefix_sep}{cat}"
                indicator = [1 if v == cat else 0 for v in raw_vals]
                result.add_column(new_col_name, indicator)
            result = result.drop_column(col)

        return result
