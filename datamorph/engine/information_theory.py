"""
DataMorph Studio - Information Theory & Entropy Subsystem
Calculates Shannon entropy, Rényi entropy, Kullback-Leibler (KL) divergence,
Jensen-Shannon divergence, and Mutual Information matrices.
"""

import math
from typing import List, Dict, Any, Tuple


class ShannonEntropy:
    """Calculates Shannon Entropy H(X) = -sum(p(x) * log2(p(x)))."""
    @staticmethod
    def discrete_entropy(labels: List[Any], base: float = 2.0) -> float:
        if not labels:
            return 0.0
        n = len(labels)
        counts: Dict[Any, int] = {}
        for x in labels:
            counts[x] = counts.get(x, 0) + 1

        h = 0.0
        for cnt in counts.values():
            p = cnt / float(n)
            if p > 0.0:
                h -= p * (math.log(p) / math.log(base))
        return round(max(0.0, h), 6)

    @staticmethod
    def continuous_entropy(values: List[float], n_bins: int = 20) -> float:
        if not values or len(values) < 2:
            return 0.0
        v_min, v_max = min(values), max(values)
        if v_min == v_max:
            return 0.0
        step = (v_max - v_min) / float(n_bins)
        bins = [0] * n_bins
        for x in values:
            b_idx = min(int((x - v_min) / step), n_bins - 1)
            bins[b_idx] += 1
        n = len(values)
        h = 0.0
        for cnt in bins:
            if cnt > 0:
                p = cnt / float(n)
                h -= p * math.log2(p)
        return round(h + math.log2(step), 6)


class RenyiEntropy:
    """Calculates Rényi Generalized Entropy of order alpha."""
    @staticmethod
    def calculate(labels: List[Any], alpha: float = 2.0) -> float:
        if not labels or alpha <= 0 or alpha == 1.0:
            return ShannonEntropy.discrete_entropy(labels)
        n = len(labels)
        counts: Dict[Any, int] = {}
        for x in labels:
            counts[x] = counts.get(x, 0) + 1

        sum_p_alpha = sum((cnt / float(n)) ** alpha for cnt in counts.values())
        return round((1.0 / (1.0 - alpha)) * math.log2(max(1e-15, sum_p_alpha)), 6)


class KullbackLeiblerDivergence:
    """Calculates KL Divergence D_KL(P || Q) = sum(P(x) * log(P(x) / Q(x)))."""
    @staticmethod
    def calculate(p_dist: List[float], q_dist: List[float], epsilon: float = 1e-10) -> float:
        if len(p_dist) != len(q_dist):
            raise ValueError("Distributions P and Q must have identical cardinality")
        kl = 0.0
        for p, q in zip(p_dist, q_dist):
            p_safe = max(epsilon, p)
            q_safe = max(epsilon, q)
            kl += p_safe * math.log(p_safe / q_safe)
        return round(max(0.0, kl), 6)


class JensenShannonDivergence:
    """Calculates symmetric, bounded Jensen-Shannon Divergence JSD(P || Q) in [0, 1]."""
    @staticmethod
    def calculate(p_dist: List[float], q_dist: List[float]) -> float:
        if len(p_dist) != len(q_dist):
            raise ValueError("Distributions P and Q must have identical cardinality")
        m = [0.5 * (p + q) for p, q in zip(p_dist, q_dist)]
        kl_pm = KullbackLeiblerDivergence.calculate(p_dist, m)
        kl_qm = KullbackLeiblerDivergence.calculate(q_dist, m)
        jsd = 0.5 * (kl_pm + kl_qm)
        return round(max(0.0, jsd / math.log(2.0)), 6)


class MutualInformationCalculator:
    """Calculates Mutual Information I(X; Y) = H(X) + H(Y) - H(X, Y)."""
    @staticmethod
    def calculate(x: List[Any], y: List[Any]) -> float:
        if len(x) != len(y) or not x:
            return 0.0
        h_x = ShannonEntropy.discrete_entropy(x)
        h_y = ShannonEntropy.discrete_entropy(y)
        joint_pairs = [f"{x[i]}_{y[i]}" for i in range(len(x))]
        h_xy = ShannonEntropy.discrete_entropy(joint_pairs)
        mi = h_x + h_y - h_xy
        return round(max(0.0, mi), 6)


class TotalCorrelationCalculator:
    """Calculates Watanabe's Total Correlation (Multi-Information) C(X_1, ..., X_n)."""
    @staticmethod
    def calculate(*features: List[Any]) -> float:
        if not features:
            return 0.0
        marginal_entropies = sum(ShannonEntropy.discrete_entropy(f) for f in features)
        n_rows = len(features[0])
        joint_tuples = [tuple(f[i] for f in features) for i in range(n_rows)]
        joint_entropy = ShannonEntropy.discrete_entropy(joint_tuples)
        tc = marginal_entropies - joint_entropy
        return round(max(0.0, tc), 6)
