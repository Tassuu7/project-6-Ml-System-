"""
DataMorph Studio - Deep Statistical Column Profiler
Calculates comprehensive moments (mean, variance, skewness, kurtosis), percentiles, and entropy.
"""

import math
from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame
from datamorph.utils.math_utils import mean, median, std_dev, variance, quantile


class DeepColumnProfiler:
    """Computes comprehensive univariate statistical profiles per feature."""

    @classmethod
    def profile_column(cls, values: List[Any], name: str = "feature") -> Dict[str, Any]:
        total = len(values)
        if total == 0:
            return {"name": name, "count": 0}

        nulls = sum(1 for v in values if v is None or v == "")
        distinct_vals = set(v for v in values if v is not None and v != "")
        distinct_count = len(distinct_vals)

        # Check if numeric
        numeric_vals = []
        for v in values:
            if v is not None and v != "":
                try:
                    numeric_vals.append(float(v))
                except Exception:
                    pass

        is_numeric = (len(numeric_vals) / float(max(1, total - nulls))) > 0.8 if (total - nulls) > 0 else False

        profile = {
            "name": name,
            "total_rows": total,
            "missing_count": nulls,
            "missing_percentage": round((nulls / float(total)) * 100.0, 2),
            "distinct_count": distinct_count,
            "distinct_percentage": round((distinct_count / float(total)) * 100.0, 2),
            "is_numeric": is_numeric,
            "is_constant": distinct_count == 1,
            "is_unique": distinct_count == total
        }

        if is_numeric and numeric_vals:
            m = mean(numeric_vals) or 0.0
            s = std_dev(numeric_vals) or 0.0
            n_num = len(numeric_vals)
            # Skewness & Kurtosis
            skewness = 0.0
            kurtosis = 0.0
            if s > 0 and n_num > 2:
                skewness = sum(((x - m) / s) ** 3 for x in numeric_vals) / n_num
                kurtosis = (sum(((x - m) / s) ** 4 for x in numeric_vals) / n_num) - 3.0

            profile["stats"] = {
                "mean": round(m, 4),
                "std": round(s, 4),
                "variance": round(variance(numeric_vals) or 0.0, 4),
                "min": min(numeric_vals),
                "q25": quantile(numeric_vals, 0.25),
                "median": median(numeric_vals),
                "q75": quantile(numeric_vals, 0.75),
                "max": max(numeric_vals),
                "skewness": round(skewness, 4),
                "kurtosis": round(kurtosis, 4)
            }
        else:
            # Categorical frequency table
            counts: Dict[str, int] = {}
            for v in values:
                s_val = str(v) if v is not None else "null"
                counts[s_val] = counts.get(s_val, 0) + 1
            sorted_cats = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
            profile["top_categories"] = [{"category": cat, "count": cnt, "percentage": round((cnt/total)*100, 2)} for cat, cnt in sorted_cats]

        return profile

    @classmethod
    def profile_dataframe(cls, df: DataFrame) -> Dict[str, Any]:
        return {col: cls.profile_column(df[col].to_list(), name=col) for col in df.columns}
