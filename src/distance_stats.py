# src/distance_stats.py
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# Import kiểu package (python -m src.distance_stats)
try:
    from .analysis import load_hospitals, _haversine  # type: ignore
# Fallback nếu chạy trực tiếp: python src/distance_stats.py
except ImportError:
    from analysis import load_hospitals, _haversine  # type: ignore


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_distance_grid(grid_size: int = 60):
    """
    Tạo lưới điểm phủ toàn bộ khu vực bệnh viện và tính
    khoảng cách đến bệnh viện gần nhất cho từng điểm.

    grid_size: số điểm theo mỗi chiều (60 -> 60x60 = 3600 điểm).
    """
    hospitals = load_hospitals()
    if hospitals.empty:
        raise ValueError(
            "Dữ liệu bệnh viện trống. Hãy chạy fetch_data + preprocess trước."
        )

    hospitals = hospitals.dropna(subset=["lat", "lon"])

    min_lat = hospitals["lat"].min()
    max_lat = hospitals["lat"].max()
    min_lon = hospitals["lon"].min()
    max_lon = hospitals["lon"].max()

    lats = np.linspace(min_lat, max_lat, grid_size)
    lons = np.linspace(min_lon, max_lon, grid_size)

    distances = []

    print(f"Đang tính khoảng cách trên lưới {grid_size} x {grid_size} ...")
    for lat in lats:
        for lon in lons:
            d_km = hospitals.apply(
                lambda row: _haversine(lat, lon, row.lat, row.lon), axis=1
            ).min()
            distances.append(float(d_km))

    distances = np.array(distances)
    print(
        f"Hoàn thành. Khoảng cách nhỏ nhất: {distances.min():.2f} km, "
        f"lớn nhất: {distances.max():.2f} km, trung bình: {distances.mean():.2f} km"
    )
    return distances


def plot_distance_histogram(distances: np.ndarray,
                            save_path: Path | None = None):
    """Vẽ histogram phân bố khoảng cách."""
    if save_path is None:
        save_path = OUTPUT_DIR / "distance_histogram.png"

    plt.figure(figsize=(8, 5))
    plt.hist(distances, bins=20, edgecolor="black")
    plt.xlabel("Khoảng cách tới bệnh viện gần nhất (km)")
    plt.ylabel("Số lượng điểm lưới")
    plt.title("Phân bố khoảng cách tới bệnh viện gần nhất (trên lưới không gian)")
    plt.grid(alpha=0.3, linestyle="--")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print("Đã lưu biểu đồ histogram:", save_path)


def plot_distance_bands(distances: np.ndarray,
                        save_path: Path | None = None):
    """
    Vẽ bar chart tỉ lệ diện tích rơi vào từng khoảng cách:
    <1 km, 1–2 km, 2–3 km, 3–4 km, >4 km
    """
    if save_path is None:
        save_path = OUTPUT_DIR / "distance_bands.png"

    bins = [0, 1, 2, 3, 4, np.inf]
    labels = ["<1 km", "1–2 km", "2–3 km", "3–4 km", ">4 km"]

    counts = []
    total = len(distances)
    for i in range(len(bins) - 1):
        mask = (distances >= bins[i]) & (distances < bins[i + 1])
        counts.append(mask.sum())

    counts = np.array(counts)
    percents = counts / total * 100

    plt.figure(figsize=(7, 5))
    plt.bar(labels, percents)
    plt.ylabel("Tỉ lệ điểm lưới (%)")
    plt.title("Tỉ lệ khu vực theo khoảng cách tới bệnh viện gần nhất")
    for i, v in enumerate(percents):
        plt.text(i, v + 0.5, f"{v:.1f}%", ha="center", va="bottom")
    plt.ylim(0, max(percents) * 1.2)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print("Đã lưu biểu đồ tỉ lệ khoảng cách:", save_path)


def main():
    distances = compute_distance_grid(grid_size=60)
    # Lưu dữ liệu khoảng cách ra CSV để tham khảo nếu cần
    np.savetxt(OUTPUT_DIR / "distance_grid_values.csv",
               distances,
               delimiter=",",
               header="distance_km",
               comments="")
    print("Đã lưu dữ liệu khoảng cách vào:", OUTPUT_DIR / "distance_grid_values.csv")

    plot_distance_histogram(distances)
    plot_distance_bands(distances)


if __name__ == "__main__":
    main()
