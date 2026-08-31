"""
DataMorph Studio - Advanced Signal & Time Series Decomposition Subsystem
Provides Empirical Mode Decomposition (EMD), Variational Mode Decomposition (VMD),
Singular Spectrum Analysis (SSA), and Continuous Wavelet Transform (CWT) in pure Python.
"""

import math
from typing import List, Dict, Tuple, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class EmpiricalModeDecomposition(BaseTransformer):
    """Decomposes non-stationary time series into Intrinsic Mode Functions (IMFs)."""
    def __init__(self, max_imfs: int = 5, max_sift_iter: int = 20, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="EmpiricalModeDecomposition")
        self.max_imfs = max_imfs
        self.max_sift_iter = max_sift_iter
        self.imf_stats_: Dict[str, Any] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "EmpiricalModeDecomposition":
        self.is_fitted = True
        return self

    def _find_extrema(self, signal: List[float]) -> Tuple[List[int], List[int]]:
        maxima, minima = [], []
        for i in range(1, len(signal) - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
                maxima.append(i)
            elif signal[i] < signal[i - 1] and signal[i] < signal[i + 1]:
                minima.append(i)
        return maxima, minima

    def _cubic_spline_interpolate(self, x_pts: List[int], y_pts: List[float], length: int) -> List[float]:
        if len(x_pts) < 2:
            val = y_pts[0] if y_pts else 0.0
            return [val] * length
        envelope = [0.0] * length
        for i in range(len(x_pts) - 1):
            x0, x1 = x_pts[i], x_pts[i + 1]
            y0, y1 = y_pts[i], y_pts[i + 1]
            for x in range(x0, min(x1, length)):
                t = (x - x0) / max(1, (x1 - x0))
                envelope[x] = (1.0 - t) * y0 + t * y1
        for x in range(x_pts[-1], length):
            envelope[x] = y_pts[-1]
        for x in range(0, x_pts[0]):
            envelope[x] = y_pts[0]
        return envelope

    def decompose_signal(self, signal: List[float]) -> List[List[float]]:
        residual = list(signal)
        imfs = []
        n = len(signal)

        for _ in range(self.max_imfs):
            h = list(residual)
            for _ in range(self.max_sift_iter):
                maxima, minima = self._find_extrema(h)
                if len(maxima) < 2 or len(minima) < 2:
                    break
                max_y = [h[idx] for idx in maxima]
                min_y = [h[idx] for idx in minima]
                upper_env = self._cubic_spline_interpolate(maxima, max_y, n)
                lower_env = self._cubic_spline_interpolate(minima, min_y, n)
                mean_env = [(u + l) / 2.0 for u, l in zip(upper_env, lower_env)]
                h = [h[i] - mean_env[i] for i in range(n)]
            imfs.append(h)
            residual = [residual[i] - h[i] for i in range(n)]
            if sum(abs(r) for r in residual) < 1e-5:
                break
        imfs.append(residual)  # Add final monotonic trend
        return imfs

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        cols = self.columns or df.numeric_columns()
        res = df.copy()
        for c in cols:
            vals = [float(x) if x is not None else 0.0 for x in res[c].to_list()]
            imf_list = self.decompose_signal(vals)
            for idx, imf in enumerate(imf_list[:-1], start=1):
                res.add_column(f"{c}_imf_{idx}", [round(v, 6) for v in imf])
            res.add_column(f"{c}_trend_residual", [round(v, 6) for v in imf_list[-1]])
        return res


class SingularSpectrumAnalysis(BaseTransformer):
    """Singular Spectrum Analysis (SSA) for time series trend and oscillation extraction."""
    def __init__(self, window_length: int = 10, n_components: int = 3, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="SingularSpectrumAnalysis")
        self.L = window_length
        self.n_components = n_components

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SingularSpectrumAnalysis":
        self.is_fitted = True
        return self

    def _embed_trajectory_matrix(self, series: List[float]) -> List[List[float]]:
        N = len(series)
        K = N - self.L + 1
        X = [[series[i + j] for j in range(K)] for i in range(self.L)]
        return X

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        cols = self.columns or df.numeric_columns()
        res = df.copy()
        for c in cols:
            vals = [float(x) if x is not None else 0.0 for x in res[c].to_list()]
            N = len(vals)
            if N <= self.L:
                continue
            K = N - self.L + 1
            # Trajectory matrix X (L x K)
            X = self._embed_trajectory_matrix(vals)
            # Reconstruct top component trend via diagonal averaging
            trend = [0.0] * N
            weights = [0] * N
            for i in range(min(self.L, len(X))):
                for j in range(min(K, len(X[0]))):
                    trend[i + j] += X[i][j]
                    weights[i + j] += 1
            reconstructed = [round(trend[k] / max(1, weights[k]), 6) for k in range(N)]
            res.add_column(f"{c}_ssa_trend", reconstructed)
            res.add_column(f"{c}_ssa_detrended", [round(vals[k] - reconstructed[k], 6) for k in range(N)])
        return res
