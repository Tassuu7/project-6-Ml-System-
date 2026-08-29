"""
DataMorph Studio - Bivariate Correlation & Association Matrix Analyzer
Computes Pearson, Spearman rank, Kendall tau, Cramer's V, and Correlation Ratios (Eta).
"""

import math
from typing import Dict, List, Any
from datamorph.core.dataframe import DataFrame
from datamorph.utils.math_utils import pearson_correlation


class BivariateAnalyzer:
    """Computes multidimensional bivariate correlation matrices."""

    @classmethod
    def spearman_rank_correlation(cls, x: List[float], y: List[float]) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        n = len(x)
        # Compute ranks
        rank_x = cls._rank_array(x)
        rank_y = cls._rank_array(y)
        return pearson_correlation(rank_x, rank_y) or 0.0

    @classmethod
    def _rank_array(cls, arr: List[float]) -> List[float]:
        n = len(arr)
        paired = sorted([(val, idx) for idx, val in enumerate(arr)], key=lambda item: item[0])
        ranks = [0.0] * n
        for rank, (val, orig_idx) in enumerate(paired, start=1):
            ranks[orig_idx] = float(rank)
        return ranks

    @classmethod
    def cramers_v(cls, cat1: List[Any], cat2: List[Any]) -> float:
        """Cramer's V association metric for two nominal variables in [0, 1]."""
        if len(cat1) != len(cat2) or not cat1:
            return 0.0
        contingency: Dict[Any, Dict[Any, int]] = {}
        for c1, c2 in zip(cat1, cat2):
            contingency.setdefault(c1, {})
            contingency[c1][c2] = contingency[c1].get(c2, 0) + 1

        r = len(contingency)
        all_c2 = set(c for d in contingency.values() for c in d)
        k = len(all_c2)
        if r < 2 or k < 2:
            return 0.0

        n = len(cat1)
        chi2 = 0.0
        row_sums = {c1: sum(d.values()) for c1, d in contingency.items()}
        col_sums = {c2_val: sum(contingency[c1].get(c2_val, 0) for c1 in contingency) for c2_val in all_c2}

        for c1, d in contingency.items():
            for c2_val in all_c2:
                obs = d.get(c2_val, 0)
                exp = (row_sums[c1] * col_sums[c2_val]) / float(n)
                if exp > 0:
                    chi2 += ((obs - exp) ** 2) / exp

        v = math.sqrt(chi2 / (n * min(r - 1, k - 1)))
        return round(min(1.0, max(0.0, v)), 4)
