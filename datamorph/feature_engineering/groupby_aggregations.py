"""
DataMorph Studio - GroupBy Entity Feature Aggregator
Calculates group-level mean, std, min, max, sum, count, and entity ratio deviations.
"""

from typing import List, Optional, Dict, Any
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean, std_dev


class GroupByAggregator(BaseTransformer):
    def __init__(self, group_by_column: str, agg_columns: List[str],
                 aggregations: List[str] = ["mean", "std", "min", "max"],
                 name: str = "GroupByAggregator"):
        super().__init__(columns=agg_columns, name=name)
        self.group_by_column = group_by_column
        self.agg_columns = agg_columns
        self.aggregations = aggregations
        self.group_stats_: Dict[str, Dict[str, Dict[str, float]]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "GroupByAggregator":
        records = df.to_dict_records()
        self.group_stats_ = {}

        # Collect group values
        groups: Dict[str, Dict[str, List[float]]] = {}
        for r in records:
            grp_key = str(r.get(self.group_by_column, "null"))
            groups.setdefault(grp_key, {c: [] for c in self.agg_columns})
            for col in self.agg_columns:
                try:
                    if r.get(col) is not None:
                        groups[grp_key][col].append(float(r[col]))
                except Exception:
                    pass

        # Compute summary statistics
        for grp_key, col_dict in groups.items():
            self.group_stats_[grp_key] = {}
            for col, vals in col_dict.items():
                if vals:
                    self.group_stats_[grp_key][col] = {
                        "mean": mean(vals) or 0.0,
                        "std": std_dev(vals) or 0.0,
                        "min": min(vals),
                        "max": max(vals),
                        "sum": sum(vals),
                        "count": float(len(vals))
                    }
                else:
                    self.group_stats_[grp_key][col] = {
                        "mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "sum": 0.0, "count": 0.0
                    }

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()
        records = df.to_dict_records()

        for col in self.agg_columns:
            for agg in self.aggregations:
                col_name = f"{col}_grp_{self.group_by_column}_{agg}"
                col_vals = []
                for r in records:
                    grp_key = str(r.get(self.group_by_column, "null"))
                    stats = self.group_stats_.get(grp_key, {}).get(col, {})
                    val = stats.get(agg, None)
                    col_vals.append(round(val, 4) if val is not None else None)
                result.add_column(col_name, col_vals)

        return result
