"""Các trang học: lộ trình, chương, bài học, thẻ."""

from __future__ import annotations

from flask import Blueprint, abort, render_template

from app.content.models import LEVELS, Lesson
from app.content.registry import Curriculum, load_curriculum

learn_bp = Blueprint("learn", __name__)


@learn_bp.route("/lo-trinh")
def curriculum() -> str:
    data = load_curriculum()
    return render_template("curriculum.html", curriculum=data, levels=LEVELS)


@learn_bp.route("/chapters/<slug>")
def chapter_detail(slug: str) -> str:
    data = load_curriculum()
    chapter = data.chapter(slug)
    if chapter is None:
        abort(404)

    index = data.chapters.index(chapter)
    return render_template(
        "chapter.html",
        chapter=chapter,
        previous=data.chapters[index - 1] if index > 0 else None,
        following=data.chapters[index + 1] if index + 1 < len(data.chapters) else None,
        number=index + 1,
    )


@learn_bp.route("/lessons/<slug>")
def lesson_detail(slug: str) -> str:
    data = load_curriculum()
    lesson = data.lesson(slug)
    if lesson is None:
        abort(404)

    previous, following = data.neighbours(lesson)
    return render_template(
        "lesson.html",
        lesson=lesson,
        chapter=data.chapter(lesson.chapter_slug),
        previous=previous,
        following=following,
        related=_related(data, lesson),
    )


@learn_bp.route("/tags")
def tag_index() -> str:
    return render_template("tag_index.html", tag_counts=load_curriculum().tag_counts())


@learn_bp.route("/tags/<tag>")
def tag_detail(tag: str) -> str:
    data = load_curriculum()
    lessons = data.lessons_for_tag(tag)
    if not lessons:
        abort(404)
    return render_template("tag_detail.html", tag=tag, lessons=lessons)


def _related(data: Curriculum, lesson: Lesson, limit: int = 4) -> list[Lesson]:
    """Bài khác chia sẻ nhiều thẻ nhất với bài hiện tại."""
    tags = set(lesson.tags)
    scored = [
        (len(tags & set(other.tags)), other)
        for other in data.lessons
        if other.slug != lesson.slug and tags & set(other.tags)
    ]
    scored.sort(key=lambda item: (-item[0], item[1].number))
    return [other for _, other in scored[:limit]]
