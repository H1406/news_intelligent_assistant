# Technical Report

## 1. Goal

Build a compact intelligent assistant focused on **sports news** from Vietnamese publishers. The system collects articles from the last 7 days, extracts trends, summarizes key stories, and exposes the results through both a markdown report and an interactive dashboard.

## 2. Architecture

The solution follows a simple pipeline:

1. `Ingestion`
   - Primary: RSS feeds from VnExpress, Thanh Nien, and Tuoi Tre
   - Optional fallback: Selenium for pages that require browser rendering
2. `Content Extraction`
   - Fetch article pages with `requests`
   - Parse main paragraphs using `BeautifulSoup`
3. `Storage`
   - Save normalized articles into `SQLite`
4. `Processing`
   - Deduplicate by normalized URL and title similarity
   - Extract trending keywords with `TF-IDF`
   - Rank highlight stories with a lightweight heuristic
5. `Summarization`
   - Preferred model: `Qwen/Qwen2.5-0.5B-Instruct`
   - Fallback: extractive summarization when local model loading fails
6. `Output`
   - Streamlit dashboard
   - Weekly markdown report

## 3. Design Decisions

### Why RSS first

RSS is much more stable than page-by-page scraping and is fast enough for a technical assessment. It also reduces the risk of selector breakage during evaluation.

### Why SQLite

This is a single-user take-home project, so SQLite keeps setup simple while still showing structured persistence.

### Why TF-IDF

It is easy to explain, fast to run, and good enough to surface recurring sports entities, tournaments, teams, and themes.

### Why Streamlit

It provides a clean interactive dashboard in very little code, which is a good tradeoff for a tech test.

### Why a fallback summarizer

The test explicitly asks for an LLM, so the project uses `Qwen/Qwen2.5-0.5B-Instruct`. To keep the demo resilient, it falls back to extractive summarization if the evaluator does not have the model cached locally.

## 4. Dashboard Views

- Article count and source count
- News volume by source
- News volume by publishing date
- Trending keywords table
- Highlighted articles
- Executive summary
- Full article explorer

## 5. Sample Output Structure

The markdown report contains:

- Executive Summary
- Trending Keywords
- Highlighted News

## 6. Tradeoffs

- Named entity recognition and clustering are omitted to avoid over-engineering
- Ranking is heuristic rather than model-based
- RSS coverage is prioritized over perfect full-text extraction

These tradeoffs are intentional for an internship tech test: the result is easier to run, explain, and review.
