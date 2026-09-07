"""Kiểm tra nội dung HTML thực sự được render, không chỉ mã trạng thái."""

from __future__ import annotations

from flask.testing import FlaskClient

from app.content.registry import Curriculum


def test_trang_chu_co_thong_ke_dung(client: FlaskClient, curriculum: Curriculum) -> None:
    body = client.get("/").get_data(as_text=True)
    assert str(curriculum.lesson_count) in body
    assert str(curriculum.sample_count) in body
    assert f"{curriculum.chapter_count}</strong>" in body


def test_trang_chu_liet_ke_moi_chuong(client: FlaskClient, curriculum: Curriculum) -> None:
    body = client.get("/").get_data(as_text=True)
    for chapter in curriculum.chapters:
        assert chapter.title in body


def test_bai_hoc_render_du_phan(client: FlaskClient, curriculum: Curriculum) -> None:
    lesson = curriculum.lesson("goroutine-co-ban")
    body = client.get(f"/lessons/{lesson.slug}").get_data(as_text=True)

    assert lesson.title in body
    assert lesson.summary in body
    for section in lesson.sections:
        assert section.heading in body
    for takeaway in lesson.takeaways:
        assert takeaway in body
    assert 'id="vi-du"' in body
    assert 'id="ghi-nho"' in body


def test_bai_hoc_render_code_va_ket_qua(client: FlaskClient, curriculum: Curriculum) -> None:
    lesson = curriculum.lesson("hello-world-dau-tien")
    body = client.get(f"/lessons/{lesson.slug}").get_data(as_text=True)

    assert 'class="code"' in body
    assert "Xin chào, Go!" in body
    assert "code-output" in body


def test_callout_render_khi_co_note(client: FlaskClient, curriculum: Curriculum) -> None:
    lesson = next(item for item in curriculum.lessons if any(s.note for s in item.sections))
    body = client.get(f"/lessons/{lesson.slug}").get_data(as_text=True)
    assert "callout" in body


def test_muc_luc_khop_so_section(client: FlaskClient, curriculum: Curriculum) -> None:
    lesson = curriculum.lessons[3]
    body = client.get(f"/lessons/{lesson.slug}").get_data(as_text=True)
    for index in range(1, len(lesson.sections) + 1):
        assert f'href="#phan-{index}"' in body


def test_code_trong_html_duoc_escape(client: FlaskClient) -> None:
    """Code mẫu chứa dấu < > phải được escape, không phá cấu trúc trang."""
    body = client.get("/lessons/channel-co-ban").get_data(as_text=True)
    assert "result &lt;- " in body
    assert "&lt;-chan int" in body
    assert "<-chan int" not in body


def test_trang_chuong_liet_ke_bai_cua_no(client: FlaskClient, curriculum: Curriculum) -> None:
    chapter = curriculum.chapters[5]
    body = client.get(f"/chapters/{chapter.slug}").get_data(as_text=True)
    for lesson in chapter.lessons:
        assert lesson.title in body


def test_trang_the_chi_liet_ke_bai_dung_the(client: FlaskClient, curriculum: Curriculum) -> None:
    tag = "generics"
    body = client.get(f"/tags/{tag}").get_data(as_text=True)
    for lesson in curriculum.lessons_for_tag(tag):
        assert lesson.title in body


def test_demo_nhung_dung_template(client: FlaskClient) -> None:
    body = client.get("/demos/goroutine-scheduler").get_data(as_text=True)
    assert "demo-scheduler" in body
    assert "work stealing" in body


def test_moi_demo_render_khoi_demo(client: FlaskClient, curriculum: Curriculum) -> None:
    for demo in curriculum.demos:
        body = client.get(f"/demos/{demo.slug}").get_data(as_text=True)
        assert 'class="demo-stage"' in body
        assert demo.title in body


def test_dieu_huong_va_footer_xuat_hien_moi_trang(client: FlaskClient) -> None:
    for path in ["/", "/lo-trinh", "/lessons/tai-sao-chon-go", "/demos"]:
        body = client.get(path).get_data(as_text=True)
        assert 'aria-label="Điều hướng chính"' in body
        assert "footer" in body
        assert "css/base.css" in body


def test_lo_trinh_liet_ke_toan_bo_bai(client: FlaskClient, curriculum: Curriculum) -> None:
    body = client.get("/lo-trinh").get_data(as_text=True)
    for lesson in curriculum.lessons:
        assert lesson.title in body
