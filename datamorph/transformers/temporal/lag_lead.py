"""
DataMorph Studio - Lag & Lead Time-Series Feature Generator
Creates shift-based historical and forward-looking features for sequential models.
"""

from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class LagLeadFeatureGenerator(BaseTransformer):
    def __init__(self, lags: List[int] = [1, 2, 3], leads: List[int] = [],
                 columns: Optional[List[str]] = None, name: str = "LagLeadFeatureGenerator"):
        super().__init__(columns=columns, name=name)
        self.lags = lags
        self.leads = leads

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "LagLeadFeatureGenerator":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()
        n_rows = len(df)

        for col in target_cols:
            raw = df[col].to_list()
            # Lags
            for lag in self.lags:
                shifted = [None] * lag + raw[:max(0, n_rows - lag)]
                result.add_column(f"{col}_lag_{lag}", shifted[:n_rows])
            # Leads
            for lead in self.leads:
                shifted = raw[lead:] + [None] * lead
                result.add_column(f"{col}_lead_{lead}", shifted[:n_rows])

        return result
