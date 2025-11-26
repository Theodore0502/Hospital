
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def preprocess_hospitals(input_csv: str | None = None,
                         output_csv: str | None = None) -> None:
    """Tiền xử lý dữ liệu bệnh viện.

    Các bước cơ bản:
    - Đọc CSV gốc
    - Loại bỏ bản ghi thiếu toạ độ
    - Loại bỏ trùng lặp theo tên + toạ độ
    - Lưu ra file mới
    """
    if input_csv is None:
        input_csv = DATA_DIR / "hospitals_clean.csv"
    else:
        input_csv = Path(input_csv)

    if output_csv is None:
        output_csv = DATA_DIR / "hospitals_preprocessed.csv"
    else:
        output_csv = Path(output_csv)

    print("Đang đọc dữ liệu từ:", input_csv)
    df = pd.read_csv(input_csv)

    # Bỏ các hàng thiếu lat / lon
    df = df.dropna(subset=["lat", "lon"])

    # Bỏ trùng lặp
    df = df.drop_duplicates(subset=["name", "lat", "lon"])

    df.to_csv(output_csv, index=False)
    print("Đã lưu dữ liệu tiền xử lý vào:", output_csv)


if __name__ == "__main__":
    preprocess_hospitals()
