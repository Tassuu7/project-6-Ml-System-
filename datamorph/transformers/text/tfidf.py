"""
DataMorph Studio - TF-IDF Vectorizer
Extracts Term Frequency - Inverse Document Frequency features from text columns.
"""

import re
import math
from typing import List, Optional, Dict, Set
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class TFIDFVectorizer(BaseTransformer):
    def __init__(self, max_features: int = 20, min_df: int = 1,
                 columns: Optional[List[str]] = None, name: str = "TFIDFVectorizer"):
        super().__init__(columns=columns, name=name)
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_: Dict[str, List[str]] = {}
        self.idf_: Dict[str, Dict[str, float]] = {}

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\b[a-zA-Z]{2,}\b', str(text).lower())

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TFIDFVectorizer":
        target_cols = self._resolve_columns(df)
        n_docs = len(df) or 1
        self.vocabulary_ = {}
        self.idf_ = {}

        for col in target_cols:
            doc_counts: Dict[str, int] = {}
            for doc in df[col].to_list():
                tokens = set(self._tokenize(doc))
                for t in tokens:
                    doc_counts[t] = doc_counts.get(t, 0) + 1

            # Select top max_features by document frequency
            valid_tokens = {t: c for t, c in doc_counts.items() if c >= self.min_df}
            sorted_vocab = sorted(valid_tokens.keys(), key=lambda t: valid_tokens[t], reverse=True)[:self.max_features]
            self.vocabulary_[col] = sorted_vocab

            idf_map = {}
            for t in sorted_vocab:
                df_count = valid_tokens[t]
                idf_map[t] = math.log((1.0 + n_docs) / (1.0 + df_count)) + 1.0
            self.idf_[col] = idf_map

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            vocab = self.vocabulary_.get(col, [])
            idf_map = self.idf_.get(col, {})
            
            # Compute TF-IDF matrix
            matrix = {f"{col}_tfidf_{word}": [] for word in vocab}
            for doc in df[col].to_list():
                tokens = self._tokenize(doc)
                total_tokens = len(tokens) or 1
                counts: Dict[str, int] = {}
                for t in tokens:
                    counts[t] = counts.get(t, 0) + 1

                for word in vocab:
                    tf = counts.get(word, 0) / total_tokens
                    idf = idf_map.get(word, 1.0)
                    matrix[f"{col}_tfidf_{word}"].append(round(tf * idf, 6))

            for feat_name, feat_vals in matrix.items():
                result.add_column(feat_name, feat_vals)

        return result
