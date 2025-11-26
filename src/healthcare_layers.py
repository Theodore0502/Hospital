# src/healthcare_layers.py
from __future__ import annotations

from pathlib import Path
import folium
import pandas as pd

try:
    from .analysis import load_hospitals
except ImportError:
    from analysis import load_hospitals

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# PHÂN TẦNG HỆ THỐNG Y TẾ — DÀNH RIÊNG CHO DATASET CỦA BẠN
# ---------------------------------------------------------
def classify_healthcare(name: str | None) -> str:
    name = str(name or "").lower()

    # ---- Hospital (Bệnh viện – Hospital) ----
    kw_hospital = [
        "bệnh viện", "bv ", " bv ", "hospital", "viện", "đa khoa",
        "trung ương", "quân y", "quốc tế", "tâm thần", "da liễu",
        "phổi", "tim", "ung bướu", "chấn thương", "vinmec", "tci",
    ]
    if any(k in name for k in kw_hospital):
        return "Hospital"

    # ---- Clinic (Phòng khám / nhà hộ sinh / nha khoa) ----
    kw_clinic = [
        "phòng khám", "phòng kh", "clinic", "đa khoa", "nha khoa",
        "nhà hộ sinh", "sản", "nhi", "medlatec", "linh đàm",
    ]
    if any(k in name for k in kw_clinic):
        return "Clinic"

    # ---- Health Center (Trạm Y Tế / Trung Tâm Y Tế) ----
    kw_center = [
        "trạm y tế", "trạm y te", "trung tâm y tế",
        "trung tâm y te", "y tế quận", "y tế xã", "y tế phường",
    ]
    if any(k in name for k in kw_center):
        return "Health Center"

    # ---- Other ----
    return "Other"


# ---------------------------------------------------------
# VISUAL MAP
# ---------------------------------------------------------
def build_healthcare_layer_map(csv_path: str | None = None,
                               save_html: str | None = None):

    df = load_hospitals(csv_path)
    df = df.dropna(subset=["lat", "lon"])

    center_lat = df.lat.mean()
    center_lon = df.lon.mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    # 4 lớp (layer)
    fg_hospital = folium.FeatureGroup("🏥 Bệnh viện (Hospital)", show=True)
    fg_clinic = folium.FeatureGroup("🏨 Phòng khám (Clinic)", show=True)
    fg_center = folium.FeatureGroup("🏣 Trung tâm y tế (Health Center)", show=False)
    fg_other = folium.FeatureGroup("🏪 Cơ sở y tế khác (Other)", show=False)

    for _, row in df.iterrows():
        lat, lon = float(row.lat), float(row.lon)
        name = str(row.get("name", "Không tên") or "")
        street = str(row.get("street", "") or "")
        city = str(row.get("city", "") or "")

        category = classify_healthcare(name)

        popup_html = f"""
        <b>{name}</b><br>
        <i>{street}, {city}</i><br>
        <b>Loại:</b> {category}
        """

        if category == "Hospital":
            color = "red"
            fg = fg_hospital
        elif category == "Clinic":
            color = "blue"
            fg = fg_clinic
        elif category == "Health Center":
            color = "green"
            fg = fg_center
        else:
            color = "gray"
            fg = fg_other

        folium.CircleMarker(
            location=[lat, lon],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=260),
        ).add_to(fg)

    # Add layers
    fg_hospital.add_to(m)
    fg_clinic.add_to(m)
    fg_center.add_to(m)
    fg_other.add_to(m)

    # Layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Save
    if save_html is None:
        save_html = OUTPUT_DIR / "healthcare_hierarchy.html"
    else:
        save_html = Path(save_html)

    m.save(save_html)
    print("✔ Đã tạo bản đồ phân tầng hệ thống y tế:", save_html)
    return save_html

if __name__ == "__main__":
    build_healthcare_layer_map()
