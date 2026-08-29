"""
DataMorph Studio - Schema Definitions & Validation
Provides declarative typing, validation rules, constraints, and statistical profiling
for tabular datasets.
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
import re
from datamorph.core.types import DataType
from datamorph.core.exceptions import SchemaValidationError


@dataclass
class Field:
    """Defines a single schema field with type constraints and business rules."""
    name: str
    dtype: DataType
    nullable: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_categories: Optional[List[str]] = None
    regex_pattern: Optional[str] = None
    description: str = ""
    is_target: bool = False
    is_primary_key: bool = False
    tags: List[str] = field(default_factory=list)

    def validate_value(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None or (isinstance(value, float) and value != value) or value == "":
            if not self.nullable:
                return False, f"Field '{self.name}' does not allow null/missing values"
            return True, None

        if self.dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT):
            try:
                num_val = float(value)
                if self.min_value is not None and num_val < self.min_value:
                    return False, f"Value {num_val} for field '{self.name}' is below minimum {self.min_value}"
                if self.max_value is not None and num_val > self.max_value:
                    return False, f"Value {num_val} for field '{self.name}' is above maximum {self.max_value}"
            except (ValueError, TypeError):
                return False, f"Value '{value}' cannot be coerced to numeric for field '{self.name}'"

        elif self.dtype in (DataType.CATEGORICAL_NOMINAL, DataType.CATEGORICAL_ORDINAL):
            str_val = str(value)
            if self.allowed_categories and str_val not in self.allowed_categories:
                return False, f"Value '{str_val}' not in allowed categories for field '{self.name}'"

        elif self.dtype == DataType.TEXT:
            str_val = str(value)
            if self.regex_pattern:
                if not re.search(self.regex_pattern, str_val):
                    return False, f"Value '{str_val}' violates regex pattern '{self.regex_pattern}' for field '{self.name}'"

        return True, None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dtype": self.dtype.value if isinstance(self.dtype, DataType) else str(self.dtype),
            "nullable": self.nullable,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "allowed_categories": self.allowed_categories,
            "regex_pattern": self.regex_pattern,
            "description": self.description,
            "is_target": self.is_target,
            "is_primary_key": self.is_primary_key,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Field":
        dtype_val = data.get("dtype", "unknown")
        try:
            dtype = DataType(dtype_val)
        except ValueError:
            dtype = DataType.UNKNOWN
        return cls(
            name=data["name"],
            dtype=dtype,
            nullable=data.get("nullable", True),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            allowed_categories=data.get("allowed_categories"),
            regex_pattern=data.get("regex_pattern"),
            description=data.get("description", ""),
            is_target=data.get("is_target", False),
            is_primary_key=data.get("is_primary_key", False),
            tags=data.get("tags", []),
        )


class Schema:
    """Schema container representing the tabular feature specification."""
    def __init__(self, fields: Optional[List[Field]] = None, name: str = "DatasetSchema"):
        self.name = name
        self._fields: Dict[str, Field] = {}
        if fields:
            for f in fields:
                self.add_field(f)

    def add_field(self, field: Field):
        self._fields[field.name] = field

    def get_field(self, name: str) -> Optional[Field]:
        return self._fields.get(name)

    def remove_field(self, name: str):
        if name in self._fields:
            del self._fields[name]

    @property
    def field_names(self) -> List[str]:
        return list(self._fields.keys())

    @property
    def fields(self) -> List[Field]:
        return list(self._fields.values())

    @property
    def numeric_features(self) -> List[str]:
        return [
            f.name for f in self._fields.values()
            if f.dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT)
        ]

    @property
    def categorical_features(self) -> List[str]:
        return [
            f.name for f in self._fields.values()
            if f.dtype in (DataType.CATEGORICAL_NOMINAL, DataType.CATEGORICAL_ORDINAL)
        ]

    @property
    def text_features(self) -> List[str]:
        return [
            f.name for f in self._fields.values()
            if f.dtype == DataType.TEXT
        ]

    @property
    def datetime_features(self) -> List[str]:
        return [
            f.name for f in self._fields.values()
            if f.dtype in (DataType.DATETIME, DataType.TIMESTAMP)
        ]

    @property
    def target_feature(self) -> Optional[str]:
        for f in self._fields.values():
            if f.is_target:
                return f.name
        return None

    def validate_row(self, row: Dict[str, Any]) -> List[str]:
        errors = []
        for name, field in self._fields.items():
            val = row.get(name)
            valid, err = field.validate_value(val)
            if not valid:
                errors.append(err)
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fields": [f.to_dict() for f in self._fields.values()],
            "numeric_count": len(self.numeric_features),
            "categorical_count": len(self.categorical_features),
            "text_count": len(self.text_features),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Schema":
        schema = cls(name=data.get("name", "DatasetSchema"))
        for f_data in data.get("fields", []):
            schema.add_field(Field.from_dict(f_data))
        return schema
