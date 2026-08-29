"""
DataMorph Studio - Lexicon Sentiment Feature Extractor
Extracts positive, negative word counts and polarity ratio from text.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext

POSITIVE_WORDS = {"good", "great", "excellent", "positive", "fortunate", "correct", "superior", "best", "happy", "love", "awesome", "fast", "reliable"}
NEGATIVE_WORDS = {"bad", "terrible", "poor", "negative", "unfortunate", "wrong", "inferior", "worst", "sad", "hate", "slow", "error", "fail"}


class SentimentFeatureExtractor(BaseTransformer):
    def __init__(self, columns: Optional[List[str]] = None, name: str = "SentimentFeatureExtractor"):
        super().__init__(columns=columns, name=name)

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SentimentFeatureExtractor":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            pos_counts = []
            neg_counts = []
            polarities = []
            for doc in df[col].to_list():
                words = str(doc).lower().split()
                pos = sum(1 for w in words if w in POSITIVE_WORDS)
                neg = sum(1 for w in words if w in NEGATIVE_WORDS)
                total = pos + neg
                polarity = (pos - neg) / (total if total > 0 else 1.0)
                pos_counts.append(pos)
                neg_counts.append(neg)
                polarities.append(round(polarity, 4))

            result.add_column(f"{col}_pos_words", pos_counts)
            result.add_column(f"{col}_neg_words", neg_counts)
            result.add_column(f"{col}_polarity", polarities)

        return result
