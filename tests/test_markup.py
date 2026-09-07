"""Filter inline_code: vừa phải escape HTML, vừa phải hỗ trợ backtick."""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient

from app.markup import inline_code


def test_chuyen_backtick_thanh_code() -> None:
    assert str(inline_code("dùng `go build` để biên dịch")) == (
        "dùng <code>go build</code> để biên dịch"
    )


def test_nhieu_doan_code_trong_mot_cau() -> None:
    assert str(inline_code("`var` và `:=`")) == "<code>var</code> và <code>:=</code>"


def test_van_ban_khong_co_backtick_giu_nguyen() -> None:
    assert str(inline_code("không có gì đặc biệt")) == "không có gì đặc biệt"


def test_escape_html_truoc_khi_thay_the() -> None:
    result = str(inline_code("<script>alert(1)</script>"))
    assert "<script>" not in result
    assert result == "&lt;script&gt;alert(1)&lt;/script&gt;"


def test_html_ben_trong_backtick_cung_bi_escape() -> None:
    result = str(inline_code("thẻ `<img onerror=x>` bị vô hiệu"))
    assert result == "thẻ <code>&lt;img onerror=x&gt;</code> bị vô hiệu"


def test_backtick_le_khong_gay_loi() -> None:
    assert str(inline_code("một backtick ` lẻ")) == "một backtick ` lẻ"


def test_filter_duoc_dang_ky(app: Flask) -> None:
    assert "inline_code" in app.jinja_env.filters


def test_trang_bai_hoc_render_inline_code(client: FlaskClient) -> None:
    body = client.get("/lessons/goroutine-co-ban").get_data(as_text=True)
    assert "<code>go f()</code>" in body
    assert "`go f()`" not in body
