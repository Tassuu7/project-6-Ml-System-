"""
DataMorph Studio - Broyden-Fletcher-Goldfarb-Shanno (BFGS) Quasi-Newton Optimizer
Approximates the inverse Hessian matrix iteratively without explicit second-derivative evaluation.
"""

import math
from typing import Callable, List, Tuple
from datamorph.engine.matrix_ops import Matrix, Vector


class BFGSOptimizer:
    """Quasi-Newton BFGS Optimizer with Line Search."""
    def __init__(self, max_iter: int = 100, tol: float = 1e-6):
        self.max_iter = max_iter
        self.tol = tol

    def optimize(self, loss_fn: Callable[[List[float]], float],
                 grad_fn: Callable[[List[float]], List[float]],
                 initial_params: List[float]) -> Tuple[List[float], float, int]:
        x = Vector(initial_params)
        n = len(x)
        # Initial inverse Hessian approximation is Identity
        H = Matrix.identity(n)

        for iteration in range(self.max_iter):
            grad = Vector(grad_fn(x.to_list()))
            if grad.norm(2) < self.tol:
                break

            # Search direction p = -H * grad
            p = H.dot_vector(-grad)

            # Backtracking line search
            alpha = 1.0
            c1 = 1e-4
            rho = 0.5
            fx = loss_fn(x.to_list())
            while loss_fn((x + alpha * p).to_list()) > fx + c1 * alpha * grad.dot(p):
                alpha *= rho
                if alpha < 1e-8:
                    break

            s = alpha * p
            x_next = x + s
            grad_next = Vector(grad_fn(x_next.to_list()))
            y = grad_next - grad

            ys = y.dot(s)
            if abs(ys) > 1e-10:
                # BFGS update formula for H
                I = Matrix.identity(n)
                # rho_k = 1 / (y^T * s)
                rho_k = 1.0 / ys
                # V = I - rho_k * s * y^T
                V = Matrix.zeros(n, n)
                for i in range(n):
                    for j in range(n):
                        V.data[i][j] = (1.0 if i == j else 0.0) - rho_k * s[i] * y[j]
                # H_{k+1} = V * H_k * V^T + rho_k * s * s^T
                H_new = V.matmul(H).matmul(V.transpose())
                for i in range(n):
                    for j in range(n):
                        H_new.data[i][j] += rho_k * s[i] * s[j]
                H = H_new

            x = x_next

        final_loss = loss_fn(x.to_list())
        return x.to_list(), final_loss, iteration + 1
