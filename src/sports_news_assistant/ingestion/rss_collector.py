from __future__ import annotations

from datetime import datetime, timedelta, timezone

import feedparser
from dateutil import parser as date_parser


def collect_rss_entries(rss_sources: dict[str, str], lookback_days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    collected: list[dict] = []

    for source_name, rss_url in rss_sources.items():
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            published = _parse_published_at(entry)
            if published is None or published < cutoff:
                continue

            collected.append(
                {
                    "source": source_name,
                    "title": (entry.get("title") or "").strip(),
                    "url": (entry.get("link") or "").strip(),
                    "published_at": published.isoformat(),
                    "published_date": published.date().isoformat(),
                    "raw_summary": (entry.get("summary") or "").strip(),
                }
            )

    return collected


def _parse_published_at(entry: dict) -> datetime | None:
    raw_value = entry.get("published") or entry.get("updated")
    if not raw_value:
        return None

    parsed = date_parser.parse(raw_value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
