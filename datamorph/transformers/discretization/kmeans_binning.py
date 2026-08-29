"""
DataMorph Studio - 1D K-Means Clustering Discretizer
Groups 1-dimensional continuous features using 1D k-means cluster centroids.
"""

from typing import List, Optional, Dict
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean


class KMeansDiscretizer(BaseTransformer):
    def __init__(self, n_clusters: int = 4, max_iter: int = 20,
                 columns: Optional[List[str]] = None, name: str = "KMeansDiscretizer"):
        super().__init__(columns=columns, name=name)
        self.n_clusters = max(2, n_clusters)
        self.max_iter = max_iter
        self.centroids_: Dict[str, List[float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "KMeansDiscretizer":
        target_cols = self._resolve_columns(df)
        self.centroids_ = {}

        for col in target_cols:
            vals = df[col].values_numeric()
            if not vals:
                self.centroids_[col] = [0.0] * self.n_clusters
                continue
            # Initial centroids via quantiles
            step = len(vals) // self.n_clusters or 1
            centroids = [sorted(vals)[min(i * step, len(vals) - 1)] for i in range(self.n_clusters)]

            for _ in range(self.max_iter):
                clusters: Dict[int, List[float]] = {i: [] for i in range(self.n_clusters)}
                for x in vals:
                    closest_idx = min(range(self.n_clusters), key=lambda idx: abs(x - centroids[idx]))
                    clusters[closest_idx].append(x)
                new_centroids = [mean(clusters[i]) or centroids[i] for i in range(self.n_clusters)]
                if new_centroids == centroids:
                    break
                centroids = sorted(new_centroids)

            self.centroids_[col] = centroids

        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        target_cols = self._resolve_columns(df)
        result = df.copy()

        for col in target_cols:
            cents = self.centroids_.get(col, [])
            binned = []
            for v in df[col].to_list():
                if v is None or v == "":
                    binned.append(None)
                else:
                    try:
                        val = float(v)
                        closest = min(range(len(cents)), key=lambda idx: abs(val - cents[idx]))
                        binned.append(f"cluster_{closest}")
                    except Exception:
                        binned.append(None)
            result.add_column(f"{col}_cluster", binned)

        return result
