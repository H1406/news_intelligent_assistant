from __future__ import annotations

from datetime import datetime, timezone


def rank_highlights(articles: list[dict], keywords: list[dict], top_k: int = 5) -> list[dict]:
    keyword_lookup = {item["keyword"] for item in keywords}
    scored_articles: list[tuple[float, dict]] = []

    for article in articles:
        score = 0.0
        text_blob = f"{article['title']} {article.get('content', '')}".lower()

        score += sum(1.0 for keyword in keyword_lookup if keyword in text_blob)

        try:
            published = datetime.fromisoformat(article["published_at"])
            age_hours = max((datetime.now(timezone.utc) - published).total_seconds() / 3600, 1)
            score += 48 / age_hours
        except Exception:
            score += 0.5

        score += min(len(article.get("content", "")) / 800, 2.0)
        scored_articles.append((score, article))

    scored_articles.sort(key=lambda item: item[0], reverse=True)
    return [article for _, article in scored_articles[:top_k]]
