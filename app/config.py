"""Cấu hình ứng dụng, tách theo môi trường."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Config:
    SITE_NAME: str = "Go Nhanh"
    SITE_TAGLINE: str = "Học Go qua hơn 100 bài, bài nào cũng có ví dụ chạy được"
    SECRET_KEY: str = field(default_factory=lambda: os.environ.get("SECRET_KEY", "dev-only"))
    TESTING: bool = False
    SEND_FILE_MAX_AGE_DEFAULT: int = 60 * 60 * 24
    MAX_SEARCH_RESULTS: int = 25

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TestingConfig(Config):
    TESTING: bool = True
    SEND_FILE_MAX_AGE_DEFAULT: int = 0
