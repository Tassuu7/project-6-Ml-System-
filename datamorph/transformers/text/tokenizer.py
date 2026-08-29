"""
DataMorph Studio - Regex Tokenizer Transformer
Segments text into lexical token arrays using configurable regular expressions.
"""

import re
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class RegexTokenizer(BaseTransformer):
    def __init__(self, pattern: str = r'\b\w+\b', lowercase: bool = True,
                 columns: Optional[List[str]] = None, name: str = "RegexTokenizer"):
        super().__init__(columns=columns, name=name)
        self.pattern = pattern
        self.lowercase = lowercase
        self._compiled_regex = re.compile(pattern)

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "RegexTokenizer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            tokenized = []
            for v in df[col].to_list():
                if v is None or v == "":
                    tokenized.append([])
                else:
                    s = str(v).lower() if self.lowercase else str(v)
                    tokens = self._compiled_regex.findall(s)
                    tokenized.append(tokens)
            result.add_column(f"{col}_tokens", tokenized)

        return result
