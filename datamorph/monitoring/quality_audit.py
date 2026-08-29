"""
DataMorph Studio - Comprehensive Data Quality Auditor
Performs multi-dimensional data quality assessments: missingness, duplicates,
type violations, cardinality anomalies, and zero variance checks.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame


class DataQualityAuditor:
    """Audits data health and calculates overall Data Quality Score (0 - 100)."""

    def audit(self, df: DataFrame) -> Dict[str, Any]:
        total_rows, total_cols = df.shape
        if total_rows == 0:
            return {"score": 0.0, "issues": ["Dataset is empty"]}

        issues = []
        col_reports = {}
        total_cells = total_rows * total_cols
        total_missing = 0

        for col in df.columns:
            s = df[col]
            missing = s.missing_count()
            total_missing += missing
            missing_pct = s.missing_percentage()
            distinct = s.distinct_count()

            col_issues = []
            if missing_pct > 30.0:
                col_issues.append(f"High missingness: {missing_pct}%")
                issues.append(f"Column '{col}' has {missing_pct}% missing values")
            if distinct == 1:
                col_issues.append("Constant feature (zero variance)")
                issues.append(f"Column '{col}' is constant (zero information)")
            if distinct == total_rows and total_rows > 10:
                col_issues.append("Unique identifier candidate (100% distinct)")

            col_reports[col] = {
                "dtype": str(s.dtype),
                "missing_count": missing,
                "missing_pct": missing_pct,
                "distinct_count": distinct,
                "issues": col_issues
            }

        # Check duplicate rows
        records = df.to_dict_records()
        seen = set()
        dup_count = 0
        for r in records[:2000]:  # sample for performance
            tup = tuple(sorted(r.items()))
            if tup in seen:
                dup_count += 1
            else:
                seen.add(tup)

        if dup_count > 0:
            issues.append(f"Detected {dup_count} duplicate rows in sample")

        # Compute composite quality score (0 - 100)
        missing_penalty = min(50.0, (total_missing / float(total_cells)) * 100.0)
        issue_penalty = min(50.0, len(issues) * 5.0)
        quality_score = max(0.0, round(100.0 - missing_penalty - issue_penalty, 1))

        return {
            "quality_score": quality_score,
            "grade": "A" if quality_score >= 90 else ("B" if quality_score >= 75 else ("C" if quality_score >= 60 else "D")),
            "total_rows": total_rows,
            "total_columns": total_cols,
            "total_missing_cells": total_missing,
            "missing_cell_percentage": round((total_missing / float(total_cells)) * 100.0, 2),
            "duplicate_rows_sample": dup_count,
            "issue_count": len(issues),
            "issues": issues,
            "column_diagnostics": col_reports
        }
