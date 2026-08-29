"""
DataMorph Studio - Surrogate Feature Importance & Permutation Ranking
Ranks features by variance explained and mutual dependency with target feature.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame
from datamorph.engine.information_theory import MutualInformationCalculator


class SurrogateFeatureImportance:
    """Evaluates relative feature importance ranking without heavy ML model dependencies."""

    @classmethod
    def calculate_importance(cls, df: DataFrame, target_column: str) -> Dict[str, float]:
        if target_column not in df.columns:
            return {}

        target_vals = df[target_column].to_list()
        feature_cols = [c for c in df.columns if c != target_column]
        importance_scores = {}

        for col in feature_cols:
            col_vals = df[col].to_list()
            # Calculate mutual information with target
            mi = MutualInformationCalculator.calculate(col_vals, target_vals)
            importance_scores[col] = round(mi, 4)

        # Normalize to sum to 1.0
        total_mi = sum(importance_scores.values())
        if total_mi > 0:
            return {col: round(score / total_mi, 4) for col, score in sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)}
        return {col: round(1.0 / len(feature_cols), 4) for col in feature_cols}
