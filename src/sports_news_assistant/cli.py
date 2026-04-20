from __future__ import annotations

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Sports News Intelligent Assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the sports news pipeline")
    run_parser.add_argument("--days", type=int, default=None, help="Lookback window in days")
    run_parser.add_argument("--max-articles", type=int, default=None, help="Maximum number of articles to analyze")

    args = parser.parse_args()

    if args.command == "run":
        from sports_news_assistant.pipeline import run_pipeline

        result = run_pipeline(lookback_days=args.days, max_articles=args.max_articles)
        print(
            json.dumps(
                {
                    "articles": len(result["articles"]),
                    "keywords": result["keywords"],
                    "report_path": result.get("report_path"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
