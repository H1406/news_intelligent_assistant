from __future__ import annotations


def build_dashboard_metrics(articles: list[dict]) -> dict:
    sources = sorted({article["source"] for article in articles})
    dates = sorted({article["published_date"] for article in articles})
    return {
        "article_count": len(articles),
        "source_count": len(sources),
        "date_count": len(dates),
    }
