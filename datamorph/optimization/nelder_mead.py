"""
DataMorph Studio - Nelder-Mead Downhill Simplex Optimization Algorithm
Derivative-free geometric simplex search for noisy, non-differentiable objectives.
"""

from typing import Callable, List, Tuple


class NelderMeadSimplexOptimizer:
    """Derivative-Free Nelder-Mead Simplex Optimizer."""
    def __init__(self, alpha: float = 1.0, gamma: float = 2.0,
                 rho: float = 0.5, sigma: float = 0.5,
                 max_iter: int = 200, tol: float = 1e-5):
        self.alpha = alpha  # Reflection
        self.gamma = gamma  # Expansion
        self.rho = rho      # Contraction
        self.sigma = sigma  # Shrink
        self.max_iter = max_iter
        self.tol = tol

    def optimize(self, loss_fn: Callable[[List[float]], float],
                 initial_point: List[float]) -> Tuple[List[float], float, int]:
        n = len(initial_point)
        # Initialize simplex of n+1 vertices
        simplex = [list(initial_point)]
        for i in range(n):
            pt = list(initial_point)
            pt[i] += 0.05 if pt[i] != 0 else 0.00025
            simplex.append(pt)

        for iteration in range(self.max_iter):
            # Evaluate objective at each vertex
            scored = sorted([(pt, loss_fn(pt)) for pt in simplex], key=lambda item: item[1])
            simplex = [item[0] for item in scored]
            scores = [item[1] for item in scored]

            if abs(scores[-1] - scores[0]) < self.tol:
                break

            # Centroid of best n points
            centroid = [0.0] * n
            for i in range(n):
                for j in range(n):
                    centroid[j] += simplex[i][j] / n

            # Reflection
            xr = [centroid[j] + self.alpha * (centroid[j] - simplex[-1][j]) for j in range(n)]
            fr = loss_fn(xr)

            if scores[0] <= fr < scores[-2]:
                simplex[-1] = xr
                continue

            # Expansion
            if fr < scores[0]:
                xe = [centroid[j] + self.gamma * (xr[j] - centroid[j]) for j in range(n)]
                fe = loss_fn(xe)
                simplex[-1] = xe if fe < fr else xr
                continue

            # Contraction
            xc = [centroid[j] + self.rho * (simplex[-1][j] - centroid[j]) for j in range(n)]
            fc = loss_fn(xc)
            if fc < scores[-1]:
                simplex[-1] = xc
                continue

            # Shrink
            for i in range(1, n + 1):
                simplex[i] = [simplex[0][j] + self.sigma * (simplex[i][j] - simplex[0][j]) for j in range(n)]

        return simplex[0], scores[0], iteration + 1
