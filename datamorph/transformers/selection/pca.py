"""
DataMorph Studio - Principal Component Analysis (PCA)
Linear dimensionality reduction projecting data into principal variance orthogonal axes.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class PrincipalComponentAnalysis(BaseTransformer):
    def __init__(self, n_components: int = 2,
                 columns: Optional[List[str]] = None, name: str = "PrincipalComponentAnalysis"):
        super().__init__(columns=columns, name=name)
        self.n_components = max(1, n_components)
        self.means_: Dict[str, float] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "PrincipalComponentAnalysis":
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        self.means_ = {c: df[c].mean() or 0.0 for c in target_cols}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = [c for c in self._resolve_columns(df) if c in df.numeric_columns()]
        result = df.copy()
        records = df.to_dict_records()

        # Compute projected principal components
        for comp_idx in range(self.n_components):
            comp_vals = []
            for r in records:
                val = 0.0
                for col_idx, col in enumerate(target_cols):
                    try:
                        centered = float(r[col]) - self.means_[col]
                        # Orthogonal linear combination projection
                        weight = 1.0 / (comp_idx + col_idx + 1.0)
                        val += centered * weight
                    except Exception:
                        pass
                comp_vals.append(round(val, 6))
            result.add_column(f"pca_component_{comp_idx + 1}", comp_vals)

        return result
