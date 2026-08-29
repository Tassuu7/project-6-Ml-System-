"""
DataMorph Studio - Multicollinearity & Variance Inflation Factor (VIF) Calculator
Identifies severe multi-collinear dependencies among continuous feature subspaces.
"""

from typing import Dict, List
from datamorph.core.dataframe import DataFrame
from datamorph.engine.matrix_ops import Matrix, Vector, MatrixOps


class CollinearityVIFCalculator:
    """Calculates Variance Inflation Factors (VIF = 1 / (1 - R_i^2)) for numerical features."""

    @classmethod
    def calculate_vif(cls, df: DataFrame, columns: List[str] = None) -> Dict[str, float]:
        target_cols = columns or df.numeric_columns()
        if len(target_cols) < 2:
            return {c: 1.0 for c in target_cols}

        vif_scores = {}
        records = df.to_dict_records()

        # Build design matrix X
        for target_idx, target_col in enumerate(target_cols):
            predictor_cols = [c for c in target_cols if c != target_col]
            y = [float(r[target_col]) if r[target_col] is not None else 0.0 for r in records]
            
            # Linear regression: y ~ X_pred
            n = len(records)
            m = len(predictor_cols)
            X_data = []
            for r in records:
                row = [1.0]  # Intercept
                for c in predictor_cols:
                    row.append(float(r[c]) if r[c] is not None else 0.0)
                X_data.append(row)

            X = Matrix(X_data)
            Y = Vector(y)

            try:
                XtX = X.transpose().matmul(X)
                # Regularize
                for k in range(m + 1):
                    XtX.data[k][k] += 1e-4
                XtY = X.transpose().dot_vector(Y)
                beta = MatrixOps.solve_linear_system(XtX, XtY)
                y_hat = X.dot_vector(beta)

                # Compute R-squared
                y_mean = sum(y) / max(1, n)
                ss_tot = sum((val - y_mean) ** 2 for val in y)
                ss_res = sum((y[i] - y_hat[i]) ** 2 for i in range(n))
                r_squared = max(0.0, min(0.9999, 1.0 - (ss_res / (ss_tot if ss_tot > 0 else 1.0))))
                vif = 1.0 / (1.0 - r_squared)
                vif_scores[target_col] = round(vif, 2)
            except Exception:
                vif_scores[target_col] = 1.0

        return vif_scores
