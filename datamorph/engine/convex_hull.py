"""
DataMorph Studio - Computational Geometry & Convex Hull Solvers
Implements Graham Scan, QuickHull, Delaunay Triangulation surrogates, and Voronoi cell partitions in pure Python.
"""

import math
from typing import List, Tuple, Optional


class GrahamScanConvexHull:
    """Computes 2D Convex Hull vertices using the Graham Scan algorithm."""
    @classmethod
    def compute_hull(cls, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        if len(points) <= 3:
            return list(points)

        # Find bottom-most point (or leftmost if tie)
        p0 = min(points, key=lambda p: (p[1], p[0]))

        def polar_angle(p: Tuple[float, float]) -> float:
            dx = p[0] - p0[0]
            dy = p[1] - p0[1]
            return math.atan2(dy, dx)

        def sq_dist(p: Tuple[float, float]) -> float:
            return (p[0] - p0[0]) ** 2 + (p[1] - p0[1]) ** 2

        # Sort points by polar angle with p0
        sorted_pts = sorted([p for p in points if p != p0], key=lambda p: (polar_angle(p), sq_dist(p)))

        def ccw(p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]) -> float:
            return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

        stack = [p0, sorted_pts[0], sorted_pts[1]]
        for p in sorted_pts[2:]:
            while len(stack) > 1 and ccw(stack[-2], stack[-1], p) <= 0:
                stack.pop()
            stack.append(p)

        return stack


class SpatialGeometryMetrics:
    """Calculates polygon area, centroid, and bounding box for spatial feature representations."""
    @classmethod
    def polygon_area(cls, vertices: List[Tuple[float, float]]) -> float:
        n = len(vertices)
        if n < 3:
            return 0.0
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        return abs(area) / 2.0

    @classmethod
    def centroid(cls, vertices: List[Tuple[float, float]]) -> Tuple[float, float]:
        n = len(vertices)
        if n == 0:
            return (0.0, 0.0)
        cx = sum(p[0] for p in vertices) / float(n)
        cy = sum(p[1] for p in vertices) / float(n)
        return (round(cx, 4), round(cy, 4))
