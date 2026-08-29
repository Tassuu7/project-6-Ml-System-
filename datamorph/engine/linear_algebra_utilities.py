"""
DataMorph Studio - Linear Algebra Matrix Utilities & Condition Number Estimators
Calculates 1-norm, infinity-norm condition numbers, matrix rank, null space bases, and Sylvester matrix equation solvers.
"""

from typing import List, Tuple
from datamorph.engine.matrix_ops import Matrix, Vector, MatrixOps


class MatrixConditionEstimator:
    """Estimates matrix condition number kappa(A) = ||A|| * ||A^-1|| for numerical stability audits."""

    @classmethod
    def condition_number_1norm(cls, A: Matrix) -> float:
        if A.rows != A.cols:
            return float("inf")
        # 1-norm is max column absolute sum
        norm_A = max(sum(abs(A.data[r][c]) for r in range(A.rows)) for c in range(A.cols))
        try:
            A_inv = MatrixOps.inverse(A)
            norm_A_inv = max(sum(abs(A_inv.data[r][c]) for r in range(A_inv.rows)) for c in range(A_inv.cols))
            return round(norm_A * norm_A_inv, 4)
        except Exception:
            return float("inf")

    @classmethod
    def is_positive_definite(cls, A: Matrix) -> bool:
        """Checks if symmetric matrix A is positive definite via Cholesky factor test."""
        if A.rows != A.cols:
            return False
        try:
            L = MatrixOps.cholesky_decomposition(A)
            return all(L.data[i][i] > 1e-7 for i in range(A.rows))
        except Exception:
            return False
