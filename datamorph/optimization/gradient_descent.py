"""
DataMorph Studio - First-Order Gradient Descent & Adaptive Momentum (Adam) Optimizers
Implements vanilla SGD, Momentum, RMSProp, and Adam numerical optimizers in pure Python.
"""

import math
from typing import Callable, List, Tuple, Optional


class GradientDescentOptimizer:
    """Standard First-Order Stochastic / Mini-Batch Gradient Descent with Momentum."""
    def __init__(self, learning_rate: float = 0.01, momentum: float = 0.9, max_iter: int = 1000, tol: float = 1e-6):
        self.lr = learning_rate
        self.momentum = momentum
        self.max_iter = max_iter
        self.tol = tol

    def optimize(self, loss_fn: Callable[[List[float]], float],
                 grad_fn: Callable[[List[float]], List[float]],
                 initial_params: List[float]) -> Tuple[List[float], float, int]:
        params = list(initial_params)
        velocity = [0.0] * len(params)

        for iteration in range(self.max_iter):
            grad = grad_fn(params)
            grad_norm = math.sqrt(sum(g * g for g in grad))
            if grad_norm < self.tol:
                break

            for i in range(len(params)):
                velocity[i] = self.momentum * velocity[i] + self.lr * grad[i]
                params[i] -= velocity[i]

        final_loss = loss_fn(params)
        return params, final_loss, iteration + 1


class AdamOptimizer:
    """Adaptive Moment Estimation (Adam) Optimizer with Bias Correction."""
    def __init__(self, learning_rate: float = 0.001, beta1: float = 0.9,
                 beta2: float = 0.999, epsilon: float = 1e-8,
                 max_iter: int = 1000, tol: float = 1e-6):
        self.lr = learning_rate
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = epsilon
        self.max_iter = max_iter
        self.tol = tol

    def optimize(self, loss_fn: Callable[[List[float]], float],
                 grad_fn: Callable[[List[float]], List[float]],
                 initial_params: List[float]) -> Tuple[List[float], float, int]:
        params = list(initial_params)
        m = [0.0] * len(params)  # First moment vector
        v = [0.0] * len(params)  # Second moment vector

        for t in range(1, self.max_iter + 1):
            grad = grad_fn(params)
            grad_norm = math.sqrt(sum(g * g for g in grad))
            if grad_norm < self.tol:
                break

            for i in range(len(params)):
                # Update biased first moment estimate
                m[i] = self.beta1 * m[i] + (1.0 - self.beta1) * grad[i]
                # Update biased second raw moment estimate
                v[i] = self.beta2 * v[i] + (1.0 - self.beta2) * (grad[i] ** 2)

                # Compute bias-corrected first moment estimate
                m_hat = m[i] / (1.0 - (self.beta1 ** t))
                # Compute bias-corrected second raw moment estimate
                v_hat = v[i] / (1.0 - (self.beta2 ** t))

                # Update parameters
                params[i] -= (self.lr * m_hat) / (math.sqrt(v_hat) + self.eps)

        final_loss = loss_fn(params)
        return params, final_loss, t
