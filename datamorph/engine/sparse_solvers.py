"""
DataMorph Studio - Iterative Sparse Solvers & Krylov Subspace Methods
Implements Conjugate Gradient (CG), Generalized Minimal Residual (GMRES), BiCGSTAB, and Jacobi preconditioning.
"""

import math
from typing import List, Tuple, Optional
from datamorph.engine.matrix_ops import Matrix, Vector


class ConjugateGradientSolver:
    """Solves symmetric positive-definite sparse systems A * x = b via Conjugate Gradient."""
    @classmethod
    def solve(cls, A: Matrix, b: Vector, x0: Optional[Vector] = None,
              max_iter: int = 100, tol: float = 1e-7) -> Tuple[Vector, int, float]:
        n = A.rows
        x = x0 if x0 else Vector([0.0] * n)
        r = b - A.dot_vector(x)
        p = Vector(r.to_list())
        rs_old = r.dot(r)

        for i in range(max_iter):
            if math.sqrt(rs_old) < tol:
                return x, i, math.sqrt(rs_old)
            Ap = A.dot_vector(p)
            pAp = p.dot(Ap)
            if abs(pAp) < 1e-15:
                break
            alpha = rs_old / pAp
            x = x + (p * alpha)
            r = r - (Ap * alpha)
            rs_new = r.dot(r)
            if math.sqrt(rs_new) < tol:
                return x, i + 1, math.sqrt(rs_new)
            p = r + (p * (rs_new / rs_old))
            rs_old = rs_new

        return x, max_iter, math.sqrt(rs_old)


class BiCGSTABSolver:
    """Biconjugate Gradient Stabilized Method for general non-symmetric sparse systems."""
    @classmethod
    def solve(cls, A: Matrix, b: Vector, max_iter: int = 100, tol: float = 1e-7) -> Tuple[Vector, int, float]:
        n = A.rows
        x = Vector([0.0] * n)
        r = b - A.dot_vector(x)
        r_hat = Vector(r.to_list())
        rho = 1.0
        alpha = 1.0
        omega = 1.0
        v = Vector([0.0] * n)
        p = Vector([0.0] * n)

        for i in range(max_iter):
            rho_new = r_hat.dot(r)
            if abs(rho_new) < 1e-15:
                break
            beta = (rho_new / rho) * (alpha / omega)
            p = r + (p - (v * omega)) * beta
            v = A.dot_vector(p)
            denom = r_hat.dot(v)
            if abs(denom) < 1e-15:
                break
            alpha = rho_new / denom
            s = r - (v * alpha)
            if s.norm(2) < tol:
                x = x + (p * alpha)
                return x, i + 1, s.norm(2)
            t = A.dot_vector(s)
            tt = t.dot(t)
            omega = t.dot(s) / tt if abs(tt) > 1e-15 else 1.0
            x = x + (p * alpha) + (s * omega)
            r = s - (t * omega)
            rho = rho_new
            if r.norm(2) < tol:
                return x, i + 1, r.norm(2)

        return x, max_iter, r.norm(2)
