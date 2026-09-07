"""Small constructors that keep the chapter modules readable."""

from __future__ import annotations

from app.content.models import Chapter, CodeSample, Lesson, Section


def sec(heading: str, *paragraphs: str, note: str | None = None) -> Section:
    return Section(heading=heading, paragraphs=tuple(paragraphs), note=note)


def code(
    title: str,
    body: str,
    *,
    output: str | None = None,
    explanation: str | None = None,
    language: str = "go",
) -> CodeSample:
    return CodeSample(
        title=title,
        code=body.strip("\n"),
        language=language,
        output=output.strip("\n") if output else None,
        explanation=explanation,
    )


def lesson(
    *,
    slug: str,
    title: str,
    summary: str,
    level: str,
    tags: list[str],
    sections: list[Section],
    samples: list[CodeSample],
    takeaways: list[str],
    exercises: list[str] | None = None,
) -> Lesson:
    return Lesson(
        slug=slug,
        title=title,
        summary=summary,
        level=level,
        tags=tuple(tags),
        sections=tuple(sections),
        samples=tuple(samples),
        takeaways=tuple(takeaways),
        exercises=tuple(exercises or ()),
    )


def chapter(*, slug: str, title: str, summary: str, lessons: list[Lesson]) -> Chapter:
    return Chapter(slug=slug, title=title, summary=summary, lessons=tuple(lessons))
