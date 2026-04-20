from __future__ import annotations

from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit

from sports_news_assistant.config import get_settings
from sports_news_assistant.ingestion.article_fetcher import ArticleFetcher
from sports_news_assistant.ingestion.rss_collector import collect_rss_entries
from sports_news_assistant.ingestion.selenium_fallback import fetch_article_with_selenium
from sports_news_assistant.models import Article
from sports_news_assistant.processing.keywords import extract_keywords
from sports_news_assistant.processing.ranking import rank_highlights
from sports_news_assistant.processing.report_builder import build_markdown_report, write_report
from sports_news_assistant.processing.summarizer import SportsNewsSummarizer
from sports_news_assistant.storage import SQLiteStorage


def run_pipeline(lookback_days: int | None = None, max_articles: int | None = None) -> dict:
    settings = get_settings()
    lookback_days = lookback_days or settings.lookback_days
    max_articles = max_articles or settings.max_articles

    storage = SQLiteStorage(settings.database_path)
    summarizer = SportsNewsSummarizer(settings.model_id)
    fetcher = ArticleFetcher(timeout=settings.request_timeout)

    rss_entries = collect_rss_entries(settings.rss_sources, lookback_days=lookback_days)
    deduplicated = _deduplicate_entries(rss_entries)[:max_articles]

    articles: list[Article] = []
    for entry in deduplicated:
        content = ""
        try:
            content = fetcher.fetch_article_text(entry["url"])
        except Exception:
            if settings.enable_selenium_fallback:
                try:
                    content = fetch_article_with_selenium(entry["url"])
                except Exception:
                    content = entry["raw_summary"]
            else:
                content = entry["raw_summary"]

        summary = summarizer.summarize_article(content or entry["raw_summary"])
        articles.append(
            Article(
                source=entry["source"],
                title=entry["title"],
                url=entry["url"],
                published_at=entry["published_at"],
                published_date=entry["published_date"],
                raw_summary=entry["raw_summary"],
                content=content,
                summary=summary,
            )
        )

    storage.upsert_articles(articles)

    snapshot = build_analysis_snapshot(storage=storage, lookback_days=lookback_days)
    report_content = build_markdown_report(
        executive_summary=snapshot["executive_summary"],
        keywords=snapshot["keywords"],
        highlights=snapshot["highlights"],
    )
    report_path = write_report(settings.report_dir, report_content)
    snapshot["report_path"] = report_path
    return snapshot


def build_analysis_snapshot(storage: SQLiteStorage, lookback_days: int) -> dict:
    settings = get_settings()
    summarizer = SportsNewsSummarizer(settings.model_id)
    articles = storage.fetch_recent_articles(lookback_days=lookback_days)

    keywords = extract_keywords(
        [f"{article['title']} {article['content']} {article['raw_summary']}" for article in articles],
        top_n=12,
    )
    highlights = rank_highlights(articles, keywords, top_k=5)
    executive_summary = summarizer.summarize_corpus(
        [article["content"] or article["raw_summary"] or article["title"] for article in highlights]
    )

    return {
        "articles": articles,
        "keywords": keywords,
        "highlights": highlights,
        "executive_summary": executive_summary,
    }


def _deduplicate_entries(entries: list[dict]) -> list[dict]:
    unique: list[dict] = []
    seen_urls: set[str] = set()

    for entry in entries:
        normalized_url = _normalize_url(entry["url"])
        title = entry["title"].strip().lower()
        if normalized_url in seen_urls:
            continue
        if any(SequenceMatcher(None, title, item["title"].strip().lower()).ratio() > 0.92 for item in unique):
            continue

        seen_urls.add(normalized_url)
        entry["url"] = normalized_url
        unique.append(entry)

    return unique


def _normalize_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
