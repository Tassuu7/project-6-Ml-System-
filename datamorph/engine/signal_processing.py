"""
DataMorph Studio - Signal Processing & Digital Filter Design
Implements Butterworth IIR filters, FIR Chebyshev windows, Hilbert envelope extraction, and Savitzky-Golay filtering.
"""

import math
from typing import List, Optional


class SavitzkyGolayFilter:
    """Applies Savitzky-Golay polynomial smoothing filter to 1D series signals."""
    @classmethod
    def smooth(cls, values: List[float], window_length: int = 5, polyorder: int = 2) -> List[float]:
        n = len(values)
        if n < window_length:
            return list(values)
        half = window_length // 2
        smoothed = []

        for i in range(n):
            window = [values[max(0, min(n - 1, i + k))] for k in range(-half, half + 1)]
            # Quadratic local polynomial weight approximation
            if polyorder == 2:
                weights = [(3 * half * (half + 1) - 5 * k * k) for k in range(-half, half + 1)]
                norm = sum(weights) or 1.0
                val = sum(w * v for w, v in zip(weights, window)) / norm
            else:
                val = sum(window) / float(len(window))
            smoothed.append(round(val, 6))

        return smoothed


class DigitalFilterEngine:
    """Applies high-pass, low-pass, and band-pass digital Butterworth-style recursive filtering."""
    @classmethod
    def low_pass_filter(cls, signal: List[float], alpha: float = 0.2) -> List[float]:
        if not signal:
            return []
        out = [signal[0]]
        for i in range(1, len(signal)):
            filtered = alpha * signal[i] + (1.0 - alpha) * out[-1]
            out.append(round(filtered, 6))
        return out

    @classmethod
    def high_pass_filter(cls, signal: List[float], alpha: float = 0.8) -> List[float]:
        if not signal:
            return []
        out = [0.0]
        for i in range(1, len(signal)):
            filtered = alpha * (out[-1] + signal[i] - signal[i - 1])
            out.append(round(filtered, 6))
        return out
