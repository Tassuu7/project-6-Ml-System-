"""
DataMorph Studio - Count Vectorizer (Bag of Words)
Converts text into token frequency occurrence count vectors.
"""

import re
from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class CountVectorizer(BaseTransformer):
    def __init__(self, max_features: int = 15, columns: Optional[List[str]] = None, name: str = "CountVectorizer"):
        super().__init__(columns=columns, name=name)
        self.max_features = max_features
        self.vocabulary_: Dict[str, List[str]] = {}

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\b[a-zA-Z]{2,}\b', str(text).lower())

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "CountVectorizer":
        target_cols = self._resolve_columns(df)
        self.vocabulary_ = {}

        for col in target_cols:
            word_counts: Dict[str, int] = {}
            for doc in df[col].to_list():
                for t in self._tokenize(doc):
                    word_counts[t] = word_counts.get(t, 0) + 1
            sorted_vocab = sorted(word_counts.keys(), key=lambda t: word_counts[t], reverse=True)[:self.max_features]
            self.vocabulary_[col] = sorted_vocab

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            vocab = self.vocabulary_.get(col, [])
            for word in vocab:
                counts = []
                for doc in df[col].to_list():
                    tokens = self._tokenize(doc)
                    counts.append(tokens.count(word))
                result.add_column(f"{col}_count_{word}", counts)

        return result
