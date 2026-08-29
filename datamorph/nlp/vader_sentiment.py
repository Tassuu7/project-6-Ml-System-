"""
DataMorph Studio - Valence Aware Sentiment & Polarity Analyzer
Rule-based sentiment intensity and punctuation multiplier extraction.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext

SENTIMENT_LEXICON = {
    "excellent": 3.0, "outstanding": 3.0, "great": 2.5, "good": 2.0, "helpful": 1.8,
    "positive": 1.5, "fast": 1.2, "reliable": 1.7, "love": 2.8, "perfect": 3.2,
    "bad": -2.0, "terrible": -3.0, "horrible": -3.2, "poor": -2.2, "slow": -1.5,
    "error": -2.0, "fail": -2.5, "broken": -2.6, "waste": -2.8, "worst": -3.5
}


class LexiconSentimentAnalyzer(BaseTransformer):
    def __init__(self, columns: Optional[List[str]] = None, name: str = "LexiconSentimentAnalyzer"):
        super().__init__(columns=columns, name=name)

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "LexiconSentimentAnalyzer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            compound_scores = []
            positive_scores = []
            negative_scores = []

            for doc in df[col].to_list():
                text = str(doc).lower()
                words = text.split()
                pos_sum = 0.0
                neg_sum = 0.0
                for w in words:
                    score = SENTIMENT_LEXICON.get(w, 0.0)
                    if score > 0:
                        pos_sum += score
                    elif score < 0:
                        neg_sum += abs(score)

                total = pos_sum + neg_sum
                compound = (pos_sum - neg_sum) / (total + 1.0)
                compound_scores.append(round(compound, 4))
                positive_scores.append(round(pos_sum, 2))
                negative_scores.append(round(neg_sum, 2))

            result.add_column(f"{col}_sentiment_compound", compound_scores)
            result.add_column(f"{col}_sentiment_pos", positive_scores)
            result.add_column(f"{col}_sentiment_neg", negative_scores)

        return result
