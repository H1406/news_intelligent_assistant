from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    model_id: str = os.getenv("SPORTS_NEWS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
    enable_llm_keyword_filter: bool = os.getenv("SPORTS_NEWS_ENABLE_LLM_KEYWORD_FILTER", "false").lower() == "true"
    llm_keyword_filter_model_id: str = os.getenv("SPORTS_NEWS_KEYWORD_FILTER_MODEL_ID", "")
    llm_keyword_filter_max_candidates: int = int(os.getenv("SPORTS_NEWS_KEYWORD_FILTER_MAX_CANDIDATES", "30"))
    lookback_days: int = int(os.getenv("SPORTS_NEWS_LOOKBACK_DAYS", "7"))
    max_articles: int = int(os.getenv("SPORTS_NEWS_MAX_ARTICLES", "60"))
    request_timeout: int = int(os.getenv("SPORTS_NEWS_REQUEST_TIMEOUT", "20"))
    enable_selenium_fallback: bool = os.getenv("ENABLE_SELENIUM_FALLBACK", "false").lower() == "true"
    database_path: str = os.getenv("SPORTS_NEWS_DB_PATH", str(Path("data") / "sports_news.db"))
    report_dir: str = os.getenv("SPORTS_NEWS_REPORT_DIR", "reports")

    @property
    def rss_sources(self) -> dict[str, str]:
        return {
            "VnExpress": "https://vnexpress.net/rss/the-thao.rss",
            "Thanh Nien": "https://thanhnien.vn/rss/the-thao.rss",
            "Tuoi Tre": "https://tuoitre.vn/rss/the-thao.rss",
        }


def get_settings() -> Settings:
    settings = Settings()
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.report_dir).mkdir(parents=True, exist_ok=True)
    return settings
