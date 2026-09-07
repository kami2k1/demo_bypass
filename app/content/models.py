"""Immutable content types used by every page of the site."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace

LEVELS = ("beginner", "intermediate", "advanced")


@dataclass(frozen=True, slots=True)
class CodeSample:
    title: str
    code: str
    language: str = "go"
    output: str | None = None
    explanation: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("code sample needs a title")
        if not self.code.strip():
            raise ValueError(f"code sample {self.title!r} is empty")

    @property
    def line_count(self) -> int:
        return len(self.code.strip().splitlines())


@dataclass(frozen=True, slots=True)
class Section:
    heading: str
    paragraphs: tuple[str, ...]
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.heading.strip():
            raise ValueError("section needs a heading")
        if not self.paragraphs:
            raise ValueError(f"section {self.heading!r} has no paragraphs")


@dataclass(frozen=True, slots=True)
class Lesson:
    slug: str
    title: str
    summary: str
    level: str
    tags: tuple[str, ...]
    sections: tuple[Section, ...]
    samples: tuple[CodeSample, ...]
    takeaways: tuple[str, ...]
    exercises: tuple[str, ...] = ()
    chapter_slug: str = ""
    chapter_title: str = ""
    number: int = 0

    def __post_init__(self) -> None:
        if self.level not in LEVELS:
            raise ValueError(f"lesson {self.slug!r} has unknown level {self.level!r}")
        for name, value in (
            ("slug", self.slug),
            ("title", self.title),
            ("summary", self.summary),
        ):
            if not value.strip():
                raise ValueError(f"lesson field {name} must not be empty")
        if not self.sections:
            raise ValueError(f"lesson {self.slug!r} has no sections")
        if not self.samples:
            raise ValueError(f"lesson {self.slug!r} has no code samples")
        if not self.takeaways:
            raise ValueError(f"lesson {self.slug!r} has no takeaways")

    @property
    def url_path(self) -> str:
        return f"/lessons/{self.slug}"

    @property
    def reading_minutes(self) -> int:
        words = sum(len(p.split()) for s in self.sections for p in s.paragraphs)
        code_lines = sum(sample.line_count for sample in self.samples)
        return max(2, round(words / 200 + code_lines / 25))


@dataclass(frozen=True, slots=True)
class Chapter:
    slug: str
    title: str
    summary: str
    lessons: tuple[Lesson, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.lessons:
            raise ValueError(f"chapter {self.slug!r} has no lessons")

    @property
    def url_path(self) -> str:
        return f"/chapters/{self.slug}"

    def with_lessons(self, lessons: Iterable[Lesson]) -> Chapter:
        return replace(self, lessons=tuple(lessons))


@dataclass(frozen=True, slots=True)
class Demo:
    """A hand-written HTML/CSS demo rendered from its own Jinja partial."""

    slug: str
    title: str
    summary: str
    template: str
    concept: str
    related_lesson: str

    @property
    def url_path(self) -> str:
        return f"/demos/{self.slug}"
