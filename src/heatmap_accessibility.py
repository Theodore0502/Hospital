# src/heatmap_accessibility.py
from __future__ import annotations

from pathlib import Path

import folium
from folium.plugins import HeatMap
import numpy as np

# Thử import kiểu package (khi chạy: python -m src.heatmap_accessibility)
try:
    from .analysis import load_hospitals, _haversine  # type: ignore
# Fallback: khi chạy trực tiếp: python src/heatmap_accessibility.py
except ImportError:  # no parent package
    from analysis import load_hospitals, _haversine  # type: ignore

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _min_distance_to_hospital(lat: float, lon: float, hospitals_df) -> float:
    """Tính khoảng cách (km) từ 1 điểm tới bệnh viện gần nhất."""
    distances = hospitals_df.apply(
        lambda row: _haversine(lat, lon, row.lat, row.lon),
        axis=1,
    )
    return float(distances.min())


def build_accessibility_heatmap(
    csv_path: str | None = None,
    save_html: str | None = None,
    grid_size: int = 70,
    max_clip_km: float = 5.0,
):
    """
    Tạo heatmap khả năng tiếp cận bệnh viện (khu xa bệnh viện sẽ "nóng").

    - grid_size: số điểm theo mỗi chiều lưới (70 -> 70x70 = 4900 điểm, mịn hơn)
    - max_clip_km: khoảng cách clip trên (vd: >5km coi như 5km để không làm bẹp thang màu)
    """
    hospitals = load_hospitals(csv_path)
    if hospitals.empty:
        raise ValueError("Dữ liệu bệnh viện trống, hãy chạy fetch_data + preprocess trước.")

    # Lấy bounding box của toàn bộ bệnh viện
    min_lat = hospitals["lat"].min()
    max_lat = hospitals["lat"].max()
    min_lon = hospitals["lon"].min()
    max_lon = hospitals["lon"].max()

    # Tạo lưới điểm
    lats = np.linspace(min_lat, max_lat, grid_size)
    lons = np.linspace(min_lon, max_lon, grid_size)

    heat_points = []
    max_dist = 0.0

    print("Đang tính khoảng cách tới bệnh viện gần nhất cho từng điểm lưới...")
    for lat in lats:
        for lon in lons:
            d_km = _min_distance_to_hospital(lat, lon, hospitals)
            max_dist = max(max_dist, d_km)
            # Chuẩn hoá và clip để màu mượt hơn
            d_clipped = min(d_km, max_clip_km)
            weight = d_clipped / max_clip_km  # 0 ~ rất gần; 1 ~ rất xa
            heat_points.append([lat, lon, weight])

    print(f"Khoảng cách lớn nhất (trước khi clip): {max_dist:.2f} km")

    # Tâm bản đồ: trung bình toạ độ
    center = [hospitals["lat"].mean(), hospitals["lon"].mean()]

    # Dùng nền sáng cho map trông chuyên nghiệp hơn
    m = folium.Map(location=center, zoom_start=11, tiles="cartodbpositron")

    # Layer heatmap vùng xa bệnh viện
    HeatMap(
        heat_points,
        radius=20,      # nhỏ hơn một chút để bớt bệt
        blur=30,
        max_zoom=13,
        min_opacity=0.2,
    ).add_to(m)

    # Thêm marker bệnh viện nhỏ xíu để nhìn rõ
    for _, row in hospitals.iterrows():
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=3,
            popup=row.get("name", ""),
            color="white",
            fill=True,
            fill_opacity=0.9,
        ).add_to(m)

    if save_html is None:
        save_html = OUTPUT_DIR / "hospital_accessibility_heatmap.html"
    else:
        save_html = Path(save_html)

    m.save(save_html)
    print("Đã tạo heatmap khả năng tiếp cận (mượt hơn):", save_html)
    return save_html


if __name__ == "__main__":
    build_accessibility_heatmap()
