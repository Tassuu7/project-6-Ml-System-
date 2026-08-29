"""
DataMorph Studio - Mathematical & Statistical Computational Library
Provides pure Python statistical calculations, matrix transformations,
distance metrics, and numerical helpers with high precision.
"""

import math
from typing import List, Optional, Any, Dict, Tuple


def mean(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0


def variance(values: List[float], sample: bool = True) -> Optional[float]:
    if not values or len(values) < 2:
        return 0.0 if len(values) == 1 else None
    avg = mean(values)
    sq_diff = sum((x - avg) ** 2 for x in values)
    divisor = (len(values) - 1) if sample else len(values)
    return sq_diff / divisor


def std_dev(values: List[float], sample: bool = True) -> Optional[float]:
    v = variance(values, sample=sample)
    if v is None:
        return None
    return math.sqrt(max(0.0, v))


def quantile(values: List[float], q: float) -> Optional[float]:
    if not values:
        return None
    if q < 0.0 or q > 1.0:
        raise ValueError(f"Quantile must be between 0.0 and 1.0, got {q}")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    pos = q * (n - 1)
    base = int(math.floor(pos))
    rest = pos - base
    if base + 1 < n:
        return sorted_vals[base] + rest * (sorted_vals[base + 1] - sorted_vals[base])
    return sorted_vals[base]


def min_value(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return min(values)


def max_value(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return max(values)


def count_missing(values: List[Any]) -> int:
    return sum(1 for x in values if x is None or (isinstance(x, float) and math.isnan(x)) or x == "")


def distinct_values(values: List[Any]) -> List[Any]:
    seen = set()
    result = []
    for x in values:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


def mode(values: List[Any]) -> Optional[Any]:
    filtered = [x for x in values if x is not None and x != ""]
    if not filtered:
        return None
    counts = {}
    for x in filtered:
        counts[x] = counts.get(x, 0) + 1
    return max(counts, key=counts.get)


def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2):
        raise ValueError("Vectors must have equal length for Euclidean distance")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def manhattan_distance(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2):
        raise ValueError("Vectors must have equal length for Manhattan distance")
    return sum(abs(a - b) for a, b in zip(v1, v2))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2):
        raise ValueError("Vectors must have equal length for Cosine similarity")
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a ** 2 for a in v1))
    norm_b = math.sqrt(sum(b ** 2 for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def pearson_correlation(x: List[float], y: List[float]) -> Optional[float]:
    if len(x) != len(y) or len(x) < 2:
        return None
    mean_x = mean(x)
    mean_y = mean(y)
    std_x = std_dev(x)
    std_y = std_dev(y)
    if std_x == 0.0 or std_y == 0.0 or std_x is None or std_y is None:
        return 0.0
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y)) / (len(x) - 1)
    return cov / (std_x * std_y)


def entropy(values: List[Any]) -> float:
    filtered = [x for x in values if x is not None and x != ""]
    if not filtered:
        return 0.0
    total = len(filtered)
    counts = {}
    for x in filtered:
        counts[x] = counts.get(x, 0) + 1
    ent = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            ent -= p * math.log2(p)
    return ent
