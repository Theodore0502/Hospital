from pathlib import Path
from unittest import result

from src.fetch_data import fetch_hospital_data
from src.preprocess import preprocess_hospitals
from src.build_map import build_map
from src.analysis import find_nearest_hospital
from src.routing import build_route_map_to_nearest_hospital
import math

def main():
    # 1. Tải dữ liệu
    fetch_hospital_data("Hanoi, Vietnam")

    # 2. Tiền xử lý
    preprocess_hospitals()

    # 3. Tạo bản đồ điểm + heatmap
    build_map()

    # 4. Demo nearest hospital (đường chim bay)
    sample_lat = 21.027763
    sample_lon = 105.834160
    result = find_nearest_hospital(sample_lat, sample_lon)

    print("\nVí dụ tính khoảng cách từ (lat, lon) = "
          f"({sample_lat}, {sample_lon}) tới bệnh viện gần nhất:")
    print(f"- Tên bệnh viện: {result.name}")
    address_parts = [p for p in [result.street, result.city] if isinstance(p, str)]
    if address_parts:
        print(f"- Địa chỉ: {', '.join(address_parts)}")
    print(f"- Khoảng cách: {result.distance_km:.2f} km")

    # 5. Demo route theo mạng lưới đường
    build_route_map_to_nearest_hospital(
        origin_lat=sample_lat,
        origin_lon=sample_lon,
        place_name="Hanoi, Vietnam",
    )

if __name__ == "__main__":
    main()
