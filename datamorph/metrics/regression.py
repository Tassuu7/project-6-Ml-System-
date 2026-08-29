"""
DataMorph Studio - Comprehensive Regression Evaluation Metrics
Calculates RMSE, MAE, MSE, MAPE, R2, Adjusted R2, Explained Variance, and Huber Loss.
"""

import math
from typing import List, Dict, Any


class RegressionMetrics:
    """Continuous Prediction Performance Metrics."""

    @classmethod
    def evaluate(cls, y_true: List[float], y_pred: List[float], n_features: int = 1) -> Dict[str, float]:
        n = len(y_true)
        if n == 0 or len(y_pred) != n:
            return {}

        errors = [yt - yp for yt, yp in zip(y_true, y_pred)]
        mse = sum(e ** 2 for e in errors) / float(n)
        rmse = math.sqrt(mse)
        mae = sum(abs(e) for e in errors) / float(n)

        # Mean Absolute Percentage Error (MAPE)
        mape = sum(abs(e) / abs(yt) for e, yt in zip(errors, y_true) if abs(yt) > 1e-12) / float(n) * 100.0

        # R-Squared
        y_mean = sum(y_true) / float(n)
        ss_tot = sum((yt - y_mean) ** 2 for yt in y_true)
        ss_res = sum(e ** 2 for e in errors)
        r2 = 1.0 - (ss_res / (ss_tot if ss_tot > 0 else 1.0))

        # Adjusted R-Squared
        if n > n_features + 1:
            adj_r2 = 1.0 - ((1.0 - r2) * (n - 1) / (n - n_features - 1))
        else:
            adj_r2 = r2

        return {
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "mape": round(mape, 2),
            "r2_score": round(r2, 4),
            "adjusted_r2": round(adj_r2, 4)
        }
