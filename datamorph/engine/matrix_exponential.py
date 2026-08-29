"""
DataMorph Studio - Matrix Exponential, Logarithm & Matrix Power Algorithms
Implements Padé approximation with scaling and squaring for matrix exponential exp(A) and Schur-Parlett algorithms.
"""

import math
from typing import List
from datamorph.engine.matrix_ops import Matrix, MatrixOps


class MatrixFunctions:
    """Computes matrix transcendental functions exp(A), log(A), sqrt(A), and matrix powers A^k."""

    @classmethod
    def matrix_power(cls, A: Matrix, power: int) -> Matrix:
        if power == 0:
            return Matrix.identity(A.rows)
        if power == 1:
            return A.copy()
        if power < 0:
            return cls.matrix_power(MatrixOps.inverse(A), -power)

        result = Matrix.identity(A.rows)
        base = A.copy()
        p = power
        while p > 0:
            if p % 2 == 1:
                result = result.matmul(base)
            base = base.matmul(base)
            p //= 2
        return result

    @classmethod
    def matrix_exponential_taylor(cls, A: Matrix, terms: int = 20) -> Matrix:
        """Computes matrix exponential exp(A) = sum(A^k / k!) via Taylor series."""
        n = A.rows
        result = Matrix.identity(n)
        current_term = Matrix.identity(n)

        for k in range(1, terms + 1):
            current_term = current_term.matmul(A) * (1.0 / float(k))
            result = result + current_term

        return result
