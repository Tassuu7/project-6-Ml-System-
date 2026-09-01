"""
DataMorph Studio - Smart Preprocessing Recommendations Engine
Analyzes dataset profiling metrics and formulates actionable, algorithmic transformation recommendations.
"""

from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame

class RecommendationsEngine:
    """Generates intelligent preprocessing recommendations based on actual dataset statistics."""

    @staticmethod
    def generate_recommendations(df: DataFrame) -> List[Dict[str, Any]]:
        recs = []
        n_rows, n_cols = df.shape
        if n_rows == 0:
            return recs

        # 1. Missing Values Analysis
        for col in df.columns:
            series = df[col]
            null_count = series.null_count()
            null_pct = round((null_count / float(n_rows)) * 100.0, 1)

            if null_pct > 0.0:
                is_numeric = col in df.numeric_columns()
                suggested_type = "SimpleImputer"
                strategy = "median" if is_numeric else "most_frequent"
                
                recs.append({
                    "id": f"rec_missing_{col}",
                    "severity": "high" if null_pct > 10.0 else "medium",
                    "column": col,
                    "issue_type": "Missing Values",
                    "issue_description": f"{null_pct}% missing values detected in '{col}' ({null_count}/{n_rows} rows).",
                    "recommendation": f"Apply {strategy.capitalize()} Imputation using {suggested_type}.",
                    "suggested_transformer": {
                        "name": f"Impute {col}",
                        "type": suggested_type,
                        "columns": [col],
                        "params": {"strategy": strategy}
                    }
                })

        # 2. Categorical High-Cardinality & Encoding
        for col in df.categorical_columns():
            series = df[col]
            n_unique = series.nunique()
            unique_ratio = n_unique / float(n_rows)

            if n_unique == n_rows and n_rows > 10:
                recs.append({
                    "id": f"rec_id_{col}",
                    "severity": "medium",
                    "column": col,
                    "issue_type": "Identifier Column",
                    "issue_description": f"Column '{col}' has 100% unique values and acts like an ID or primary key.",
                    "recommendation": "Drop this feature or use identifier hashing to prevent model overfitting.",
                    "suggested_transformer": {
                        "name": f"Drop {col}",
                        "type": "DropColumnTransformer",
                        "columns": [col],
                        "params": {}
                    }
                })
            elif n_unique > 15:
                recs.append({
                    "id": f"rec_card_{col}",
                    "severity": "medium",
                    "column": col,
                    "issue_type": "High Cardinality",
                    "issue_description": f"Categorical column '{col}' has {n_unique} distinct categories.",
                    "recommendation": "Use FrequencyEncoder or OrdinalEncoder instead of OneHotEncoder to avoid sparse matrix explosion.",
                    "suggested_transformer": {
                        "name": f"Freq Encode {col}",
                        "type": "FrequencyEncoder",
                        "columns": [col],
                        "params": {}
                    }
                })
            else:
                recs.append({
                    "id": f"rec_ohe_{col}",
                    "severity": "low",
                    "column": col,
                    "issue_type": "Categorical Feature",
                    "issue_description": f"Categorical column '{col}' has {n_unique} categories suitable for one-hot representation.",
                    "recommendation": "Encode using OneHotEncoder for linear/neural model compatibility.",
                    "suggested_transformer": {
                        "name": f"One-Hot {col}",
                        "type": "OneHotEncoder",
                        "columns": [col],
                        "params": {}
                    }
                })

        # 3. Numeric Scaling & Outlier Detection
        for col in df.numeric_columns():
            vals = df[col].values_numeric()
            if len(vals) > 5:
                v_min, v_max = min(vals), max(vals)
                # Check for extreme range / scaling need
                if (v_max - v_min) > 1000.0 or v_max > 500.0:
                    recs.append({
                        "id": f"rec_scale_{col}",
                        "severity": "medium",
                        "column": col,
                        "issue_type": "Unscaled Magnitude",
                        "issue_description": f"Large numerical scale detected on '{col}' (Range: [{v_min:g}, {v_max:g}]).",
                        "recommendation": "Apply StandardScaler or RobustScaler to normalize gradient variance.",
                        "suggested_transformer": {
                            "name": f"Scale {col}",
                            "type": "StandardScaler",
                            "columns": [col],
                            "params": {}
                        }
                    })

                # Check for zero variance / constant feature
                if v_min == v_max:
                    recs.append({
                        "id": f"rec_const_{col}",
                        "severity": "high",
                        "column": col,
                        "issue_type": "Constant Feature",
                        "issue_description": f"Column '{col}' has zero variance (all values = {v_min}).",
                        "recommendation": "Drop this constant column as it provides zero mutual information.",
                        "suggested_transformer": {
                            "name": f"Drop Constant {col}",
                            "type": "DropColumnTransformer",
                            "columns": [col],
                            "params": {}
                        }
                    })

        return recs
