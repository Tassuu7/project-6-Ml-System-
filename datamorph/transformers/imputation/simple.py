"""
DataMorph Studio - Simple Imputation Transformer
Handles missing values via statistical strategies: mean, median, mode, constant, forward/backward fill.
"""

from typing import List, Optional, Dict, Any, Union
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.core.types import ImputationStrategy


class SimpleImputer(BaseTransformer):
    def __init__(self, strategy: Union[str, ImputationStrategy] = ImputationStrategy.MEAN,
                 fill_value: Optional[Any] = None, columns: Optional[List[str]] = None, name: str = "SimpleImputer"):
        super().__init__(columns=columns, name=name)
        self.strategy = ImputationStrategy(strategy) if isinstance(strategy, str) else strategy
        self.fill_value = fill_value
        self.statistics_: Dict[str, Any] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SimpleImputer":
        target_cols = self._resolve_columns(df)
        self.statistics_ = {}

        for col in target_cols:
            series = df[col]
            if self.strategy == ImputationStrategy.MEAN:
                val = series.mean()
                self.statistics_[col] = val if val is not None else 0.0
            elif self.strategy == ImputationStrategy.MEDIAN:
                val = series.median()
                self.statistics_[col] = val if val is not None else 0.0
            elif self.strategy == ImputationStrategy.MODE:
                val = series.mode()
                self.statistics_[col] = val if val is not None else ""
            elif self.strategy == ImputationStrategy.CONSTANT:
                self.statistics_[col] = self.fill_value
            elif self.strategy in (ImputationStrategy.FORWARD_FILL, ImputationStrategy.BACKWARD_FILL):
                self.statistics_[col] = None

        self._fitted_params = {"statistics": self.statistics_, "strategy": self.strategy.value}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            if self.strategy in (ImputationStrategy.MEAN, ImputationStrategy.MEDIAN, ImputationStrategy.MODE, ImputationStrategy.CONSTANT):
                fill_val = self.statistics_.get(col, 0.0)
                result.add_column(col, result[col].fillna(fill_val))
            elif self.strategy == ImputationStrategy.FORWARD_FILL:
                raw = result[col].to_list()
                last_valid = None
                for i in range(len(raw)):
                    if raw[i] is not None and raw[i] != "":
                        last_valid = raw[i]
                    else:
                        raw[i] = last_valid
                result.add_column(col, raw)
            elif self.strategy == ImputationStrategy.BACKWARD_FILL:
                raw = result[col].to_list()
                last_valid = None
                for i in range(len(raw) - 1, -1, -1):
                    if raw[i] is not None and raw[i] != "":
                        last_valid = raw[i]
                    else:
                        raw[i] = last_valid
                result.add_column(col, raw)

        return result
