"""
DataMorph Studio - Text Cleaner Transformer
Cleans and normalizes unstructured text data (lowercase, punct removal, whitespace trimming).
"""

import re
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class TextCleaner(BaseTransformer):
    def __init__(self, lowercase: bool = True, remove_punctuation: bool = True,
                 remove_numbers: bool = False, remove_extra_spaces: bool = True,
                 columns: Optional[List[str]] = None, name: str = "TextCleaner"):
        super().__init__(columns=columns, name=name)
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_extra_spaces = remove_extra_spaces

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TextCleaner":
        self.is_fitted = True
        return self

    def clean_text(self, text: Any) -> str:
        if text is None:
            return ""
        s = str(text)
        if self.lowercase:
            s = s.lower()
        if self.remove_numbers:
            s = re.sub(r'\d+', '', s)
        if self.remove_punctuation:
            s = re.sub(r'[^\w\s]', '', s)
        if self.remove_extra_spaces:
            s = re.sub(r'\s+', ' ', s).strip()
        return s

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cleaned = [self.clean_text(v) for v in df[col].to_list()]
            result.add_column(col, cleaned)

        return result
