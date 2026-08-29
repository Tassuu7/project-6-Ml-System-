"""
DataMorph Studio - Network Graph In-Degree & Out-Degree Centrality Extractor
Extracts graph connectivity centrality features for fraud networks and social graphs.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class DegreeCentralityExtractor(BaseTransformer):
    def __init__(self, source_col: str, target_col: str, name: str = "DegreeCentralityExtractor"):
        super().__init__(columns=[source_col, target_col], name=name)
        self.source_col = source_col
        self.target_col = target_col
        self.in_degree_: Dict[str, int] = {}
        self.out_degree_: Dict[str, int] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "DegreeCentralityExtractor":
        src_vals = [str(x) for x in df[self.source_col].to_list()]
        dst_vals = [str(x) for x in df[self.target_col].to_list()]

        self.in_degree_ = {}
        self.out_degree_ = {}

        for s, d in zip(src_vals, dst_vals):
            self.out_degree_[s] = self.out_degree_.get(s, 0) + 1
            self.in_degree_[d] = self.in_degree_.get(d, 0) + 1

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()

        src_out = [self.out_degree_.get(str(x), 0) for x in df[self.source_col].to_list()]
        dst_in = [self.in_degree_.get(str(x), 0) for x in df[self.target_col].to_list()]

        result.add_column(f"{self.source_col}_out_degree", src_out)
        result.add_column(f"{self.target_col}_in_degree", dst_in)
        return result
