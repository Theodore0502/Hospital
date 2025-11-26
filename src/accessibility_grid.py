# src/accessibility_grid.py
from __future__ import annotations

from pathlib import Path

import folium
import numpy as np
from folium.plugins import Fullscreen, MeasureControl, MiniMap, HeatMap, Search
from branca.element import Template, MacroElement

try:
    from .analysis import load_hospitals, _haversine
except ImportError:
    from analysis import load_hospitals, _haversine

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
#  Hỗ trợ tính khoảng cách & chọn màu theo khoảng cách
# ---------------------------------------------------------
def _min_distance_to_hospital(lat: float, lon: float, hospitals_df) -> float:
    distances = hospitals_df.apply(
        lambda row: _haversine(lat, lon, row.lat, row.lon),
        axis=1,
    )
    return float(distances.min())


def _distance_to_color(d_km: float) -> str:
    if d_km <= 1:
        return "#1a9850"
    elif d_km <= 2:
        return "#66bd63"
    elif d_km <= 3:
        return "#fee08b"
    elif d_km <= 4:
        return "#f46d43"
    else:
        return "#d73027"


# ---------------------------------------------------------
# LEGEND
# ---------------------------------------------------------
def add_distance_legend(m):
    template = """
    {% macro html(this, kwargs) %}
    <div style="
        position: fixed;
        bottom: 40px;
        left: 40px;
        z-index: 9999;
        background-color: white;
        padding: 10px 12px;
        border: 2px solid #444;
        border-radius: 5px;
        box-shadow: 0 0 8px rgba(0,0,0,0.2);
        font-size: 12px;
    ">
      <div style="font-weight: bold; margin-bottom: 4px;">
        Khoảng cách tới bệnh viện
      </div>

      <div style="display: flex; align-items: center; margin-bottom: 2px;">
        <div style="width: 12px; height: 12px; background: #1a9850; margin-right: 6px;"></div>
        <span>Vùng rất gần (&lt; 1 km)</span>
      </div>

      <div style="display: flex; align-items: center; margin-bottom: 2px;">
        <div style="width: 12px; height: 12px; background: #fee08b; margin-right: 6px;"></div>
        <span>Vùng trung bình (1–3 km)</span>
      </div>

      <div style="display: flex; align-items: center;">
        <div style="width: 12px; height: 12px; background: #d73027; margin-right: 6px;"></div>
        <span>Vùng xa (&gt; 3 km)</span>
      </div>
    </div>
    {% endmacro %}
    """
    macro = MacroElement()
    macro._template = Template(template)
    m.get_root().add_child(macro)


# ---------------------------------------------------------
#  BUILD MAP
# ---------------------------------------------------------
def build_accessibility_grid_map(
    csv_path=None,
    save_html=None,
    grid_size=25,
    refine_factor=5,
):
    hospitals = load_hospitals(csv_path)
    hospitals = hospitals.dropna(subset=["lat", "lon"])

    min_lat = hospitals.lat.min()
    max_lat = hospitals.lat.max()
    min_lon = hospitals.lon.min()
    max_lon = hospitals.lon.max()

    n_lat = grid_size * refine_factor
    n_lon = grid_size * refine_factor

    lat_edges = np.linspace(min_lat, max_lat, n_lat + 1)
    lon_edges = np.linspace(min_lon, max_lon, n_lon + 1)

    center_lat = hospitals.lat.mean()
    center_lon = hospitals.lon.mean()

    # BASE MAP
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="cartodbpositron")

    # ---------------------------------------------------------
    #  Layer Bệnh viện + Tìm kiếm nâng cao
    # ---------------------------------------------------------
    fg_hospitals = folium.FeatureGroup(name="Bệnh viện", show=True)
    geo_features = []

    COMMON_PREFIXES = [
        "bệnh viện ", "benh vien ", "phòng khám ", "phong kham ",
        "trung tâm ", "trung tam ",
    ]

    for _, row in hospitals.iterrows():
        name = row["name"]
        street = row.get("street", "")
        city = row.get("city", "")
        lat, lon = float(row.lat), float(row.lon)

        # tạo popup
        address = ", ".join([p for p in [street, city] if isinstance(p, str) and p])
        popup_html = f"<b>{name}</b><br>{address}"

        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(fg_hospitals)

        # -------- SEARCH TEXT --------
        lower_name = name.lower()
        core = lower_name.replace("đa khoa ", "").replace("da khoa ", "")

        core_stripped = core
        for prefix in COMMON_PREFIXES:
            if core_stripped.startswith(prefix):
                core_stripped = core_stripped[len(prefix):]
                break
        core_stripped = core_stripped.strip()

        variations = set([name, lower_name])

        if core_stripped:
            variations.update([
                core_stripped, core_stripped.title(),
                f"phòng khám {core_stripped}",
                f"Phòng khám {core_stripped.title()}",
                f"bệnh viện {core_stripped}",
                f"Bệnh viện {core_stripped.title()}",
            ])

        search_text = " | ".join(sorted(variations))

        geo_features.append({
            "type": "Feature",
            "properties": {
                "name": name,
                "address": address,
                "search_text": search_text,
            },
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
        })

    fg_hospitals.add_to(m)

    gj = folium.GeoJson({"type": "FeatureCollection", "features": geo_features})
    gj.add_to(m)

    Search(
        layer=gj,
        search_label="search_text",
        placeholder="Tìm bệnh viện (vd: linh đàm)",
        collapsed=False,
        min_len=2,
    ).add_to(m)

    # ---------------------------------------------------------
    #  Layer GRID
    # ---------------------------------------------------------
    fg_grid = folium.FeatureGroup(name="Vùng gần/xa bệnh viện (grid)", show=False)

    print(f"Đang tính lưới {n_lat} x {n_lon} ...")

    for i in range(n_lat):
        lat_min, lat_max = lat_edges[i], lat_edges[i + 1]
        lat_c = (lat_min + lat_max) / 2

        for j in range(n_lon):
            lon_min, lon_max = lon_edges[j], lon_edges[j + 1]
            lon_c = (lon_min + lon_max) / 2

            d = _min_distance_to_hospital(lat_c, lon_c, hospitals)
            color = _distance_to_color(d)

            folium.Rectangle(
                bounds=[[lat_min, lon_min], [lat_max, lon_max]],
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=0
            ).add_to(fg_grid)

    fg_grid.add_to(m)

    # ---------------------------------------------------------
    #  Layer HEATMAP DENSITY
    # ---------------------------------------------------------
    fg_heat = folium.FeatureGroup(name="Mật độ bệnh viện (heatmap)", show=False)
    heat_data = hospitals[["lat", "lon"]].values.tolist()

    HeatMap(heat_data, radius=18, blur=25).add_to(fg_heat)
    fg_heat.add_to(m)

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------
    Fullscreen().add_to(m)
    MeasureControl(primary_length_unit="kilometers").add_to(m)
    MiniMap(toggle_display=True).add_to(m)

    add_distance_legend(m)
    folium.LayerControl(collapsed=False).add_to(m)

    if not save_html:
        save_html = OUTPUT_DIR / "hospital_accessibility_grid.html"
    else:
        save_html = Path(save_html)

    m.save(save_html)
    print("Đã tạo:", save_html)
    return save_html


if __name__ == "__main__":
    build_accessibility_grid_map()
