"""
DataMorph Studio - Native High-Performance In-Memory DataFrame & Series
Implements comprehensive tabular operations, column indexing, slicing, aggregations,
filtering, and conversion utilities natively in Python.
"""

import math
import copy
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Iterator
from datamorph.core.types import DataType
from datamorph.core.schema import Schema, Field
from datamorph.utils.math_utils import (
    mean, median, std_dev, variance, quantile, min_value, max_value,
    count_missing, distinct_values, mode
)


class Series:
    """
    Represents a 1-dimensional array of values with rich mathematical and transformation operations.
    """
    def __init__(self, data: List[Any], name: str = "series", dtype: Optional[DataType] = None):
        self.name = name
        self._data: List[Any] = list(data)
        self.dtype = dtype or self._infer_dtype()

    def _infer_dtype(self) -> DataType:
        non_nulls = [x for x in self._data if x is not None and x != ""]
        if not non_nulls:
            return DataType.UNKNOWN
        
        all_int = True
        all_float = True
        all_bool = True

        for item in non_nulls[:200]:
            if isinstance(item, bool):
                all_int = False
                all_float = False
                continue
            if isinstance(item, int):
                all_bool = False
                continue
            if isinstance(item, float):
                all_bool = False
                all_int = False
                continue
            if isinstance(item, str):
                all_bool = False
                all_int = False
                all_float = False
                break
        
        if all_bool:
            return DataType.BOOLEAN
        if all_int:
            return DataType.NUMERIC_INT
        if all_float:
            return DataType.NUMERIC_FLOAT
        return DataType.CATEGORICAL_NOMINAL

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index: Union[int, slice]) -> Any:
        if isinstance(index, slice):
            return Series(self._data[index], name=self.name, dtype=self.dtype)
        return self._data[index]

    def __setitem__(self, index: int, value: Any):
        self._data[index] = value

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def to_list(self) -> List[Any]:
        return list(self._data)

    def is_null(self) -> List[bool]:
        return [x is None or (isinstance(x, float) and math.isnan(x)) or x == "" for x in self._data]

    def not_null(self) -> List[bool]:
        return [not x for x in self.is_null()]

    def count(self) -> int:
        return sum(1 for x in self.not_null() if x)

    def missing_count(self) -> int:
        return sum(1 for x in self.is_null() if x)

    def missing_percentage(self) -> float:
        if not self._data:
            return 0.0
        return round((self.missing_count() / len(self._data)) * 100.0, 2)

    def values_numeric(self) -> List[float]:
        result = []
        for x in self._data:
            if x is not None and x != "":
                try:
                    f = float(x)
                    if not math.isnan(f):
                        result.append(f)
                except (ValueError, TypeError):
                    pass
        return result

    def mean(self) -> Optional[float]:
        return mean(self.values_numeric())

    def median(self) -> Optional[float]:
        return median(self.values_numeric())

    def mode(self) -> Optional[Any]:
        return mode(self._data)

    def std(self) -> Optional[float]:
        return std_dev(self.values_numeric())

    def var(self) -> Optional[float]:
        return variance(self.values_numeric())

    def min(self) -> Optional[float]:
        return min_value(self.values_numeric())

    def max(self) -> Optional[float]:
        return max_value(self.values_numeric())

    def quantile(self, q: float) -> Optional[float]:
        return quantile(self.values_numeric(), q)

    def distinct_count(self) -> int:
        return len(set(x for x in self._data if x is not None))

    def unique_values(self) -> List[Any]:
        seen = set()
        out = []
        for x in self._data:
            if x is not None and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def value_counts(self) -> Dict[Any, int]:
        counts = {}
        for x in self._data:
            key = "null" if x is None or x == "" else str(x)
            counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    def apply(self, func: Callable[[Any], Any]) -> "Series":
        new_data = [func(x) for x in self._data]
        return Series(new_data, name=self.name)

    def fillna(self, value: Any) -> "Series":
        new_data = [value if (x is None or (isinstance(x, float) and math.isnan(x)) or x == "") else x for x in self._data]
        return Series(new_data, name=self.name, dtype=self.dtype)

    def replace(self, to_replace: Dict[Any, Any]) -> "Series":
        new_data = [to_replace.get(x, x) for x in self._data]
        return Series(new_data, name=self.name, dtype=self.dtype)

    def clip(self, lower: Optional[float] = None, upper: Optional[float] = None) -> "Series":
        new_data = []
        for x in self._data:
            if x is None or x == "":
                new_data.append(x)
            else:
                try:
                    val = float(x)
                    if lower is not None and val < lower:
                        val = lower
                    if upper is not None and val > upper:
                        val = upper
                    new_data.append(val)
                except (ValueError, TypeError):
                    new_data.append(x)
        return Series(new_data, name=self.name, dtype=self.dtype)


class DataFrame:
    """
    Tabular in-memory matrix with rich column-oriented data structures,
    slicing, transformation, filtering, and aggregation.
    """
    def __init__(self, data: Optional[Union[Dict[str, List[Any]], List[Dict[str, Any]]]] = None,
                 schema: Optional[Schema] = None):
        self._columns: Dict[str, Series] = {}
        self._length: int = 0
        self.schema: Optional[Schema] = schema

        if data:
            if isinstance(data, dict):
                for col_name, values in data.items():
                    self.add_column(col_name, values)
            elif isinstance(data, list) and len(data) > 0:
                col_names = list(data[0].keys())
                for col in col_names:
                    col_data = [row.get(col) for row in data]
                    self.add_column(col, col_data)

    def add_column(self, name: str, values: Union[List[Any], Series]):
        if isinstance(values, Series):
            series = values
            series.name = name
        else:
            series = Series(list(values), name=name)

        if not self._columns:
            self._length = len(series)
        else:
            if len(series) != self._length:
                raise ValueError(f"Length mismatch: column '{name}' has {len(series)} rows, expected {self._length}")

        self._columns[name] = series

    def drop_column(self, name: str) -> "DataFrame":
        df = self.copy()
        if name in df._columns:
            del df._columns[name]
        return df

    def rename_column(self, old_name: str, new_name: str) -> "DataFrame":
        df = self.copy()
        if old_name in df._columns:
            series = df._columns.pop(old_name)
            series.name = new_name
            df._columns[new_name] = series
        return df

    @property
    def columns(self) -> List[str]:
        return list(self._columns.keys())

    @property
    def shape(self) -> Tuple[int, int]:
        return self._length, len(self._columns)

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, item: Union[str, List[str], slice]) -> Any:
        if isinstance(item, str):
            if item not in self._columns:
                raise KeyError(f"Column '{item}' not found in DataFrame")
            return self._columns[item]
        elif isinstance(item, list):
            df = DataFrame()
            for col in item:
                if col in self._columns:
                    df.add_column(col, self._columns[col].to_list())
            return df
        elif isinstance(item, slice):
            df = DataFrame()
            for col_name, s in self._columns.items():
                df.add_column(col_name, s[item].to_list())
            return df
        raise TypeError(f"Invalid index type: {type(item)}")

    def __setitem__(self, key: str, value: Union[List[Any], Series]):
        self.add_column(key, value)

    def head(self, n: int = 5) -> "DataFrame":
        return self[:min(n, self._length)]

    def tail(self, n: int = 5) -> "DataFrame":
        start = max(0, self._length - n)
        return self[start:self._length]

    def copy(self) -> "DataFrame":
        df = DataFrame()
        for col_name, s in self._columns.items():
            df.add_column(col_name, list(s.to_list()))
        if self.schema:
            df.schema = copy.deepcopy(self.schema)
        return df

    def to_dict_records(self) -> List[Dict[str, Any]]:
        records = []
        cols = self.columns
        for i in range(self._length):
            row = {}
            for col in cols:
                row[col] = self._columns[col][i]
            records.append(row)
        return records

    def to_column_dict(self) -> Dict[str, List[Any]]:
        return {col: s.to_list() for col, s in self._columns.items()}

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> "DataFrame":
        records = self.to_dict_records()
        filtered = [r for r in records if predicate(r)]
        return DataFrame(filtered)

    def select_dtypes(self, include: List[DataType]) -> "DataFrame":
        df = DataFrame()
        for col_name, s in self._columns.items():
            if s.dtype in include:
                df.add_column(col_name, s.to_list())
        return df

    def numeric_columns(self) -> List[str]:
        return [col for col, s in self._columns.items() if s.dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT)]

    def categorical_columns(self) -> List[str]:
        return [col for col, s in self._columns.items() if s.dtype in (DataType.CATEGORICAL_NOMINAL, DataType.CATEGORICAL_ORDINAL)]

    def describe(self) -> Dict[str, Dict[str, Any]]:
        stats = {}
        for col in self.columns:
            s = self._columns[col]
            col_stat = {
                "dtype": s.dtype.value if isinstance(s.dtype, DataType) else str(s.dtype),
                "count": s.count(),
                "missing": s.missing_count(),
                "missing_pct": s.missing_percentage(),
                "distinct": s.distinct_count(),
            }
            if s.dtype in (DataType.NUMERIC_INT, DataType.NUMERIC_FLOAT):
                col_stat.update({
                    "mean": s.mean(),
                    "std": s.std(),
                    "min": s.min(),
                    "q25": s.quantile(0.25),
                    "median": s.median(),
                    "q75": s.quantile(0.75),
                    "max": s.max(),
                })
            else:
                col_stat.update({
                    "mode": s.mode(),
                    "top_categories": list(s.value_counts().keys())[:5]
                })
            stats[col] = col_stat
        return stats
