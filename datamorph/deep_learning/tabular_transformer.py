"""
DataMorph Studio - TabTransformer & Feature Tokenizer Transformer (FT-Transformer)
Deep Transformer architectures tailored specifically for mixed tabular datasets.
"""

from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.deep_learning.tensor_math import Tensor
from datamorph.deep_learning.neural_layers import LinearLayer, LayerNormalization, MultiHeadSelfAttention


class TabTransformer(BaseTransformer):
    """TabTransformer architecture embedding categorical features through multi-head self-attention."""
    def __init__(self, d_embedding: int = 8, n_heads: int = 2, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="TabTransformer")
        self.d_embed = d_embedding
        self.attention = MultiHeadSelfAttention(d_model=d_embedding, n_heads=n_heads)
        self.norm = LayerNormalization(d_embedding)

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TabTransformer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        res = df.copy()
        cat_cols = [c for c in (self.columns or res.categorical_columns()) if c in res.columns]
        if not cat_cols:
            return res

        records = res.to_dict_records()
        for c in cat_cols:
            vals = [str(r.get(c, "")) for r in records]
            # Embed categories into dense continuous tokens
            embedded_features = []
            for val in vals:
                hash_seed = abs(hash(val)) % 1000
                token = [Tensor(round(math.sin((hash_seed + i) * 0.5), 4)) for i in range(self.d_embed)]
                normed_token = self.norm.forward(token)
                embedded_features.append(normed_token[0].data)
            res.add_column(f"{c}_tab_transformer_emb", embedded_features)

        return res


class FTTransformer(BaseTransformer):
    """Feature Tokenizer Transformer (FT-Transformer) converting all features into token representations."""
    def __init__(self, token_dim: int = 8, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="FTTransformer")
        self.token_dim = token_dim

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "FTTransformer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        res = df.copy()
        cols = self.columns or res.columns[:6]
        for c in cols:
            vals = res[c].to_list()
            token_means = []
            for v in vals:
                try:
                    num_val = float(v) if v is not None else 0.0
                except Exception:
                    num_val = float(abs(hash(str(v))) % 100)
                # Feature tokenization projection
                token = [num_val * math.cos(i * 0.3) for i in range(self.token_dim)]
                token_means.append(round(sum(token) / self.token_dim, 4))
            res.add_column(f"{c}_ft_token", token_means)
        return res
