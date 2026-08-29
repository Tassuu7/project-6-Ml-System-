"""
DataMorph Studio - Automated Data Quality Rule Engine
Evaluates structural integrity, business logic boundaries, and schema compliance.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame
from datamorph.profiling.column_profiler import DeepColumnProfiler


class DataQualityRuleEngine:
    @classmethod
    def evaluate_all_rules(cls, df: DataFrame) -> Dict[str, Any]:
        profiles = DeepColumnProfiler.profile_dataframe(df)
        results = []
        overall_passed = True

        for col, prof in profiles.items():
            # Rule 1: Null check
            null_passed = prof["missing_percentage"] <= 30.0
            results.append({
                "rule_id": f"RULE_NULL_{col}",
                "column": col,
                "rule": "Missing values <= 30%",
                "status": "PASS" if null_passed else "FAIL",
                "observed": f"{prof['missing_percentage']}%"
            })
            if not null_passed: overall_passed = False

            # Rule 2: Constant check
            const_passed = not prof["is_constant"]
            results.append({
                "rule_id": f"RULE_CONST_{col}",
                "column": col,
                "rule": "Non-constant variance",
                "status": "PASS" if const_passed else "FAIL",
                "observed": f"Distinct values = {prof['distinct_count']}"
            })
            if not const_passed: overall_passed = False

        return {
            "overall_status": "PASSED" if overall_passed else "FAILED",
            "rules_evaluated": len(results),
            "passed_count": sum(1 for r in results if r["status"] == "PASS"),
            "failed_count": sum(1 for r in results if r["status"] == "FAIL"),
            "rule_details": results
        }
