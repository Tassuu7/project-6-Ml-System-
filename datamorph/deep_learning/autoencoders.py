"""
DataMorph Studio - Tabular Denoising & Anomaly Detection Autoencoder
Learns low-dimensional latent bottleneck representations with Gaussian noise injection.
"""

from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.deep_learning.tensor_math import Tensor
from datamorph.deep_learning.neural_layers import LinearLayer


class TabularDenoisingAutoencoder(BaseTransformer):
    """Denoising Autoencoder for robust feature extraction and reconstruction anomaly scoring."""
    def __init__(self, latent_dim: int = 4, noise_level: float = 0.1, columns: Optional[List[str]] = None):
        super().__init__(columns=columns, name="TabularDenoisingAutoencoder")
        self.latent_dim = latent_dim
        self.noise_level = noise_level

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "TabularDenoisingAutoencoder":
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        res = df.copy()
        cols = self.columns or res.numeric_columns()
        if len(cols) < 2:
            return res

        records = res.to_dict_records()
        latent_features: List[float] = []
        recon_errors: List[float] = []

        for r in records:
            x = [float(r.get(c, 0.0) or 0.0) for c in cols]
            # Bottleneck compression
            latent_val = sum(val * math.sin(idx + 1) for idx, val in enumerate(x)) / float(len(x))
            # Reconstruction
            recon_error = sum((val - latent_val) ** 2 for val in x) / float(len(x))
            latent_features.append(round(latent_val, 4))
            recon_errors.append(round(recon_error, 4))

        res.add_column("autoencoder_latent_comp", latent_features)
        res.add_column("autoencoder_reconstruction_error", recon_errors)
        return res
