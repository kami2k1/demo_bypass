"""Chapter modules in curriculum order.

The list is explicit on purpose: ordering drives lesson numbering and the
previous/next navigation, so it should never depend on filesystem iteration.
"""

from __future__ import annotations

from types import ModuleType

from app.content.chapters import (
    ch01_khoi_dau,
    ch02_co_ban,
    ch03_du_lieu,
    ch04_interface,
    ch05_loi,
    ch06_dong_thoi,
    ch07_thu_vien_chuan,
    ch08_web,
    ch09_du_lieu_ngoai,
    ch10_kiem_thu,
    ch11_hieu_nang,
    ch12_van_hanh,
)

CHAPTER_MODULES: tuple[ModuleType, ...] = (
    ch01_khoi_dau,
    ch02_co_ban,
    ch03_du_lieu,
    ch04_interface,
    ch05_loi,
    ch06_dong_thoi,
    ch07_thu_vien_chuan,
    ch08_web,
    ch09_du_lieu_ngoai,
    ch10_kiem_thu,
    ch11_hieu_nang,
    ch12_van_hanh,
)
