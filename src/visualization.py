import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ========================
# Helper
# ========================
def ensure_output():
    if not os.path.exists("output"):
        os.makedirs("output")


# ========================
# 1. Scatter plot vị trí bệnh viện
# ========================
def plot_hospital_scatter(csv_path="data/hospitals_preprocessed.csv"):
    ensure_output()

    df = pd.read_csv(csv_path)

    if not {"lat", "lon"}.issubset(df.columns):
        print("[WARNING] Không có cột lat/lon. Bỏ qua scatter plot.")
        return

    plt.figure(figsize=(8, 8))
    plt.scatter(df["lon"], df["lat"], s=20, color="tomato", alpha=0.7)

    plt.title("Phân bố không gian của các bệnh viện (Scatter Plot)")
    plt.xlabel("Longitude (Kinh độ)")
    plt.ylabel("Latitude (Vĩ độ)")

    plt.tight_layout()
    plt.savefig("output/hospital_scatter.png", dpi=300)
    plt.close()
    print("✓ Đã tạo: output/hospital_scatter.png")


# ========================
# 2. Heatmap mật độ bệnh viện (2D Histogram - không cần scipy)
# ========================
def plot_hospital_heatmap(csv_path="data/hospitals_preprocessed.csv"):
    ensure_output()

    df = pd.read_csv(csv_path)

    if not {"lat", "lon"}.issubset(df.columns):
        print("[WARNING] Không có cột lat/lon. Bỏ qua heatmap.")
        return

    x = df["lon"].values
    y = df["lat"].values

    plt.figure(figsize=(8, 8))
    plt.hist2d(x, y, bins=40, cmap="Reds")

    plt.colorbar(label="Mật độ bệnh viện")
    plt.scatter(x, y, s=5, color="black", alpha=0.5)

    plt.title("Heatmap mật độ bệnh viện (2D Histogram)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    plt.tight_layout()
    plt.savefig("output/hospital_heatmap.png", dpi=300)
    plt.close()
    print("✓ Đã tạo: output/hospital_heatmap.png")


# ========================
# 3. Histogram khoảng cách (nếu có)
# ========================
def plot_distance_histogram(csv_path="output/distances.csv"):
    ensure_output()

    if not os.path.exists(csv_path):
        print("[WARNING] Không tìm thấy output/distances.csv. Bỏ qua histogram khoảng cách.")
        return

    df = pd.read_csv(csv_path)

    if "distance_km" not in df.columns:
        print("[WARNING] Không có cột distance_km.")
        return

    plt.figure(figsize=(8, 6))
    plt.hist(df["distance_km"], bins=20, color="#4C72B0")

    plt.title("Histogram khoảng cách tới bệnh viện gần nhất")
    plt.xlabel("Khoảng cách (km)")
    plt.ylabel("Số lượng")

    plt.tight_layout()
    plt.savefig("output/hist_distance_custom.png", dpi=300)
    plt.close()
    print("✓ Đã tạo: output/hist_distance_custom.png")


# ========================
# RUN ALL
# ========================
def run_all_visualizations():
    print("=== BẮT ĐẦU TRỰC QUAN HÓA (KHÔNG CẦN SCIPY) ===")

    plot_hospital_scatter()
    plot_hospital_heatmap()
    plot_distance_histogram()

    print("=== HOÀN TẤT! Hình ảnh nằm ở thư mục /output ===")


if __name__ == "__main__":
    run_all_visualizations()
