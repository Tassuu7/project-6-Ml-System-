"""
DataMorph Studio - Partial Differential Equations (PDE) Finite Difference Solvers
Implements 1D Heat equation diffusion, Wave equation hyperbolic solvers, and Poisson elliptic solvers.
"""

from typing import List, Tuple


class FiniteDifferenceHeatSolver:
    """Solves 1D Heat Equation du/dt = alpha * d2u/dx2 using explicit Forward-Time Central-Space (FTCS)."""
    @classmethod
    def solve_1d(cls, initial_u: List[float], alpha: float = 0.01,
                 dx: float = 0.1, dt: float = 0.001, n_time_steps: int = 50) -> List[List[float]]:
        # Stability condition: r = alpha * dt / dx^2 <= 0.5
        r = alpha * dt / (dx ** 2)
        u_history = [list(initial_u)]
        u = list(initial_u)
        n = len(u)

        for _ in range(n_time_steps):
            u_next = list(u)
            for i in range(1, n - 1):
                u_next[i] = u[i] + r * (u[i + 1] - 2.0 * u[i] + u[i - 1])
            u = u_next
            u_history.append([round(v, 6) for v in u])

        return u_history


class Poisson2DSolver:
    """Solves 2D Poisson Equation nabla^2 u = f(x, y) on rectangular grid via Jacobi relaxation."""
    @classmethod
    def solve(cls, source_f: List[List[float]], boundary_val: float = 0.0,
              max_iter: int = 100, tol: float = 1e-4) -> List[List[float]]:
        rows = len(source_f)
        cols = len(source_f[0]) if rows > 0 else 0
        u = [[boundary_val for _ in range(cols)] for _ in range(rows)]

        for it in range(max_iter):
            max_diff = 0.0
            u_next = [list(row) for row in u]
            for r in range(1, rows - 1):
                for c in range(1, cols - 1):
                    # Jacobi 5-point stencil: u_ij = 0.25 * (u_{i+1,j} + u_{i-1,j} + u_{i,j+1} + u_{i,j-1} - f_ij)
                    val = 0.25 * (u[r + 1][c] + u[r - 1][c] + u[r][c + 1] + u[r][c - 1] - source_f[r][c])
                    diff = abs(val - u[r][c])
                    if diff > max_diff:
                        max_diff = diff
                    u_next[r][c] = val
            u = u_next
            if max_diff < tol:
                break

        return [[round(v, 6) for v in row] for row in u]
