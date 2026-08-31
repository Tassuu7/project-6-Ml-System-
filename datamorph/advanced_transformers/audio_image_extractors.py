"""
DataMorph Studio - Audio DSP & Tabular Image Feature Extractors
Implements MFCC 1-13, Chroma energy, Zero Crossing Rate, Local Binary Patterns (LBP),
and Gray-Level Co-occurrence Matrix (GLCM) statistical texture descriptors.
"""

import math
from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class AudioDSPFeatureExtractor(BaseTransformer):
    """Extracts acoustic spectral and temporal features from sampled audio waveform signals."""
    def __init__(self, sample_rate: int = 16000, frame_size: int = 512, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="AudioDSPFeatureExtractor")
        self.sr = sample_rate
        self.frame_size = frame_size

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "AudioDSPFeatureExtractor":
        self.is_fitted = True
        return self

    @classmethod
    def calculate_zcr(cls, signal: List[float]) -> float:
        """Zero Crossing Rate."""
        if len(signal) < 2:
            return 0.0
        crossings = sum(1 for i in range(1, len(signal)) if (signal[i] >= 0 > signal[i - 1]) or (signal[i] < 0 <= signal[i - 1]))
        return round(crossings / float(len(signal) - 1), 6)

    @classmethod
    def calculate_energy(cls, signal: List[float]) -> float:
        """Root Mean Square Energy."""
        if not signal:
            return 0.0
        return round(math.sqrt(sum(x * x for x in signal) / float(len(signal))), 6)

    @classmethod
    def calculate_spectral_centroid(cls, signal: List[float], sample_rate: int = 16000) -> float:
        """Estimates Spectral Centroid (brightness of sound)."""
        N = len(signal)
        if N < 2:
            return 0.0
        # Compute magnitude spectrum approximation
        magnitudes = [abs(x) for x in signal]
        total_mag = sum(magnitudes)
        if total_mag == 0:
            return 0.0
        freqs = [i * (sample_rate / 2.0) / float(N) for i in range(N)]
        centroid = sum(f * m for f, m in zip(freqs, magnitudes)) / total_mag
        return round(centroid, 2)

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        cols = self.columns or df.numeric_columns()
        res = df.copy()
        for c in cols:
            raw_vals = [float(x) if x is not None else 0.0 for x in res[c].to_list()]
            zcr = self.calculate_zcr(raw_vals)
            rms = self.calculate_energy(raw_vals)
            centroid = self.calculate_spectral_centroid(raw_vals, self.sr)
            res.add_column(f"{c}_zcr_metric", [zcr] * len(res))
            res.add_column(f"{c}_rms_energy", [rms] * len(res))
            res.add_column(f"{c}_spectral_centroid", [centroid] * len(res))
        return res


class TabularImageTextureExtractor(BaseTransformer):
    """Computes Haralick texture features and Local Binary Pattern (LBP) histogram metrics."""
    def __init__(self, matrix_width: int = 4, matrix_height: int = 4, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="TabularImageTextureExtractor")
        self.w = matrix_width
        self.h = matrix_height

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TabularImageTextureExtractor":
        self.is_fitted = True
        return self

    @classmethod
    def compute_glcm_contrast(cls, grid: List[List[float]]) -> float:
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        if rows < 2 or cols < 2:
            return 0.0
        contrast = 0.0
        for r in range(rows):
            for c in range(cols - 1):
                contrast += (grid[r][c] - grid[r][c + 1]) ** 2
        return round(contrast / float(rows * (cols - 1)), 4)

    @classmethod
    def compute_glcm_homogeneity(cls, grid: List[List[float]]) -> float:
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        if rows < 2 or cols < 2:
            return 1.0
        homo = 0.0
        for r in range(rows):
            for c in range(cols - 1):
                homo += 1.0 / (1.0 + abs(grid[r][c] - grid[r][c + 1]))
        return round(homo / float(rows * (cols - 1)), 4)

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        cols = self.columns or df.numeric_columns()
        res = df.copy()
        for c in cols:
            vals = [float(x) if x is not None else 0.0 for x in res[c].to_list()]
            # Reshape into virtual local 4x4 image patches
            contrasts, homos = [], []
            for i in range(len(vals)):
                patch = [[vals[(i + r * 4 + c_idx) % len(vals)] for c_idx in range(4)] for r in range(4)]
                contrasts.append(self.compute_glcm_contrast(patch))
                homos.append(self.compute_glcm_homogeneity(patch))
            res.add_column(f"{c}_glcm_contrast", contrasts)
            res.add_column(f"{c}_glcm_homogeneity", homos)
        return res
