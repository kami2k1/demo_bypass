"""Mọi URL của site phải trả về 200 — bộ test này chạy qua toàn bộ hơn 100 trang."""

from __future__ import annotations

from xml.etree import ElementTree

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient

from app.content.registry import Curriculum

STATIC_ROUTES = [
    "/",
    "/lo-trinh",
    "/tags",
    "/demos",
    "/tai-sao-go",
    "/gioi-thieu",
    "/tim-kiem",
    "/sitemap",
]


@pytest.mark.parametrize("path", STATIC_ROUTES)
def test_trang_tinh_tra_ve_200(client: FlaskClient, path: str) -> None:
    assert client.get(path).status_code == 200


def test_moi_bai_hoc_tra_ve_200(client: FlaskClient, curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        response = client.get(f"/lessons/{lesson.slug}")
        assert response.status_code == 200, lesson.slug


def test_moi_chuong_tra_ve_200(client: FlaskClient, curriculum: Curriculum) -> None:
    for chapter in curriculum.chapters:
        assert client.get(f"/chapters/{chapter.slug}").status_code == 200


def test_moi_the_tra_ve_200(client: FlaskClient, curriculum: Curriculum) -> None:
    for tag in curriculum.tags:
        assert client.get(f"/tags/{tag}").status_code == 200


def test_moi_demo_tra_ve_200(client: FlaskClient, curriculum: Curriculum) -> None:
    for demo in curriculum.demos:
        assert client.get(f"/demos/{demo.slug}").status_code == 200


def test_tong_so_trang_vuot_100(curriculum: Curriculum) -> None:
    total = (
        len(STATIC_ROUTES)
        + curriculum.lesson_count
        + curriculum.chapter_count
        + len(curriculum.tags)
        + len(curriculum.demos)
    )
    assert total > 100


def test_slug_khong_ton_tai_tra_ve_404(client: FlaskClient) -> None:
    for path in [
        "/lessons/khong-co",
        "/chapters/khong-co",
        "/tags/khong-co",
        "/demos/khong-co",
    ]:
        assert client.get(path).status_code == 404


def test_trang_404_co_o_tim_kiem(client: FlaskClient) -> None:
    response = client.get("/duong-dan-la")
    assert response.status_code == 404
    assert b"404" in response.data
    assert b'name="q"' in response.data


def test_sitemap_xml_hop_le(client: FlaskClient, curriculum: Curriculum) -> None:
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert response.mimetype == "application/xml"

    root = ElementTree.fromstring(response.data)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locations = [node.text for node in root.iter(f"{namespace}loc")]

    assert len(locations) >= curriculum.lesson_count + curriculum.chapter_count
    assert all(location.startswith("http") for location in locations)


def test_sitemap_html_liet_ke_moi_bai(client: FlaskClient, curriculum: Curriculum) -> None:
    body = client.get("/sitemap").get_data(as_text=True)
    for lesson in curriculum.lessons:
        assert f"/lessons/{lesson.slug}" in body


def test_dieu_huong_truoc_sau_hien_tren_trang(client: FlaskClient, curriculum: Curriculum) -> None:
    middle = curriculum.lessons[10]
    body = client.get(f"/lessons/{middle.slug}").get_data(as_text=True)

    previous, following = curriculum.neighbours(middle)
    assert f"/lessons/{previous.slug}" in body
    assert f"/lessons/{following.slug}" in body


def test_bai_dau_khong_co_link_truoc(client: FlaskClient, curriculum: Curriculum) -> None:
    first = curriculum.lessons[0]
    body = client.get(f"/lessons/{first.slug}").get_data(as_text=True)
    assert "pager-prev" not in body


def test_url_for_khop_duong_dan_thuc(app: Flask, curriculum: Curriculum) -> None:
    with app.test_request_context():
        lesson = curriculum.lessons[0]
        assert url_for("learn.lesson_detail", slug=lesson.slug) == lesson.url_path
        chapter = curriculum.chapters[0]
        assert url_for("learn.chapter_detail", slug=chapter.slug) == chapter.url_path
        demo = curriculum.demos[0]
        assert url_for("site.demo_detail", slug=demo.slug) == demo.url_path
