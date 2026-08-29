"""
DataMorph Studio - Base Transformer Architecture
Provides the abstract base class and state contract for all data transformations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.core.exceptions import TransformerError, TransformerNotFittedError


class BaseTransformer(ABC):
    """
    Abstract Base Class for all DataMorph Transformers.
    Enforces scikit-learn compatible fit(), transform(), and fit_transform() lifecycle.
    """
    def __init__(self, columns: Optional[List[str]] = None, name: Optional[str] = None):
        self.columns = columns or []
        self.name = name or self.__class__.__name__
        self.is_fitted: bool = False
        self._fitted_params: Dict[str, Any] = {}

    @abstractmethod
    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "BaseTransformer":
        """Learn statistical parameters from input DataFrame."""
        pass

    @abstractmethod
    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        """Apply learned transformations to input DataFrame."""
        pass

    def fit_transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        """Fit parameters and transform dataset in a single pass."""
        return self.fit(df, context=context).transform(df, context=context)

    def check_is_fitted(self):
        if not self.is_fitted:
            raise TransformerNotFittedError(self.name)

    def _resolve_columns(self, df: DataFrame) -> List[str]:
        if self.columns:
            missing = [c for c in self.columns if c not in df.columns]
            if missing:
                raise TransformerError(f"Specified columns {missing} not present in DataFrame", transformer_name=self.name)
            return self.columns
        return df.columns

    def get_params(self) -> Dict[str, Any]:
        """Return learned parameters dictionary."""
        return dict(self._fitted_params)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize transformer configuration and state for DAG execution."""
        return {
            "type": self.__class__.__name__,
            "name": self.name,
            "columns": self.columns,
            "is_fitted": self.is_fitted,
            "fitted_params": self._fitted_params
        }
