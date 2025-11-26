
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_map(csv_path: str | None = None,
              save_html: str | None = None,
              add_heatmap: bool = True) -> None:
    """Tạo bản đồ tương tác bệnh viện với Folium.

    - Marker từng bệnh viện
    - (Tuỳ chọn) lớp heatmap mật độ
    """        
    if csv_path is None:
        # Ưu tiên file đã tiền xử lý, nếu không có thì dùng file gốc
        preprocessed = DATA_DIR / "hospitals_preprocessed.csv"
        if preprocessed.exists():
            csv_path = preprocessed
        else:
            csv_path = DATA_DIR / "hospitals_clean.csv"
    else:
        csv_path = Path(csv_path)

    if save_html is None:
        save_html = OUTPUT_DIR / "hospital_map.html"
    else:
        save_html = Path(save_html)

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("Dữ liệu bệnh viện trống, hãy kiểm tra file CSV.")

    center = [df.lat.mean(), df.lon.mean()]
    m = folium.Map(location=center, zoom_start=12)

    # Lớp marker
    for _, row in df.iterrows():
        popup_html = f"<b>{row.get('name', 'No name')}</b><br>"
        if not pd.isna(row.get("street")):
            popup_html += str(row.get("street"))
        if not pd.isna(row.get("city")):
            popup_html += f", {row.get('city')}"

        folium.Marker(
            location=[row.lat, row.lon],
            popup=popup_html,
            icon=folium.Icon(color="red", icon="plus-sign"),
        ).add_to(m)

    # Lớp heatmap
    if add_heatmap:
        heat_data = df[["lat", "lon"]].dropna().values.tolist()
        HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)

    m.save(save_html)
    print("Đã tạo bản đồ:", save_html)

if __name__ == "__main__":
    build_map()
