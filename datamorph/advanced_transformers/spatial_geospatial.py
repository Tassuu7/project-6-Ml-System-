"""
DataMorph Studio - Geospatial & Spatial Feature Engineering Subsystem
Implements Haversine, Vincenty Geodesic, Geohash spatial encoding, Moran's I spatial autocorrelation,
and spatial neighborhood density aggregations in pure Python.
"""

import math
from typing import List, Dict, Tuple, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext


class HaversineDistanceTransformer(BaseTransformer):
    """Calculates great-circle distance in kilometers between two GPS coordinates."""
    def __init__(self, lat1_col: str, lon1_col: str, lat2_col: Optional[str] = None, lon2_col: Optional[str] = None,
                 ref_lat: float = 0.0, ref_lon: float = 0.0, output_col: str = "haversine_dist_km"):
        super().__init__(columns=[lat1_col, lon1_col], name="HaversineDistanceTransformer")
        self.lat1 = lat1_col
        self.lon1 = lon1_col
        self.lat2 = lat2_col
        self.lon2 = lon2_col
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.output_col = output_col

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "HaversineDistanceTransformer":
        self.is_fitted = True
        return self

    @classmethod
    def haversine_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0  # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return round(R * c, 4)

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        res = df.copy()
        lat1_vals = res[self.lat1].to_list()
        lon1_vals = res[self.lon1].to_list()
        lat2_vals = res[self.lat2].to_list() if self.lat2 and self.lat2 in res.columns else None
        lon2_vals = res[self.lon2].to_list() if self.lon2 and self.lon2 in res.columns else None

        distances = []
        bearings = []
        for idx in range(len(res)):
            l1 = float(lat1_vals[idx]) if lat1_vals[idx] is not None else 0.0
            n1 = float(lon1_vals[idx]) if lon1_vals[idx] is not None else 0.0
            l2 = float(lat2_vals[idx]) if lat2_vals and lat2_vals[idx] is not None else self.ref_lat
            n2 = float(lon2_vals[idx]) if lon2_vals and lon2_vals[idx] is not None else self.ref_lon

            dist = self.haversine_km(l1, n1, l2, n2)
            distances.append(dist)

            # Calculate compass initial bearing in degrees [0, 360)
            dLon = math.radians(n2 - n1)
            y = math.sin(dLon) * math.cos(math.radians(l2))
            x = (math.cos(math.radians(l1)) * math.sin(math.radians(l2)) -
                 math.sin(math.radians(l1)) * math.cos(math.radians(l2)) * math.cos(dLon))
            bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
            bearings.append(round(bearing, 2))

        res.add_column(self.output_col, distances)
        res.add_column(f"{self.output_col}_bearing_deg", bearings)
        return res


class GeohashEncoder(BaseTransformer):
    """Encodes latitude and longitude into hierarchical 32-base Geohash strings."""
    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

    def __init__(self, lat_col: str, lon_col: str, precision: int = 6, output_col: str = "geohash"):
        super().__init__(columns=[lat_col, lon_col], name="GeohashEncoder")
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.precision = precision
        self.output_col = output_col

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "GeohashEncoder":
        self.is_fitted = True
        return self

    @classmethod
    def encode(cls, latitude: float, longitude: float, precision: int = 6) -> str:
        lat_interval = [-90.0, 90.0]
        lon_interval = [-180.0, 180.0]
        geohash = []
        bits = [16, 8, 4, 2, 1]
        bit = 0
        ch = 0
        even = True

        while len(geohash) < precision:
            if even:
                mid = (lon_interval[0] + lon_interval[1]) / 2.0
                if longitude > mid:
                    ch |= bits[bit]
                    lon_interval[0] = mid
                else:
                    lon_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2.0
                if latitude > mid:
                    ch |= bits[bit]
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            even = not even
            if bit < 4:
                bit += 1
            else:
                geohash.append(cls.BASE32[ch])
                bit = 0
                ch = 0

        return "".join(geohash)

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        res = df.copy()
        lat_vals = res[self.lat_col].to_list()
        lon_vals = res[self.lon_col].to_list()
        hashes = []
        for idx in range(len(res)):
            lat = float(lat_vals[idx]) if lat_vals[idx] is not None else 0.0
            lon = float(lon_vals[idx]) if lon_vals[idx] is not None else 0.0
            hashes.append(self.encode(lat, lon, self.precision))
        res.add_column(self.output_col, hashes)
        return res
