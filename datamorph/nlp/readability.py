"""
DataMorph Studio - Readability & Lexical Complexity Metrics
Extracts Flesch Reading Ease, Automated Readability Index (ARI), and Token Length statistics.
"""

import re
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class ReadabilityMetricExtractor(BaseTransformer):
    def __init__(self, columns: Optional[List[str]] = None, name: str = "ReadabilityMetricExtractor"):
        super().__init__(columns=columns, name=name)

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "ReadabilityMetricExtractor":
        self.is_fitted = True
        return self

    def _count_syllables(self, word: str) -> int:
        w = word.lower()
        count = len(re.findall(r'[aeiouy]+', w))
        if w.endswith('e') and not w.endswith('le') and len(w) > 2:
            count = max(1, count - 1)
        return max(1, count)

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            flesch_scores = []
            avg_word_lengths = []

            for doc in df[col].to_list():
                text = str(doc)
                words = re.findall(r'\b\w+\b', text)
                sentences = re.split(r'[.!?]+', text)
                sentences = [s for s in sentences if s.strip()]

                n_words = len(words) or 1
                n_sentences = len(sentences) or 1
                n_syllables = sum(self._count_syllables(w) for w in words) or 1

                # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
                flesch = 206.835 - (1.015 * (n_words / n_sentences)) - (84.6 * (n_syllables / n_words))
                flesch_scores.append(round(max(0.0, min(100.0, flesch)), 2))

                avg_len = sum(len(w) for w in words) / float(n_words)
                avg_word_lengths.append(round(avg_len, 2))

            result.add_column(f"{col}_flesch_score", flesch_scores)
            result.add_column(f"{col}_avg_word_len", avg_word_lengths)

        return result
