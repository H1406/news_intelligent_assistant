from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from sports_news_assistant.config import get_settings
from sports_news_assistant.pipeline import build_analysis_snapshot
from sports_news_assistant.storage import SQLiteStorage


def main() -> None:
    settings = get_settings()
    storage = SQLiteStorage(settings.database_path)

    st.set_page_config(
        page_title="Sports News Dashboard",
        page_icon="📰",
        layout="wide",
    )
    st.title("Sports News Intelligent Assistant")
    st.caption("Vietnamese sports news analysis for the latest 7 days")

    with st.sidebar:
        st.header("Controls")
        days = st.slider("Lookback days", min_value=3, max_value=14, value=settings.lookback_days)
        max_articles = st.slider("Max articles", min_value=10, max_value=100, value=settings.max_articles, step=5)
        refresh = st.button("Refresh pipeline")

    if refresh:
        from sports_news_assistant.pipeline import run_pipeline

        with st.spinner("Collecting and analyzing sports news..."):
            run_pipeline(lookback_days=days, max_articles=max_articles)
        st.success("Pipeline completed.")

    snapshot = build_analysis_snapshot(storage=storage, lookback_days=days)
    articles = snapshot["articles"]

    if not articles:
        st.warning("No articles found in the local database yet. Click 'Refresh pipeline' to ingest data.")
        return

    article_df = pd.DataFrame(articles)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Articles", len(article_df))
    col2.metric("Sources", article_df["source"].nunique())
    col3.metric("Highlights", len(snapshot["highlights"]))
    col4.metric("Keywords", len(snapshot["keywords"]))

    trend_df = article_df.groupby("published_date", as_index=False)["title"].count()
    trend_df['article_count'] = trend_df['title']
    source_df = article_df.groupby("source", as_index=False)["title"].count()
    source_df['article_count'] = source_df['title']

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(source_df, x="source", y="article_count", title="Articles by source", color="source")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(trend_df, x="published_date", y="article_count", markers=True, title="Publishing trend")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Trending Keywords")
    keyword_df = pd.DataFrame(snapshot["keywords"])
    st.dataframe(keyword_df, use_container_width=True, hide_index=True)

    st.subheader("Executive Summary")
    st.write(snapshot["executive_summary"])

    st.subheader("Highlighted News")
    for item in snapshot["highlights"]:
        with st.container(border=True):
            st.markdown(f"### [{item['title']}]({item['url']})")
            st.write(f"**Source:** {item['source']} | **Published:** {item['published_at']}")
            st.write(item["summary"])

    st.subheader("Article Explorer")
    display_columns = ["source", "published_at", "title", "url", "summary"]
    st.dataframe(article_df[display_columns], use_container_width=True, hide_index=True)

    latest_report = sorted(Path(settings.report_dir).glob("sports_weekly_report_*.md"))
    if latest_report:
        st.subheader("Latest Markdown Report")
        st.code(latest_report[-1].read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
