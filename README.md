
# Hospital Accessibility Mapping (HospitalGIS)

python -m src.routing

Đề tài: **Phân tích khả năng tiếp cận bệnh viện** bằng hệ thống bản đồ tương tác.

## 1. Mục tiêu

- Hiển thị toàn bộ bệnh viện trong một khu vực (ví dụ: TP. Hồ Chí Minh).
- Phân tích khả năng tiếp cận (vùng phục vụ theo bán kính).
- Tạo heatmap mật độ bệnh viện.
- Tính khoảng cách từ một điểm bất kỳ đến bệnh viện gần nhất.

## 2. Cấu trúc thư mục

```text
HospitalGIS/
│
├── data/
│   ├── hospitals_raw.geojson      # (tuỳ chọn, nếu muốn lưu raw OSM)
│   ├── hospitals_clean.csv        # từ fetch_data.py
│   └── hospitals_preprocessed.csv # sau tiền xử lý
│
├── src/
│   ├── fetch_data.py        # tải + lưu OSM data
│   ├── preprocess.py        # xử lý dữ liệu
│   ├── build_map.py         # tạo bản đồ folium (marker + heatmap)
│   ├── analysis.py          # tính khoảng cách, buffer vùng phục vụ
│   └── utils.py             # hàm phụ trợ
│
├── output/
│   ├── hospital_map.html           # bản đồ tương tác
│   └── hospital_service_areas.geojson  # vùng phục vụ (buffer)
│
├── main.py
└── requirements.txt
```

## 3. Cài đặt môi trường

Khuyên dùng Python 3.10 và `venv` hoặc `conda`.

```bash
pip install -r requirements.txt
```

hoặc với conda:

```bash
conda create -n hospitalgis python=3.10
conda activate hospitalgis
pip install -r requirements.txt
```

## 4. Chạy nhanh toàn bộ pipeline

```bash
python main.py
```

Các bước bên trong:

1. `src/fetch_data.py` tải dữ liệu bệnh viện từ OSM cho khu vực
   mặc định là **Ho Chi Minh City, Vietnam** và lưu vào
   `data/hospitals_clean.csv`.
2. `src/preprocess.py` làm sạch dữ liệu và lưu vào
   `data/hospitals_preprocessed.csv`.
3. `src/build_map.py` tạo bản đồ Folium và lưu vào
   `output/hospital_map.html`.
4. `src/analysis.py` được dùng để tính khoảng cách tới bệnh viện gần nhất
   và tạo buffer vùng phục vụ.

Mở file `output/hospital_map.html` trong trình duyệt để xem bản đồ.

## 5. Chạy từng bước thủ công (tuỳ chọn)

```bash
# 1. Tải dữ liệu OSM
python src/fetch_data.py

# 2. Tiền xử lý
python src/preprocess.py

# 3. Tạo bản đồ
python src/build_map.py

# 4. Tạo buffer vùng phục vụ 2km
python src/analysis.py
```

Hoặc import các hàm trong notebook Jupyter để trình bày demo.

## 6. Ghi chú

- Dự án dùng dữ liệu **OpenStreetMap** qua thư viện `osmnx` nên:
  - Miễn phí, cập nhật thường xuyên.
  - Không cần API key.
  - Tự động có toạ độ (lat, lon).
- Nếu muốn đổi khu vực, chỉ cần sửa tham số `place_name` trong
  `fetch_hospital_data` (file `src/fetch_data.py`).
