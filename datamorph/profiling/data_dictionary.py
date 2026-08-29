"""
DataMorph Studio - Automated Data Dictionary & Metadata Catalog Generator
Generates enterprise data catalog schemas with inferred business descriptions.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame
from datamorph.profiling.column_profiler import DeepColumnProfiler


class DataDictionaryGenerator:
    @classmethod
    def generate(cls, df: DataFrame, title: str = "Dataset Dictionary") -> Dict[str, Any]:
        profiles = DeepColumnProfiler.profile_dataframe(df)
        columns_dict = []

        for col, prof in profiles.items():
            dtype_label = "Continuous Float" if prof["is_numeric"] else "Categorical String"
            if prof.get("is_unique"): dtype_label = "Unique Primary Key Candidate"

            columns_dict.append({
                "column_name": col,
                "data_type": dtype_label,
                "missing_pct": prof["missing_percentage"],
                "distinct_count": prof["distinct_count"],
                "sample_values": [str(x) for x in df[col].to_list()[:5] if x is not None],
                "description": f"Automated feature description for {col} ({dtype_label})"
            })

        return {
            "catalog_title": title,
            "total_columns": len(df.columns),
            "total_rows": len(df),
            "columns": columns_dict
        }
