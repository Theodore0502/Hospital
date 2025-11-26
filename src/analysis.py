
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class HospitalDistanceResult:
    name: str
    street: Optional[str]
    city: Optional[str]
    distance_km: float
    lat: float
    lon: float


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Tính khoảng cách giữa 2 điểm (lat/lon) theo km (công thức Haversine)."""
    R = 6371  # bán kính Trái Đất (km)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def load_hospitals(csv_path: str | None = None) -> pd.DataFrame:
    if csv_path is None:
        preprocessed = DATA_DIR / "hospitals_preprocessed.csv"
        if preprocessed.exists():
            csv_path = preprocessed
        else:
            csv_path = DATA_DIR / "hospitals_clean.csv"
    else:
        csv_path = Path(csv_path)

    return pd.read_csv(csv_path)


def find_nearest_hospital(lat: float,
                          lon: float,
                          csv_path: str | None = None) -> HospitalDistanceResult:
    """Tìm bệnh viện gần nhất đến một toạ độ bất kỳ."""
    df = load_hospitals(csv_path)
    if df.empty:
        raise ValueError("Dữ liệu bệnh viện trống.")

    distances = df.apply(
        lambda row: _haversine(lat, lon, row.lat, row.lon),
        axis=1,
    )
    idx_min = distances.idxmin()
    row = df.loc[idx_min]
    dist_km = float(distances.loc[idx_min])

    return HospitalDistanceResult(
        name=str(row.get("name", "No name")),
        street=row.get("street"),
        city=row.get("city"),
        distance_km=dist_km,
        lat=float(row.lat),
        lon=float(row.lon),
    )


def build_service_area_buffers(buffer_m: float = 2000,
                               csv_path: str | None = None,
                               save_geojson: str | None = None) -> Path:
    """Tạo buffer (vùng phục vụ) xung quanh từng bệnh viện.

    buffer_m: bán kính tính bằng mét (vd: 2000 = 2km).
    """
    df = load_hospitals(csv_path)
    if df.empty:
        raise ValueError("Dữ liệu bệnh viện trống.")

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.lon, df.lat),
        crs="EPSG:4326",
    )

    # Chuyển sang Web Mercator để buffer theo mét
    gdf_proj = gdf.to_crs(epsg=3857)
    gdf_proj["geometry"] = gdf_proj.geometry.buffer(buffer_m)
    gdf_buffer = gdf_proj.to_crs(epsg=4326)

    if save_geojson is None:
        save_geojson = OUTPUT_DIR / "hospital_service_areas.geojson"
    else:
        save_geojson = Path(save_geojson)

    gdf_buffer.to_file(save_geojson, driver="GeoJSON")
    print("Đã tạo buffer vùng phục vụ và lưu vào:", save_geojson)
    return save_geojson


if __name__ == "__main__":
    # Ví dụ: tạo buffer 2km xung quanh mỗi bệnh viện
    build_service_area_buffers(buffer_m=2000)
