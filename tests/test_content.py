"""Kiểm tra tính toàn vẹn của nội dung: đây là nơi lỗi biên tập bị chặn."""

from __future__ import annotations

import re

import pytest

from app.content.models import LEVELS, Chapter, CodeSample, Lesson, Section
from app.content.registry import MINIMUM_LESSONS, Curriculum

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def test_dat_du_so_bai_toi_thieu(curriculum: Curriculum) -> None:
    assert curriculum.lesson_count >= MINIMUM_LESSONS


def test_so_bai_khop_tong_cac_chuong(curriculum: Curriculum) -> None:
    assert sum(len(c.lessons) for c in curriculum.chapters) == curriculum.lesson_count


def test_slug_dung_dinh_dang(curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        assert SLUG.match(lesson.slug), lesson.slug
    for chapter in curriculum.chapters:
        assert SLUG.match(chapter.slug), chapter.slug
    for demo in curriculum.demos:
        assert SLUG.match(demo.slug), demo.slug


def test_slug_khong_trung_lap(curriculum: Curriculum) -> None:
    slugs = [lesson.slug for lesson in curriculum.lessons]
    assert len(slugs) == len(set(slugs))


def test_so_thu_tu_lien_tuc(curriculum: Curriculum) -> None:
    numbers = [lesson.number for lesson in curriculum.lessons]
    assert numbers == list(range(1, curriculum.lesson_count + 1))


def test_moi_bai_thuoc_mot_chuong(curriculum: Curriculum) -> None:
    chapter_slugs = {chapter.slug for chapter in curriculum.chapters}
    for lesson in curriculum.lessons:
        assert lesson.chapter_slug in chapter_slugs
        assert lesson.chapter_title


@pytest.mark.parametrize("field", ["title", "summary"])
def test_truong_van_ban_khong_rong(curriculum: Curriculum, field: str) -> None:
    for lesson in curriculum.lessons:
        assert getattr(lesson, field).strip()


def test_moi_bai_co_du_thanh_phan(curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        assert lesson.level in LEVELS
        assert lesson.tags
        assert len(lesson.sections) >= 1
        assert len(lesson.samples) >= 1
        assert len(lesson.takeaways) >= 2


def test_moi_section_co_noi_dung(curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        for section in lesson.sections:
            assert section.heading.strip()
            assert section.paragraphs
            assert all(p.strip() for p in section.paragraphs)


def test_moi_vi_du_co_code(curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        for sample in lesson.samples:
            assert sample.code.strip()
            assert sample.line_count >= 1
            assert sample.language in {
                "go",
                "bash",
                "yaml",
                "sql",
                "html",
                "text",
                "dockerfile",
                "protobuf",
            }


def test_the_dung_dinh_dang_url(curriculum: Curriculum) -> None:
    for tag in curriculum.tags:
        assert SLUG.match(tag), tag


def test_demo_tro_toi_bai_ton_tai(curriculum: Curriculum) -> None:
    for demo in curriculum.demos:
        assert curriculum.lesson(demo.related_lesson) is not None


def test_dieu_huong_truoc_sau(curriculum: Curriculum) -> None:
    first, last = curriculum.lessons[0], curriculum.lessons[-1]
    assert curriculum.neighbours(first)[0] is None
    assert curriculum.neighbours(last)[1] is None

    middle = curriculum.lessons[5]
    previous, following = curriculum.neighbours(middle)
    assert previous.number == middle.number - 1
    assert following.number == middle.number + 1


def test_tra_cuu_theo_the_khop_du_lieu(curriculum: Curriculum) -> None:
    for tag in curriculum.tags:
        lessons = curriculum.lessons_for_tag(tag)
        assert lessons
        assert all(tag in lesson.tags for lesson in lessons)


def test_tag_counts_sap_xep_giam_dan(curriculum: Curriculum) -> None:
    counts = [count for _, count in curriculum.tag_counts()]
    assert counts == sorted(counts, reverse=True)


def test_featured_lay_bai_dau_moi_chuong(curriculum: Curriculum) -> None:
    featured = curriculum.featured(3)
    assert len(featured) == 3
    assert featured[0].slug == curriculum.chapters[0].lessons[0].slug


def test_thoi_gian_doc_hop_ly(curriculum: Curriculum) -> None:
    for lesson in curriculum.lessons:
        assert 2 <= lesson.reading_minutes <= 30


def test_mo_hinh_tu_choi_du_lieu_sai() -> None:
    with pytest.raises(ValueError):
        CodeSample(title="", code="x")
    with pytest.raises(ValueError):
        CodeSample(title="t", code="   ")
    with pytest.raises(ValueError):
        Section(heading="h", paragraphs=())
    with pytest.raises(ValueError):
        Chapter(slug="s", title="t", summary="s", lessons=())


def test_lesson_tu_choi_level_la() -> None:
    with pytest.raises(ValueError):
        Lesson(
            slug="s",
            title="t",
            summary="s",
            level="expert",
            tags=("a",),
            sections=(Section("h", ("p",)),),
            samples=(CodeSample(title="t", code="c"),),
            takeaways=("a",),
        )
