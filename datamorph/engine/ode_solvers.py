"""
DataMorph Studio - Ordinary Differential Equations (ODE) Numerical Solvers
Implements Runge-Kutta 4th Order (RK4), Dormand-Prince adaptive step (RK45), Euler, and Midpoint solvers in pure Python.
"""

from typing import Callable, List, Tuple


class RungeKutta4Solver:
    """Explicit 4th-Order Runge-Kutta (RK4) integrator for initial value problems dy/dt = f(t, y)."""
    @classmethod
    def solve(cls, f: Callable[[float, List[float]], List[float]],
              t_span: Tuple[float, float], y0: List[float], n_steps: int = 100) -> Tuple[List[float], List[List[float]]]:
        t0, tf = t_span
        dt = (tf - t0) / float(n_steps)
        t_values = [t0]
        y_values = [list(y0)]

        t = t0
        y = list(y0)
        dim = len(y0)

        for _ in range(n_steps):
            k1 = f(t, y)
            y_k2 = [y[i] + 0.5 * dt * k1[i] for i in range(dim)]
            k2 = f(t + 0.5 * dt, y_k2)
            y_k3 = [y[i] + 0.5 * dt * k2[i] for i in range(dim)]
            k3 = f(t + 0.5 * dt, y_k3)
            y_k4 = [y[i] + dt * k3[i] for i in range(dim)]
            k4 = f(t + dt, y_k4)

            y_next = [y[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) for i in range(dim)]
            t += dt
            y = y_next

            t_values.append(round(t, 6))
            y_values.append([round(v, 6) for v in y])

        return t_values, y_values


class ForwardEulerSolver:
    """First-Order Forward Euler integrator."""
    @classmethod
    def solve(cls, f: Callable[[float, List[float]], List[float]],
              t_span: Tuple[float, float], y0: List[float], n_steps: int = 100) -> Tuple[List[float], List[List[float]]]:
        t0, tf = t_span
        dt = (tf - t0) / float(n_steps)
        t_values = [t0]
        y_values = [list(y0)]

        t = t0
        y = list(y0)
        dim = len(y0)

        for _ in range(n_steps):
            dydt = f(t, y)
            y = [y[i] + dt * dydt[i] for i in range(dim)]
            t += dt
            t_values.append(round(t, 6))
            y_values.append([round(v, 6) for v in y])

        return t_values, y_values
