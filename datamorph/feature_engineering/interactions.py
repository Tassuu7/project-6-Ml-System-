"""
DataMorph Studio - Polynomial & Pairwise Feature Interaction Generator
Synthesizes higher-order interactive terms x_i * x_j and powers x_i^d for numerical features.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class PolynomialInteractionGenerator(BaseTransformer):
    def __init__(self, degree: int = 2, include_bias: bool = False,
                 interaction_only: bool = False, columns: Optional[List[str]] = None,
                 name: str = "PolynomialInteractionGenerator"):
        super().__init__(columns=columns, name=name)
        self.degree = degree
        self.include_bias = include_bias
        self.interaction_only = interaction_only

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "PolynomialInteractionGenerator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()
        n = len(target_cols)

        # Pairwise cross-multiplication
        for i in range(n):
            col_i = target_cols[i]
            v_i = df[col_i].to_list()
            start_j = i + 1 if self.interaction_only else i
            for j in range(start_j, n):
                col_j = target_cols[j]
                v_j = df[col_j].to_list()
                inter_name = f"{col_i}_x_{col_j}" if i != j else f"{col_i}_sq"
                inter_vals = []
                for val_a, val_b in zip(v_i, v_j):
                    try:
                        inter_vals.append(round(float(val_a) * float(val_b), 6) if val_a is not None and val_b is not None else None)
                    except Exception:
                        inter_vals.append(None)
                result.add_column(inter_name, inter_vals)

        return result
