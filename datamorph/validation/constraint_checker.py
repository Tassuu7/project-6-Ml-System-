"""
DataMorph Studio - Schema Constraint Checker
Enforces business domain rules and multi-column integrity constraints.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame


class ConstraintChecker:
    def check_constraints(self, df: DataFrame, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        violations = []
        for rule in rules:
            rule_name = rule.get("name", "UnnamedConstraint")
            col1 = rule.get("col1")
            col2 = rule.get("col2")
            op = rule.get("operator", "<=")

            if col1 in df.columns and col2 in df.columns:
                records = df.to_dict_records()
                for idx, r in enumerate(records):
                    try:
                        v1 = float(r[col1])
                        v2 = float(r[col2])
                        if op == "<=" and not (v1 <= v2):
                            violations.append({"rule": rule_name, "row": idx, "val1": v1, "val2": v2})
                        elif op == ">=" and not (v1 >= v2):
                            violations.append({"rule": rule_name, "row": idx, "val1": v1, "val2": v2})
                    except Exception:
                        pass

        return {
            "total_rules": len(rules),
            "violation_count": len(violations),
            "violations": violations[:50]
        }
