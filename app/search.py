"""A tiny in-memory search index: enough for a few hundred documents."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

from app.content.models import Lesson
from app.content.registry import load_curriculum

_TOKEN = re.compile(r"[a-z0-9_+#.]+")
_TITLE_WEIGHT = 8
_TAG_WEIGHT = 5
_SUMMARY_WEIGHT = 3
_BODY_WEIGHT = 1
_SNIPPET_RADIUS = 90


def tokenize(text: str) -> list[str]:
    """Tách từ khoá, bỏ các mảnh chỉ gồm dấu câu như \".\" hay \"...\"."""
    return [token for token in _TOKEN.findall(text.lower()) if any(c.isalnum() for c in token)]


@dataclass(frozen=True, slots=True)
class SearchHit:
    lesson: Lesson
    score: int
    snippet: str


@dataclass(frozen=True, slots=True)
class _Document:
    lesson: Lesson
    weights: Counter[str]
    body: str


@lru_cache(maxsize=1)
def _documents() -> tuple[_Document, ...]:
    documents: list[_Document] = []
    for lesson in load_curriculum().lessons:
        weights: Counter[str] = Counter()
        for token in tokenize(lesson.title):
            weights[token] += _TITLE_WEIGHT
        for tag in lesson.tags:
            for token in tokenize(tag):
                weights[token] += _TAG_WEIGHT
        for token in tokenize(lesson.summary):
            weights[token] += _SUMMARY_WEIGHT
        body = " ".join(
            paragraph for section in lesson.sections for paragraph in section.paragraphs
        )
        for token in tokenize(body):
            weights[token] += _BODY_WEIGHT
        documents.append(_Document(lesson=lesson, weights=weights, body=body))
    return tuple(documents)


def _snippet(document: _Document, terms: list[str]) -> str:
    haystack = document.body
    lowered = haystack.lower()
    position = next(
        (index for index in (lowered.find(term) for term in terms) if index != -1),
        -1,
    )
    if position == -1:
        return document.lesson.summary
    start = max(0, position - _SNIPPET_RADIUS)
    end = min(len(haystack), position + _SNIPPET_RADIUS)
    prefix = "…" if start > 0 else ""
    suffix = "…" if end < len(haystack) else ""
    return f"{prefix}{haystack[start:end].strip()}{suffix}"


def search(query: str, limit: int = 25) -> tuple[SearchHit, ...]:
    terms = tokenize(query)
    if not terms:
        return ()

    hits: list[SearchHit] = []
    for document in _documents():
        score = sum(document.weights.get(term, 0) for term in terms)
        if score == 0:
            continue
        hits.append(
            SearchHit(
                lesson=document.lesson,
                score=score,
                snippet=_snippet(document, terms),
            )
        )
    hits.sort(key=lambda hit: (-hit.score, hit.lesson.number))
    return tuple(hits[:limit])
