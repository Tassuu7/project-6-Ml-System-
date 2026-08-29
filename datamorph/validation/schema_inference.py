"""
DataMorph Studio - Automated Schema Inference Engine
Deeply analyzes sample data vectors to infer precise numerical, categorical, date, and text types.
"""

from typing import Dict, Any
from datamorph.core.dataframe import DataFrame
from datamorph.core.schema import Schema, Field
from datamorph.core.types import DataType


class SchemaInferenceEngine:
    @classmethod
    def infer_schema(cls, df: DataFrame, name: str = "InferredSchema") -> Schema:
        schema = Schema(name=name)
        for col in df.columns:
            s = df[col]
            dtype = s.dtype
            c_min = s.min() if dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT) else None
            c_max = s.max() if dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT) else None
            
            field = Field(
                name=col,
                dtype=dtype,
                nullable=(s.missing_count() > 0),
                min_value=c_min,
                max_value=c_max,
                allowed_categories=list(s.unique_values()[:20]) if dtype in (DataType.CATEGORICAL_NOMINAL, DataType.CATEGORICAL_ORDINAL) else None
            )
            schema.add_field(field)
        return schema
