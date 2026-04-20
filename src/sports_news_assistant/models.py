from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Article:
    source: str
    title: str
    url: str
    published_at: str
    published_date: str
    raw_summary: str
    content: str
    summary: str


@dataclass(slots=True)
class KeywordScore:
    keyword: str
    score: float
