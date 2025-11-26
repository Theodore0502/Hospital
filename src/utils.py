# src/utils.py
from __future__ import annotations

from pathlib import Path
from typing import Tuple
import unicodedata

import osmnx as ox


def ensure_dir(path: str | Path) -> Path:
    """Tạo thư mục nếu chưa tồn tại và trả về Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt, trả về chuỗi ASCII (dùng cho fallback geocode)."""
    text_norm = unicodedata.normalize("NFD", text)
    return "".join(
        ch for ch in text_norm
        if unicodedata.category(ch) != "Mn"
    )


def _has_city(text: str, default_city: str) -> bool:
    """Kiểm tra xem trong text đã có city hay chưa (so sánh dạng bỏ dấu, lower)."""
    t = _strip_accents(text).lower()
    c = _strip_accents(default_city).lower()
    return c in t


def _shorten_to_last_parts(query: str, n_parts: int = 2) -> str | None:
    """Rút gọn query còn n phần cuối cùng (ngăn cách bởi dấu phẩy)."""
    parts = [p.strip() for p in query.split(",") if p.strip()]
    if len(parts) <= n_parts:
        return None
    return ", ".join(parts[-n_parts:])


def geocode_address(
    address: str,
    default_city: str = "Hanoi, Vietnam",
) -> Tuple[float | None, float | None]:
    """
    Chuyển địa chỉ text thành (lat, lon) dùng geocoder của osmnx.

    Chiến lược:
    1. Thử nguyên văn người dùng nhập.
    2. Nếu chưa có city thì thêm `default_city`.
    3. Thử bản bỏ dấu (ASCII) của query.
    4. Nếu vẫn fail, rút gọn chỉ còn phần quận/huyện + city (2 phần cuối),
       rồi thử lại (cả có dấu và bỏ dấu).

    Trả về:
        (lat, lon) nếu geocode thành công,
        (None, None) nếu thử tất cả vẫn thất bại.
    """
    raw = (address or "").strip()
    if not raw:
        print("❌ Địa chỉ trống, không thể geocode.")
        return None, None

    candidates: list[str] = []

    # 1) nguyên văn người dùng
    candidates.append(raw)

    # 2) thêm city nếu chưa có
    if not _has_city(raw, default_city):
        q_with_city = f"{raw}, {default_city}"
        if q_with_city not in candidates:
            candidates.append(q_with_city)
    else:
        q_with_city = raw

    # 3) phiên bản bỏ dấu (ASCII) của query có city
    ascii_with_city = _strip_accents(q_with_city)
    if ascii_with_city not in candidates:
        candidates.append(ascii_with_city)

    # 4) rút gọn chỉ còn 2 phần cuối (thường là “Đông Anh, Hanoi, Vietnam”)
    short_q = _shorten_to_last_parts(q_with_city, n_parts=2)
    if short_q and short_q not in candidates:
        candidates.append(short_q)

    short_q_ascii = _strip_accents(short_q) if short_q else None
    if short_q_ascii and short_q_ascii not in candidates:
        candidates.append(short_q_ascii)

    # Thử lần lượt các candidate
    for q in candidates:
        print(f"Đang geocode (thử): {q}")
        try:
            lat, lon = ox.geocode(q)
            print(f" -> OK, toạ độ: ({lat}, {lon})")
            return float(lat), float(lon)
        except Exception as e:
            print(f"   Thử với '{q}' thất bại:", e)

    print("❌ Không geocode được địa chỉ sau nhiều lần thử.")
    return None, None
