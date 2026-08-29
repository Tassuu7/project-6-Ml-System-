"""
DataMorph Studio - Date-Time Component Feature Extractor
Extracts granular calendar components (year, month, day, dayofweek, hour, is_weekend).
"""

import datetime
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class DateTimeFeatureExtractor(BaseTransformer):
    def __init__(self, formats: Optional[List[str]] = None,
                 columns: Optional[List[str]] = None, name: str = "DateTimeFeatureExtractor"):
        super().__init__(columns=columns, name=name)
        self.formats = formats or ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "DateTimeFeatureExtractor":
        self.is_fitted = True
        return self

    def _parse_dt(self, val: Any) -> Optional[datetime.datetime]:
        if val is None or val == "":
            return None
        if isinstance(val, datetime.datetime):
            return val
        s = str(val).strip()
        for fmt in self.formats:
            try:
                return datetime.datetime.strptime(s, fmt)
            except ValueError:
                pass
        return None

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            dts = [self._parse_dt(v) for v in df[col].to_list()]
            result.add_column(f"{col}_year", [dt.year if dt else None for dt in dts])
            result.add_column(f"{col}_month", [dt.month if dt else None for dt in dts])
            result.add_column(f"{col}_day", [dt.day if dt else None for dt in dts])
            result.add_column(f"{col}_dayofweek", [dt.weekday() if dt else None for dt in dts])
            result.add_column(f"{col}_hour", [dt.hour if dt else None for dt in dts])
            result.add_column(f"{col}_is_weekend", [1 if (dt and dt.weekday() >= 5) else 0 for dt in dts])

        return result
