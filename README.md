# Sports News Intelligent Assistant

Lightweight Python project for the AI Engineer Intern technical test. It collects Vietnamese sports news from RSS feeds, filters the latest 7-day articles, extracts keywords, ranks highlights, generates summaries, and shows everything in an interactive dashboard.

The implementation is intentionally simple:

- `RSS` is the primary ingestion method
- `requests + BeautifulSoup` is used to enrich article content
- `Selenium` is supported as an optional fallback for dynamic pages
- `SQLite` stores the normalized articles
- `TF-IDF` extracts trending keywords with optional LLM-based noise filtering
- `Qwen/Qwen2.5-0.5B-Instruct` is the preferred LLM for summaries
- An extractive fallback keeps the project runnable even without a local model
- `Streamlit + Plotly` provides the dashboard

## Features

- Collect sports news from:
  - VnExpress
  - Thanh Nien
  - Tuoi Tre
- Keep only articles from the last 7 days
- Remove duplicates with normalized URL and title similarity checks
- Extract trending keywords
- Rank highlighted articles using recency, source diversity, and keyword relevance
- Generate:
  - article summaries
  - executive summary
  - weekly markdown report
- Explore the data in an interactive dashboard

## Project Structure

```text
.
├── app.py
├── docs/
│   └── technical_report.md
├── reports/
│   └── .gitkeep
├── requirements.txt
├── src/
│   └── sports_news_assistant/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── pipeline.py
│       ├── storage.py
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── article_fetcher.py
│       │   ├── rss_collector.py
│       │   └── selenium_fallback.py
│       └── processing/
│           ├── __init__.py
│           ├── dashboard_metrics.py
│           ├── keywords.py
│           ├── llm_loader.py
│           ├── ranking.py
│           ├── report_builder.py
│           └── summarizer.py
└── tests/
    └── test_keywords.py
```

Keyword filtering strategy:

- Default mode keeps extraction fast: TF-IDF + stop words + heuristic cleanup.
- Optional hybrid mode (`SPORTS_NEWS_ENABLE_LLM_KEYWORD_FILTER=true`) asks the LLM to keep only meaningful candidates from the top-ranked keyword pool.
- If the LLM is unavailable or returns unusable output, the extractor automatically falls back to heuristic-only output.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run The Pipeline

Ingest the latest sports news and write the markdown report:

```bash
PYTHONPATH=src python3 -m sports_news_assistant.cli run
```

This generates:

- SQLite database at `data/sports_news.db`
- Markdown report under `reports/`

## Run The Dashboard

```bash
PYTHONPATH=src streamlit run app.py
```

The dashboard includes:

- Source distribution
- Publishing trend by date
- Top keywords
- Highlighted articles
- Generated executive summary

## Optional Selenium Support

RSS is enough for the tech test, but a Selenium fallback is included for pages that require browser rendering.

To enable it:

```bash
pip install selenium webdriver-manager
```

Then set:

```bash
export ENABLE_SELENIUM_FALLBACK=true
```

## LLM Configuration

Default summarization model:

```text
Qwen/Qwen2.5-0.5B-Instruct
```

The code tries to load the model locally with `transformers`. If model loading fails, it automatically falls back to extractive summarization so the app can still be evaluated.

Useful environment variables:

```bash
export SPORTS_NEWS_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
export SPORTS_NEWS_LOOKBACK_DAYS=7
export SPORTS_NEWS_MAX_ARTICLES=60
export SPORTS_NEWS_ENABLE_LLM_KEYWORD_FILTER=false
export SPORTS_NEWS_KEYWORD_FILTER_MODEL_ID=
export SPORTS_NEWS_KEYWORD_FILTER_MAX_CANDIDATES=30
```

## Design Notes

- `RSS first` keeps collection stable and fast
- `SQLite` is enough for a take-home test and simplifies setup
- `TF-IDF + optional LLM reranking` keeps extraction interpretable while reducing noisy generic terms
- `Streamlit` gives a quick interactive dashboard with low boilerplate
- `LLM fallback` avoids breaking the demo when a local model is unavailable

## Deliverables Included

- Source code
- Setup instructions
- Technical report in [`docs/technical_report.md`](/Users/phanhieu/news_intelligent_assistant/docs/technical_report.md)
- Sample report output path in `reports/`

## Notes

- Internet access is required to fetch fresh news from the RSS feeds and article pages.
- The project targets sports news only, as requested.
