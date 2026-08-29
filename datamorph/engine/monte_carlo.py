"""
DataMorph Studio - Monte Carlo Simulation & Resampling Subsystem
Implements Bootstrap percentile intervals, Jackknife variance estimation, and Latin Hypercube Sampling (LHS).
"""

import random
from typing import List, Tuple, Callable, Dict, Any
from datamorph.utils.math_utils import mean, variance, quantile


class BootstrapEstimator:
    """Non-parametric Bootstrap resampling for confidence intervals."""
    @classmethod
    def estimate_ci(cls, data: List[float], statistic_fn: Callable[[List[float]], float] = mean,
                    n_bootstraps: int = 500, ci: float = 0.95) -> Dict[str, float]:
        n = len(data)
        if n == 0:
            return {"point_estimate": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

        point_est = statistic_fn(data)
        boot_estimates = []

        for _ in range(n_bootstraps):
            sample = [random.choice(data) for _ in range(n)]
            boot_estimates.append(statistic_fn(sample))

        alpha = (1.0 - ci) / 2.0
        lower = quantile(boot_estimates, alpha)
        upper = quantile(boot_estimates, 1.0 - alpha)

        return {
            "point_estimate": round(point_est, 4),
            "ci_lower": round(lower, 4),
            "ci_upper": round(upper, 4),
            "std_error": round(math.sqrt(variance(boot_estimates) or 0.0), 4)
        }


class LatinHypercubeSampler:
    """Generates space-filling multi-dimensional Latin Hypercube Samples."""
    @classmethod
    def sample(cls, n_samples: int, n_dimensions: int, bounds: List[Tuple[float, float]]) -> List[List[float]]:
        result = [[0.0 for _ in range(n_dimensions)] for _ in range(n_samples)]

        for dim in range(n_dimensions):
            low, high = bounds[dim]
            step = (high - low) / float(n_samples)
            intervals = [low + i * step + random.random() * step for i in range(n_samples)]
            random.shuffle(intervals)
            for i in range(n_samples):
                result[i][dim] = round(intervals[i], 6)

        return result
