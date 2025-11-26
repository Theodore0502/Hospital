
import os
from pathlib import Path

import osmnx as ox
import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_hospital_data(place_name: str = "Hanoi, Vietnam",
                        save_path: str | None = None) -> None:
    """Tải dữ liệu bệnh viện từ OpenStreetMap bằng osmnx."""
    if save_path is None:
        save_path = DATA_DIR / "hospitals_clean.csv"
    else:
        save_path = Path(save_path)

    tags = {"amenity": "hospital"}
    print(f"Đang tải dữ liệu bệnh viện cho khu vực: {place_name} ...")
    gdf = ox.features_from_place(place_name, tags)

    # Giữ các trường cần thiết nếu tồn tại
    keep_cols = ["name", "geometry", "amenity", "addr:street", "addr:city"]
    existing_cols = [c for c in keep_cols if c in gdf.columns]
    gdf = gdf[existing_cols]

    # Tạo DataFrame với centroid (lat/lon)
    centroids = gdf.geometry.centroid
    df = pd.DataFrame({
        "name": gdf.get("name"),
        "lat": centroids.y,
        "lon": centroids.x,
        "street": gdf.get("addr:street"),
        "city": gdf.get("addr:city"),
    })

    df.to_csv(save_path, index=False)
    print("Đã lưu dữ liệu vào:", save_path)



if __name__ == "__main__":
    fetch_hospital_data()
