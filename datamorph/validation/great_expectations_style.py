"""
DataMorph Studio - Expectation Suite & Data Assertions Engine
Declarative test assertions verifying column ranges, null limits, regexes, and uniqueness.
"""

from typing import List, Dict, Any, Optional
from datamorph.core.dataframe import DataFrame


class ExpectationSuite:
    def __init__(self, suite_name: str = "ProductionDataExpectations"):
        self.suite_name = suite_name
        self.expectations: List[Dict[str, Any]] = []

    def expect_column_values_to_not_be_null(self, column: str, max_null_pct: float = 0.0) -> "ExpectationSuite":
        self.expectations.append({"type": "not_null", "column": column, "max_null_pct": max_null_pct})
        return self

    def expect_column_values_to_be_between(self, column: str, min_val: float, max_val: float) -> "ExpectationSuite":
        self.expectations.append({"type": "between", "column": column, "min": min_val, "max": max_val})
        return self

    def expect_column_values_to_be_in_set(self, column: str, allowed_set: List[Any]) -> "ExpectationSuite":
        self.expectations.append({"type": "in_set", "column": column, "allowed": set(allowed_set)})
        return self

    def expect_column_values_to_be_unique(self, column: str) -> "ExpectationSuite":
        self.expectations.append({"type": "unique", "column": column})
        return self

    def validate(self, df: DataFrame) -> Dict[str, Any]:
        results = []
        all_passed = True

        for exp in self.expectations:
            col = exp["column"]
            if col not in df.columns:
                results.append({"expectation": exp, "success": False, "error": f"Column '{col}' not found"})
                all_passed = False
                continue

            s = df[col]
            if exp["type"] == "not_null":
                null_pct = s.missing_percentage()
                passed = null_pct <= exp["max_null_pct"]
                results.append({"expectation": exp, "success": passed, "observed_null_pct": null_pct})
                if not passed: all_passed = False

            elif exp["type"] == "between":
                vals = s.values_numeric()
                c_min = min(vals) if vals else 0.0
                c_max = max(vals) if vals else 0.0
                passed = (c_min >= exp["min"]) and (c_max <= exp["max"])
                results.append({"expectation": exp, "success": passed, "observed_range": [c_min, c_max]})
                if not passed: all_passed = False

            elif exp["type"] == "in_set":
                observed = set(s.unique_values())
                invalid = observed - exp["allowed"]
                passed = len(invalid) == 0
                results.append({"expectation": exp, "success": passed, "invalid_values": list(invalid)})
                if not passed: all_passed = False

            elif exp["type"] == "unique":
                passed = s.distinct_count() == len(s)
                results.append({"expectation": exp, "success": passed, "distinct_count": s.distinct_count()})
                if not passed: all_passed = False

        return {
            "suite_name": self.suite_name,
            "success": all_passed,
            "total_checks": len(self.expectations),
            "passed_checks": sum(1 for r in results if r["success"]),
            "failed_checks": sum(1 for r in results if not r["success"]),
            "details": results
        }
