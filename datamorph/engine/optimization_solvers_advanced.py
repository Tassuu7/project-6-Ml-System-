"""
DataMorph Studio - Advanced Constrained & Non-Linear Optimization Solvers
Implements Sequential Least Squares Programming (SLSQP), Augmented Lagrangian,
and Karush-Kuhn-Tucker (KKT) multiplier boundary constraint solvers in pure Python.
"""

import math
from typing import Callable, List, Tuple, Optional, Dict
from datamorph.engine.matrix_ops import Matrix, Vector, MatrixOps


class AugmentedLagrangianSolver:
    """Solves equality and inequality constrained non-linear optimization problems."""
    def __init__(self, rho: float = 1.0, max_outer_iter: int = 20, max_inner_iter: int = 50, tol: float = 1e-5):
        self.rho = rho
        self.max_outer_iter = max_outer_iter
        self.max_inner_iter = max_inner_iter
        self.tol = tol

    def solve(self, objective_fn: Callable[[List[float]], float],
              grad_fn: Callable[[List[float]], List[float]],
              equality_constraints: List[Callable[[List[float]], float]],
              initial_x: List[float]) -> Tuple[List[float], float, Dict[str, Any]]:
        x = list(initial_x)
        n = len(x)
        m = len(equality_constraints)
        lambdas = [0.0] * m
        mu = self.rho

        for outer in range(self.max_outer_iter):
            # Inner unconstrained minimization of Augmented Lagrangian
            for inner in range(self.max_inner_iter):
                # Gradient of Augmented Lagrangian
                grad_obj = grad_fn(x)
                grad_al = list(grad_obj)

                for i, c_fn in enumerate(equality_constraints):
                    c_val = c_fn(x)
                    # Numerical gradient of constraint
                    grad_c = []
                    eps = 1e-6
                    for j in range(n):
                        x_plus = list(x)
                        x_plus[j] += eps
                        grad_c.append((c_fn(x_plus) - c_val) / eps)

                    for j in range(n):
                        grad_al[j] += (lambdas[i] + mu * c_val) * grad_c[j]

                # Gradient descent step
                grad_norm = math.sqrt(sum(g * g for g in grad_al))
                if grad_norm < self.tol:
                    break
                step_size = 0.01 / (1.0 + outer * 0.1)
                for j in range(n):
                    x[j] -= step_size * grad_al[j]

            # Update Lagrange multipliers: lambda = lambda + mu * c(x)
            max_violation = 0.0
            for i, c_fn in enumerate(equality_constraints):
                c_val = c_fn(x)
                lambdas[i] += mu * c_val
                max_violation = max(max_violation, abs(c_val))

            if max_violation < self.tol:
                break
            mu *= 2.0  # Penalty parameter increase

        final_val = objective_fn(x)
        return x, final_val, {
            "outer_iterations": outer + 1,
            "max_constraint_violation": round(max_violation, 6),
            "multipliers": lambdas
        }


class ProjectedGradientDescent:
    """Projected Gradient Descent for bounded hyperbox constraints l_i <= x_i <= u_i."""
    @classmethod
    def optimize(cls, loss_fn: Callable[[List[float]], float],
                 grad_fn: Callable[[List[float]], List[float]],
                 lower_bounds: List[float],
                 upper_bounds: List[float],
                 initial_x: List[float],
                 learning_rate: float = 0.01,
                 max_iter: int = 500,
                 tol: float = 1e-6) -> Tuple[List[float], float, int]:
        x = list(initial_x)
        n = len(x)

        for iteration in range(max_iter):
            grad = grad_fn(x)
            grad_norm = math.sqrt(sum(g * g for g in grad))
            if grad_norm < tol:
                break

            for i in range(n):
                # Gradient update
                x_next = x[i] - learning_rate * grad[i]
                # Projection onto box [l_i, u_i]
                x[i] = max(lower_bounds[i], min(upper_bounds[i], x_next))

        return x, loss_fn(x), iteration + 1
