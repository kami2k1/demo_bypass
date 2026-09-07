"""Assembles the chapter modules into one validated, queryable curriculum."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache

from app.content.chapters import CHAPTER_MODULES
from app.content.demos import DEMOS
from app.content.models import Chapter, Demo, Lesson

MINIMUM_LESSONS = 100


class ContentError(RuntimeError):
    """Raised when the authored content violates a structural rule."""


@dataclass(frozen=True, slots=True)
class Curriculum:
    chapters: tuple[Chapter, ...]
    lessons: tuple[Lesson, ...]
    demos: tuple[Demo, ...]
    _by_slug: dict[str, Lesson]
    _chapter_by_slug: dict[str, Chapter]
    _tags: dict[str, tuple[Lesson, ...]]

    @property
    def lesson_count(self) -> int:
        return len(self.lessons)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    @property
    def sample_count(self) -> int:
        return sum(len(lesson.samples) for lesson in self.lessons)

    @property
    def code_line_count(self) -> int:
        return sum(s.line_count for lesson in self.lessons for s in lesson.samples)

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(sorted(self._tags))

    def lesson(self, slug: str) -> Lesson | None:
        return self._by_slug.get(slug)

    def chapter(self, slug: str) -> Chapter | None:
        return self._chapter_by_slug.get(slug)

    def demo(self, slug: str) -> Demo | None:
        return next((demo for demo in self.demos if demo.slug == slug), None)

    def lessons_for_tag(self, tag: str) -> tuple[Lesson, ...]:
        return self._tags.get(tag, ())

    def tag_counts(self) -> tuple[tuple[str, int], ...]:
        counts = ((tag, len(lessons)) for tag, lessons in self._tags.items())
        return tuple(sorted(counts, key=lambda item: (-item[1], item[0])))

    def neighbours(self, lesson: Lesson) -> tuple[Lesson | None, Lesson | None]:
        index = lesson.number - 1
        previous = self.lessons[index - 1] if index > 0 else None
        following = self.lessons[index + 1] if index + 1 < len(self.lessons) else None
        return previous, following

    def level_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for lesson in self.lessons:
            counts[lesson.level] = counts.get(lesson.level, 0) + 1
        return counts

    def featured(self, limit: int = 6) -> tuple[Lesson, ...]:
        """First lesson of each chapter: a natural entry point per topic."""
        picks = [chapter.lessons[0] for chapter in self.chapters]
        return tuple(picks[:limit])


def _numbered_chapters() -> tuple[tuple[Chapter, ...], tuple[Lesson, ...]]:
    chapters: list[Chapter] = []
    lessons: list[Lesson] = []
    counter = 0
    for module in CHAPTER_MODULES:
        chapter = module.CHAPTER
        numbered: list[Lesson] = []
        for lesson in chapter.lessons:
            counter += 1
            numbered.append(
                replace(
                    lesson,
                    chapter_slug=chapter.slug,
                    chapter_title=chapter.title,
                    number=counter,
                )
            )
        chapters.append(chapter.with_lessons(numbered))
        lessons.extend(numbered)
    return tuple(chapters), tuple(lessons)


def _validate(chapters: tuple[Chapter, ...], lessons: tuple[Lesson, ...]) -> None:
    if len(lessons) < MINIMUM_LESSONS:
        raise ContentError(
            f"curriculum needs at least {MINIMUM_LESSONS} lessons, found {len(lessons)}"
        )

    seen_lessons: set[str] = set()
    for lesson in lessons:
        if lesson.slug in seen_lessons:
            raise ContentError(f"duplicate lesson slug {lesson.slug!r}")
        seen_lessons.add(lesson.slug)

    seen_chapters: set[str] = set()
    for chapter in chapters:
        if chapter.slug in seen_chapters:
            raise ContentError(f"duplicate chapter slug {chapter.slug!r}")
        seen_chapters.add(chapter.slug)

    seen_demos: set[str] = set()
    for demo in DEMOS:
        if demo.slug in seen_demos:
            raise ContentError(f"duplicate demo slug {demo.slug!r}")
        seen_demos.add(demo.slug)
        if demo.related_lesson not in seen_lessons:
            raise ContentError(
                f"demo {demo.slug!r} points at unknown lesson {demo.related_lesson!r}"
            )


@lru_cache(maxsize=1)
def load_curriculum() -> Curriculum:
    chapters, lessons = _numbered_chapters()
    _validate(chapters, lessons)

    tags: dict[str, list[Lesson]] = {}
    for lesson in lessons:
        for tag in lesson.tags:
            tags.setdefault(tag, []).append(lesson)

    return Curriculum(
        chapters=chapters,
        lessons=lessons,
        demos=DEMOS,
        _by_slug={lesson.slug: lesson for lesson in lessons},
        _chapter_by_slug={chapter.slug: chapter for chapter in chapters},
        _tags={tag: tuple(items) for tag, items in sorted(tags.items())},
    )
