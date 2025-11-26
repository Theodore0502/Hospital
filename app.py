import streamlit as st
from pathlib import Path

from src.fetch_data import fetch_hospital_data
from src.preprocess import preprocess_hospitals
from src.build_map import build_map
from src.routing import route_from_address

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Hospital Accessibility Mapping",
    layout="wide",
)

st.title("Hospital Accessibility Mapping – Hà Nội")

# --- Sidebar: chuẩn bị dữ liệu OSM ---
st.sidebar.header("Cấu hình dữ liệu")
place_name = st.sidebar.text_input(
    "Khu vực phân tích",
    value="Hanoi, Vietnam",
    help="Có thể đổi sang khu vực khác nếu muốn."
)

if st.sidebar.button("Tải / cập nhật dữ liệu bệnh viện từ OSM"):
    with st.spinner("Đang tải dữ liệu bệnh viện và xây dựng bản đồ..."):
        fetch_hospital_data(place_name)
        preprocess_hospitals()
        build_map()
    st.sidebar.success("Đã cập nhật dữ liệu & tạo hospital_map.html")


st.markdown("### Nhập địa chỉ để tìm bệnh viện gần nhất và tuyến đường")

address = st.text_input(
    "Địa chỉ xuất phát",
    value="Ngõ 90 Khuất Duy Tiến, Thanh Xuân",
    help="Ví dụ: 'Ngõ 90 Khuất Duy Tiến, Thanh Xuân'"
)

run_button = st.button("Tính đường đi tới bệnh viện gần nhất")

if run_button:
    if not address.strip():
        st.warning("Vui lòng nhập địa chỉ hợp lệ.")
    else:
        with st.spinner("Đang geocode địa chỉ, tìm bệnh viện gần nhất và tính tuyến đường..."):
            result = route_from_address(
                address=address,
                place_name=place_name,
            )

        if result is None:
            st.error("Không geocode được địa chỉ này. Hãy thử ghi cụ thể hơn (thêm quận/phường).")
        else:
            html_path, nearest = result

            st.subheader("Bệnh viện gần nhất")
            st.write(f"**Tên:** {nearest.name}")

            # địa chỉ nếu có
            parts = []
            if isinstance(nearest.street, str):
                parts.append(nearest.street)
            if isinstance(nearest.city, str):
                parts.append(nearest.city)
            if parts:
                st.write("**Địa chỉ:**", ", ".join(parts))

            st.write(f"**Khoảng cách đường chim bay:** {nearest.distance_km:.2f} km")

            # Nhúng map HTML
            html = Path(html_path).read_text(encoding="utf-8")
            st.subheader("🗺️ Bản đồ tuyến đường")
            st.components.v1.html(html, height=600, scrolling=True)

            st.info(
                "Bạn có thể sửa địa chỉ ở ô trên và bấm lại nút để xem tuyến đường mới. "
                "Mỗi lần bấm sẽ vẽ lại map với địa chỉ mới."
            )
