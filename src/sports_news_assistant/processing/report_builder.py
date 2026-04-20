from __future__ import annotations

from datetime import datetime
from pathlib import Path


def build_markdown_report(executive_summary: str, keywords: list[dict], highlights: list[dict]) -> str:
    lines = [
        "# Weekly Sports News Report",
        "",
        "## Executive Summary",
        executive_summary,
        "",
        "## Trending Keywords",
    ]

    for item in keywords:
        lines.append(f"- {item['keyword']}: {item['score']}")

    lines.extend(["", "## Highlighted News"])

    for article in highlights:
        lines.extend(
            [
                f"### {article['title']}",
                f"- Source: {article['source']}",
                f"- Published: {article['published_at']}",
                f"- Link: {article['url']}",
                f"- Summary: {article['summary']}",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


def write_report(report_dir: str, content: str) -> str:
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(report_dir) / f"sports_weekly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)
