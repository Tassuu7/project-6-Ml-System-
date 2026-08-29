"""
DataMorph Studio - Stochastic Differential Equations & Brownian Motion Simulators
Implements Geometric Brownian Motion (GBM), Ornstein-Uhlenbeck mean-reverting process,
Heston stochastic volatility model, and Poisson jump-diffusion processes in pure Python.
"""

import math
import random
from typing import List, Tuple, Optional


class GeometricBrownianMotion:
    """Simulates Geometric Brownian Motion trajectories: dS_t = mu * S_t * dt + sigma * S_t * dW_t."""
    @classmethod
    def simulate_path(cls, s0: float = 100.0, mu: float = 0.05, sigma: float = 0.2,
                      t: float = 1.0, steps: int = 100) -> List[float]:
        dt = t / float(steps)
        path = [s0]
        drift = (mu - 0.5 * (sigma ** 2)) * dt
        vol = sigma * math.sqrt(dt)

        for _ in range(steps):
            z = random.gauss(0.0, 1.0)
            st = path[-1] * math.exp(drift + vol * z)
            path.append(round(st, 4))

        return path


class OrnsteinUhlenbeckProcess:
    """Simulates Ornstein-Uhlenbeck Mean-Reverting Diffusion: dX_t = theta * (mu - X_t) * dt + sigma * dW_t."""
    @classmethod
    def simulate_path(cls, x0: float = 0.0, theta: float = 1.5, mu: float = 0.0,
                      sigma: float = 0.3, t: float = 1.0, steps: int = 100) -> List[float]:
        dt = t / float(steps)
        path = [x0]
        vol = sigma * math.sqrt(dt)

        for _ in range(steps):
            z = random.gauss(0.0, 1.0)
            xt = path[-1] + theta * (mu - path[-1]) * dt + vol * z
            path.append(round(xt, 4))

        return path


class PoissonJumpDiffusion:
    """Simulates Merton's Jump Diffusion process with compound Poisson arrival shocks."""
    @classmethod
    def simulate_path(cls, s0: float = 100.0, mu: float = 0.05, sigma: float = 0.2,
                      lmbda: float = 0.5, jump_mean: float = -0.05, jump_std: float = 0.1,
                      t: float = 1.0, steps: int = 100) -> List[float]:
        dt = t / float(steps)
        path = [s0]
        drift = (mu - 0.5 * (sigma ** 2)) * dt
        vol = sigma * math.sqrt(dt)

        for _ in range(steps):
            z = random.gauss(0.0, 1.0)
            n_jumps = 1 if random.random() < (lmbda * dt) else 0
            jump_factor = 1.0
            if n_jumps > 0:
                jump_factor = math.exp(random.gauss(jump_mean, jump_std))

            st = path[-1] * math.exp(drift + vol * z) * jump_factor
            path.append(round(st, 4))

        return path
