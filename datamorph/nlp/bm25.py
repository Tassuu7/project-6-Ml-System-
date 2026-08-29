"""
DataMorph Studio - Okapi BM25 Ranking Score Feature Extractor
Computes non-linear probabilistic term relevance BM25 scores across document corpus.
"""

import re
import math
from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class BM25FeatureExtractor(BaseTransformer):
    def __init__(self, query_terms: List[str] = ["important", "error", "success", "alert"],
                 k1: float = 1.5, b: float = 0.75,
                 columns: Optional[List[str]] = None, name: str = "BM25FeatureExtractor"):
        super().__init__(columns=columns, name=name)
        self.query_terms = [q.lower() for q in query_terms]
        self.k1 = k1
        self.b = b
        self.avg_doc_len_: float = 1.0
        self.idf_: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\b[a-zA-Z]{2,}\b', str(text).lower())

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "BM25FeatureExtractor":
        target_cols = self._resolve_columns(df)
        n_docs = len(df) or 1

        all_lengths = []
        for col in target_cols:
            doc_counts = {t: 0 for t in self.query_terms}
            for doc in df[col].to_list():
                tokens = self._tokenize(doc)
                all_lengths.append(len(tokens))
                token_set = set(tokens)
                for t in self.query_terms:
                    if t in token_set:
                        doc_counts[t] += 1

            self.avg_doc_len_ = sum(all_lengths) / max(1, len(all_lengths))
            for t in self.query_terms:
                df_cnt = doc_counts[t]
                # Standard BM25 Robertson-Sparck Jones IDF
                idf = math.log(((n_docs - df_cnt + 0.5) / (df_cnt + 0.5)) + 1.0)
                self.idf_[t] = max(0.0, idf)

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            bm25_scores = []
            for doc in df[col].to_list():
                tokens = self._tokenize(doc)
                doc_len = len(tokens)
                score = 0.0
                for term in self.query_terms:
                    tf = tokens.count(term)
                    if tf > 0:
                        idf = self.idf_.get(term, 0.0)
                        denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len_))
                        score += idf * (tf * (self.k1 + 1.0)) / max(1e-12, denom)
                bm25_scores.append(round(score, 4))
            result.add_column(f"{col}_bm25_score", bm25_scores)

        return result
