from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from sports_news_assistant.models import Article


class SQLiteStorage:
    def __init__(self, database_path: str) -> None:
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS articles (
                    url TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    raw_summary TEXT,
                    content TEXT,
                    summary TEXT
                )
                """
            )
            connection.commit()

    def upsert_articles(self, articles: Iterable[Article]) -> None:
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO articles (
                    url, source, title, published_at, published_date, raw_summary, content, summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    source=excluded.source,
                    title=excluded.title,
                    published_at=excluded.published_at,
                    published_date=excluded.published_date,
                    raw_summary=excluded.raw_summary,
                    content=excluded.content,
                    summary=excluded.summary
                """,
                [
                    (
                        article.url,
                        article.source,
                        article.title,
                        article.published_at,
                        article.published_date,
                        article.raw_summary,
                        article.content,
                        article.summary,
                    )
                    for article in articles
                ],
            )
            connection.commit()

    def fetch_recent_articles(self, lookback_days: int) -> list[dict]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT source, title, url, published_at, published_date, raw_summary, content, summary
                FROM articles
                WHERE DATE(published_date) >= DATE('now', ?)
                ORDER BY published_at DESC
                """,
                (f"-{lookback_days} day",),
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
