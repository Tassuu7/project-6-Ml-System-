"""
DataMorph Studio - Power Transformer (Yeo-Johnson & Box-Cox)
Applies non-linear power transformations to stabilize variance and minimize skewness.
"""

import math
from typing import List, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class PowerTransformer(BaseTransformer):
    def __init__(self, method: str = "yeo-johnson", lmbda: float = 0.5,
                 columns: Optional[List[str]] = None, name: str = "PowerTransformer"):
        super().__init__(columns=columns, name=name)
        self.method = method
        self.lmbda = lmbda

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "PowerTransformer":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            new_vals = []
            for val in df[col].to_list():
                if val is None or val == "":
                    new_vals.append(None)
                else:
                    try:
                        y = float(val)
                        if self.method == "yeo-johnson":
                            if y >= 0:
                                if self.lmbda != 0:
                                    t = ((y + 1.0) ** self.lmbda - 1.0) / self.lmbda
                                else:
                                    t = math.log(y + 1.0)
                            else:
                                if self.lmbda != 2:
                                    t = -((-y + 1.0) ** (2.0 - self.lmbda) - 1.0) / (2.0 - self.lmbda)
                                else:
                                    t = -math.log(-y + 1.0)
                        else:  # Box-Cox
                            y = max(1e-6, y)
                            if self.lmbda != 0:
                                t = (y ** self.lmbda - 1.0) / self.lmbda
                            else:
                                t = math.log(y)
                        new_vals.append(round(t, 6))
                    except Exception:
                        new_vals.append(val)
            result.add_column(col, new_vals)

        return result
