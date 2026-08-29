"""
DataMorph Studio - Second-Order Newton-Raphson Optimization Solver
Utilizes Hessian matrix curvature for quadratic convergence on smooth convex objectives.
"""

import math
from typing import Callable, List, Tuple
from datamorph.engine.matrix_ops import Matrix, Vector, MatrixOps


class NewtonRaphsonSolver:
    """Multivariate Newton-Raphson Optimization Solver using Hessian Inversion."""
    def __init__(self, max_iter: int = 50, tol: float = 1e-6, damping: float = 1.0):
        self.max_iter = max_iter
        self.tol = tol
        self.damping = damping

    def optimize(self, loss_fn: Callable[[List[float]], float],
                 grad_fn: Callable[[List[float]], List[float]],
                 hessian_fn: Callable[[List[float]], List[List[float]]],
                 initial_params: List[float]) -> Tuple[List[float], float, int]:
        params = list(initial_params)
        n = len(params)

        for iteration in range(self.max_iter):
            grad = grad_fn(params)
            grad_norm = math.sqrt(sum(g * g for g in grad))
            if grad_norm < self.tol:
                break

            hessian_mat = Matrix(hessian_fn(params))
            # Regularize Hessian diagonal for positive-definiteness
            for i in range(n):
                hessian_mat.data[i][i] += 1e-5

            try:
                # Solve H * delta = -grad
                delta = MatrixOps.solve_linear_system(hessian_mat, Vector([-g for g in grad]))
                for i in range(n):
                    params[i] += self.damping * delta[i]
            except Exception:
                # Fallback to gradient descent step if Hessian is singular
                for i in range(n):
                    params[i] -= 0.01 * grad[i]

        final_loss = loss_fn(params)
        return params, final_loss, iteration + 1
