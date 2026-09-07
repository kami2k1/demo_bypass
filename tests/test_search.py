"""Chỉ mục tìm kiếm: xếp hạng, đoạn trích và các đầu vào biên."""

from __future__ import annotations

from flask.testing import FlaskClient

from app.search import search, tokenize


def test_tokenize_bo_dau_cau() -> None:
    assert tokenize("go test -race ./...") == ["go", "test", "race"]
    assert tokenize("net/http, encoding/json") == ["net", "http", "encoding", "json"]
    assert tokenize("...") == []


def test_query_rong_khong_tra_ket_qua() -> None:
    assert search("") == ()
    assert search("   ") == ()


def test_tim_theo_tu_khoa_trong_tieu_de() -> None:
    hits = search("goroutine")
    assert hits
    assert any("goroutine" in hit.lesson.title.lower() for hit in hits[:3])


def test_tieu_de_duoc_uu_tien_hon_noi_dung() -> None:
    hits = search("defer")
    top = hits[0].lesson
    assert "defer" in top.title.lower()


def test_ket_qua_sap_xep_giam_theo_diem() -> None:
    scores = [hit.score for hit in search("channel")]
    assert scores == sorted(scores, reverse=True)


def test_tim_theo_the() -> None:
    hits = search("hieu-nang")
    assert hits
    assert any("hieu-nang" in hit.lesson.tags for hit in hits)


def test_tu_khoa_khong_ton_tai() -> None:
    assert search("zzzkhongtontai") == ()


def test_gioi_han_so_ket_qua() -> None:
    assert len(search("go", limit=5)) <= 5


def test_snippet_khong_rong() -> None:
    for hit in search("interface"):
        assert hit.snippet.strip()


def test_trang_tim_kiem_hien_ket_qua(client: FlaskClient) -> None:
    body = client.get("/tim-kiem?q=goroutine").get_data(as_text=True)
    assert "kết quả cho" in body
    assert "/lessons/goroutine-co-ban" in body


def test_trang_tim_kiem_khi_khong_co_ket_qua(client: FlaskClient) -> None:
    body = client.get("/tim-kiem?q=zzzkhongtontai").get_data(as_text=True)
    assert "Không có kết quả" in body


def test_query_duoc_escape_khong_gay_xss(client: FlaskClient) -> None:
    body = client.get("/tim-kiem?q=<script>alert(1)</script>").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body
