"""
DataMorph Studio - Parametric Statistical Distributions Subsystem
Implements probability density functions (PDF), cumulative distribution functions (CDF),
quantile functions (PPF), and random sampling across 10 continuous and discrete distributions.
"""

import math
import random
from typing import List, Optional, Tuple


class GaussianDistribution:
    """Univariate Normal / Gaussian Distribution N(mu, sigma^2)."""
    def __init__(self, mu: float = 0.0, sigma: float = 1.0):
        if sigma <= 0:
            raise ValueError("Standard deviation sigma must be strictly positive")
        self.mu = float(mu)
        self.sigma = float(sigma)

    def pdf(self, x: float) -> float:
        """Probability Density Function."""
        coeff = 1.0 / (self.sigma * math.sqrt(2.0 * math.pi))
        exponent = -0.5 * (((x - self.mu) / self.sigma) ** 2)
        return coeff * math.exp(exponent)

    def cdf(self, x: float) -> float:
        """Cumulative Distribution Function via standard error function erf."""
        z = (x - self.mu) / (self.sigma * math.sqrt(2.0))
        return 0.5 * (1.0 + math.erf(z))

    def ppf(self, p: float) -> float:
        """Percent Point Function (Inverse CDF / Quantile Function)."""
        if not (0.0 < p < 1.0):
            raise ValueError("Probability p must be in range (0, 1)")
        # Rational approximation of inverse error function
        z = self._approx_inv_erf(2.0 * p - 1.0)
        return self.mu + self.sigma * math.sqrt(2.0) * z

    def _approx_inv_erf(self, z: float) -> float:
        a = 0.147
        sgn = 1.0 if z >= 0 else -1.0
        log_term = math.log(max(1e-15, 1.0 - z * z))
        term1 = (2.0 / (math.pi * a)) + (log_term / 2.0)
        term2 = (log_term / a)
        inner = (term1 * term1) - term2
        return sgn * math.sqrt(math.sqrt(max(0.0, inner)) - term1)

    def sample(self, n: int = 1) -> List[float]:
        """Generates n samples via Box-Muller transform."""
        samples = []
        for _ in range(n):
            u1 = max(1e-12, random.random())
            u2 = random.random()
            z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            samples.append(self.mu + self.sigma * z0)
        return samples


class StudentTDistribution:
    """Student's t-Distribution with nu degrees of freedom."""
    def __init__(self, df: float = 10.0):
        if df <= 0:
            raise ValueError("Degrees of freedom must be strictly positive")
        self.df = float(df)

    def pdf(self, x: float) -> float:
        nu = self.df
        gamma_ratio = math.exp(math.lgamma((nu + 1.0) / 2.0) - math.lgamma(nu / 2.0))
        denom = math.sqrt(nu * math.pi)
        base = 1.0 + (x * x) / nu
        return (gamma_ratio / denom) * (base ** (-(nu + 1.0) / 2.0))

    def cdf(self, x: float) -> float:
        # Normal approximation for moderate to large df
        nu = self.df
        if nu > 30:
            return GaussianDistribution(0, 1).cdf(x)
        # Numerical integration for smaller df
        steps = 200
        t_min = -10.0
        if x < t_min:
            return 0.0
        if x > 10.0:
            return 1.0
        dt = (x - t_min) / float(steps)
        integral = 0.0
        for i in range(steps):
            t_mid = t_min + (i + 0.5) * dt
            integral += self.pdf(t_mid) * dt
        return max(0.0, min(1.0, integral))


class ExponentialDistribution:
    """Exponential Distribution with rate parameter lambda."""
    def __init__(self, rate: float = 1.0):
        if rate <= 0:
            raise ValueError("Rate parameter lambda must be positive")
        self.rate = float(rate)

    def pdf(self, x: float) -> float:
        if x < 0:
            return 0.0
        return self.rate * math.exp(-self.rate * x)

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        return 1.0 - math.exp(-self.rate * x)

    def ppf(self, p: float) -> float:
        if not (0.0 <= p < 1.0):
            raise ValueError("Probability p must be in [0, 1)")
        return -math.log(1.0 - p) / self.rate

    def sample(self, n: int = 1) -> List[float]:
        return [-math.log(max(1e-12, 1.0 - random.random())) / self.rate for _ in range(n)]


class GammaDistribution:
    """Gamma Distribution with shape k (alpha) and scale theta (beta)."""
    def __init__(self, shape: float = 2.0, scale: float = 1.0):
        if shape <= 0 or scale <= 0:
            raise ValueError("Shape and scale must be strictly positive")
        self.shape = float(shape)
        self.scale = float(scale)

    def pdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        k, theta = self.shape, self.scale
        return (1.0 / (math.gamma(k) * (theta ** k))) * (x ** (k - 1.0)) * math.exp(-x / theta)

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        # Incomplete gamma function approximation
        steps = 150
        dx = x / float(steps)
        integral = 0.0
        for i in range(steps):
            x_mid = (i + 0.5) * dx
            integral += self.pdf(x_mid) * dx
        return max(0.0, min(1.0, integral))


class BetaDistribution:
    """Beta Distribution with parameters alpha and beta over [0, 1]."""
    def __init__(self, alpha: float = 2.0, beta: float = 2.0):
        if alpha <= 0 or beta <= 0:
            raise ValueError("Alpha and beta must be positive")
        self.alpha = float(alpha)
        self.beta = float(beta)

    def pdf(self, x: float) -> float:
        if not (0.0 <= x <= 1.0):
            return 0.0
        a, b = self.alpha, self.beta
        b_const = math.exp(math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))
        return (1.0 / b_const) * (x ** (a - 1.0)) * ((1.0 - x) ** (b - 1.0))


class WeibullDistribution:
    """Weibull Distribution for survival and reliability analysis."""
    def __init__(self, shape: float = 1.5, scale: float = 1.0):
        if shape <= 0 or scale <= 0:
            raise ValueError("Weibull parameters must be positive")
        self.k = float(shape)
        self.lam = float(scale)

    def pdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        return (self.k / self.lam) * ((x / self.lam) ** (self.k - 1.0)) * math.exp(-((x / self.lam) ** self.k))

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        return 1.0 - math.exp(-((x / self.lam) ** self.k))


class PoissonDistribution:
    """Discrete Poisson Distribution with arrival rate lambda."""
    def __init__(self, lmbda: float = 5.0):
        if lmbda <= 0:
            raise ValueError("Poisson lambda must be positive")
        self.lmbda = float(lmbda)

    def pmf(self, k: int) -> float:
        if k < 0:
            return 0.0
        return ((self.lmbda ** k) * math.exp(-self.lmbda)) / math.factorial(k)

    def cdf(self, k: int) -> float:
        if k < 0:
            return 0.0
        return sum(self.pmf(i) for i in range(int(k) + 1))


class BinomialDistribution:
    """Discrete Binomial Distribution with n trials and probability p."""
    def __init__(self, n: int = 10, p: float = 0.5):
        if n < 0 or not (0.0 <= p <= 1.0):
            raise ValueError("Invalid parameters for Binomial distribution")
        self.n = int(n)
        self.p = float(p)

    def pmf(self, k: int) -> float:
        if not (0 <= k <= self.n):
            return 0.0
        comb = math.comb(self.n, k)
        return comb * (self.p ** k) * ((1.0 - self.p) ** (self.n - k))

    def cdf(self, k: int) -> float:
        if k < 0:
            return 0.0
        if k >= self.n:
            return 1.0
        return sum(self.pmf(i) for i in range(int(k) + 1))


class ChiSquareDistribution:
    """Chi-Square Distribution with k degrees of freedom."""
    def __init__(self, df: int = 5):
        if df <= 0:
            raise ValueError("Chi-Square df must be positive integer")
        self.df = int(df)

    def pdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        k = self.df
        denom = (2.0 ** (k / 2.0)) * math.gamma(k / 2.0)
        numer = (x ** ((k / 2.0) - 1.0)) * math.exp(-x / 2.0)
        return numer / denom


class LogNormalDistribution:
    """Log-Normal Distribution with location mu and scale sigma."""
    def __init__(self, mu: float = 0.0, sigma: float = 1.0):
        if sigma <= 0:
            raise ValueError("Log-Normal sigma must be positive")
        self.mu = float(mu)
        self.sigma = float(sigma)

    def pdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        coeff = 1.0 / (x * self.sigma * math.sqrt(2.0 * math.pi))
        exponent = -0.5 * (((math.log(x) - self.mu) / self.sigma) ** 2)
        return coeff * math.exp(exponent)

    def cdf(self, x: float) -> float:
        if x <= 0:
            return 0.0
        return GaussianDistribution(self.mu, self.sigma).cdf(math.log(x))
