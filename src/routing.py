# src/routing.py
from __future__ import annotations

from pathlib import Path

import folium
import osmnx as ox

from .analysis import find_nearest_hospital
from .utils import geocode_address

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def download_road_network(place_name: str = "Hanoi, Vietnam",
                          save_path: str | None = None) -> Path:
    """
    Tải mạng lưới đường (graph) cho khu vực cần phân tích.

    place_name: tên khu vực (ví dụ: "Hanoi, Vietnam")
    """
    if save_path is None:
        save_path = DATA_DIR / "road_network.graphml"
    else:
        save_path = Path(save_path)

    print(f"Đang tải mạng lưới đường cho khu vực: {place_name} ...")
    G = ox.graph_from_place(place_name, network_type="drive")
    ox.save_graphml(G, save_path)
    print("Đã lưu graph road network vào:", save_path)
    return save_path


def _load_road_network(graphml_path: str | Path | None = None,
                       place_name: str = "Hanoi, Vietnam"):
    """
    Load road network từ file graphml, nếu chưa có thì tải mới.
    """
    if graphml_path is None:
        graphml_path = DATA_DIR / "road_network.graphml"
    else:
        graphml_path = Path(graphml_path)

    if not graphml_path.exists():
        download_road_network(place_name=place_name, save_path=graphml_path)

    print("Đang load road network từ:", graphml_path)
    G = ox.load_graphml(graphml_path)
    return G


def build_route_map_to_nearest_hospital(
    origin_lat: float,
    origin_lon: float,
    place_name: str = "Hanoi, Vietnam",
    graphml_path: str | None = None,
    csv_path: str | None = None,
    save_html: str | None = None,
):
    """
    Tạo bản đồ Folium thể hiện:
    - Điểm xuất phát (nhà)
    - Bệnh viện gần nhất (theo Haversine distance)
    - Đường đi ngắn nhất theo mạng lưới đường (shortest path theo 'length')
    """
    if save_html is None:
        save_html = OUTPUT_DIR / "route_to_nearest_hospital.html"
    else:
        save_html = Path(save_html)

    # 1. Load road network
    G = _load_road_network(graphml_path, place_name=place_name)

    # 2. Tìm bệnh viện gần nhất (dùng hàm đã có)
    nearest = find_nearest_hospital(origin_lat, origin_lon, csv_path=csv_path)
    print("Bệnh viện gần nhất theo khoảng cách đường chim bay:")
    print(f"- {nearest.name} ({nearest.lat}, {nearest.lon})")
    print(f"- Khoảng cách ~ {nearest.distance_km:.2f} km")

    # 3. Tìm node gần nhất trên graph cho điểm origin & hospital
    # osmnx dùng (x=lon, y=lat)
    orig_node = ox.distance.nearest_nodes(G, origin_lon, origin_lat)
    dest_node = ox.distance.nearest_nodes(G, nearest.lon, nearest.lat)

    # 4. Tính shortest path theo độ dài (mét)
    route = ox.shortest_path(G, orig_node, dest_node, weight="length")

    # 5. Tạo map Folium, center ở điểm giữa nhà và bệnh viện
    center_lat = (origin_lat + nearest.lat) / 2
    center_lon = (origin_lon + nearest.lon) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # 6. Thêm marker: origin
    folium.Marker(
        location=[origin_lat, origin_lon],
        popup="Điểm xuất phát",
        icon=folium.Icon(color="blue", icon="home"),
    ).add_to(m)

    # 7. Thêm marker: bệnh viện
    popup_html = f"<b>{nearest.name}</b>"
    folium.Marker(
        location=[nearest.lat, nearest.lon],
        popup=popup_html,
        icon=folium.Icon(color="red", icon="plus-sign"),
    ).add_to(m)

    # 8. Vẽ route
    route_coords = []
    for node in route:
        node_data = G.nodes[node]
        route_coords.append([node_data["y"], node_data["x"]])  # [lat, lon]

    folium.PolyLine(
        locations=route_coords,
        weight=6,
        opacity=0.8,
    ).add_to(m)

    m.save(save_html)
    print("Đã tạo bản đồ đường đi:", save_html)

    return save_html, nearest


def route_from_address(
    address: str,
    place_name: str = "Hanoi, Vietnam",
    graphml_path: str | None = None,
    csv_path: str | None = None,
    save_html: str | None = None,
):
    """
    Nhập địa chỉ (string) -> geocode -> chỉ đường tới bệnh viện gần nhất.

    address: địa chỉ tiếng Việt, ví dụ: "Nguyễn Trãi, Thanh Xuân"
    """
    # 1. Geocode địa chỉ sang lat/lon
    lat, lon = geocode_address(address, default_city=place_name)
    if lat is None or lon is None:
        print("Không thể tạo route do geocode thất bại.")
        # báo lỗi / st.error / print warning...
        return
    # 2. Gọi lại hàm route cũ dùng lat/lon
    if save_html is None:
        save_html = OUTPUT_DIR / "route_from_address.html"

    return build_route_map_to_nearest_hospital(
        origin_lat=lat,
        origin_lon=lon,
        place_name=place_name,
        graphml_path=graphml_path,
        csv_path=csv_path,
        save_html=save_html,
    )
