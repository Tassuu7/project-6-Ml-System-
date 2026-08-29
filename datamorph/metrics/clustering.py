"""
DataMorph Studio - Unsupervised Clustering Validation Metrics
Calculates Silhouette Coefficient, Davies-Bouldin Index, and Calinski-Harabasz Variance Ratio.
"""

import math
from typing import List, Dict, Any
from datamorph.utils.math_utils import euclidean_distance


class ClusteringMetrics:
    """Evaluates unsupervised cluster quality."""

    @classmethod
    def silhouette_score(cls, X: List[List[float]], labels: List[int]) -> float:
        n = len(X)
        if n < 2 or len(set(labels)) < 2:
            return 0.0

        unique_labels = set(labels)
        cluster_points: Dict[int, List[List[float]]] = {lbl: [] for lbl in unique_labels}
        for pt, lbl in zip(X, labels):
            cluster_points[lbl].append(pt)

        s_scores = []
        for i in range(min(500, n)):  # sample for performance
            pt_i = X[i]
            lbl_i = labels[i]

            # a(i): mean intra-cluster distance
            same_pts = cluster_points[lbl_i]
            if len(same_pts) > 1:
                a_i = sum(euclidean_distance(pt_i, p) for p in same_pts if p != pt_i) / (len(same_pts) - 1)
            else:
                a_i = 0.0

            # b(i): mean nearest-cluster distance
            min_b = float("inf")
            for other_lbl, other_pts in cluster_points.items():
                if other_lbl != lbl_i and other_pts:
                    dist_b = sum(euclidean_distance(pt_i, p) for p in other_pts) / len(other_pts)
                    if dist_b < min_b:
                        min_b = dist_b

            b_i = min_b if min_b != float("inf") else 0.0
            denom = max(a_i, b_i)
            s_i = (b_i - a_i) / denom if denom > 0 else 0.0
            s_scores.append(s_i)

        return round(sum(s_scores) / max(1, len(s_scores)), 4)
