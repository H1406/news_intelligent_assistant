from sports_news_assistant.processing.report_builder import build_markdown_report
from sports_news_assistant.processing.summarizer import SportsNewsSummarizer


def test_summarize_corpus_falls_back_when_llm_output_is_noise(monkeypatch):
    monkeypatch.setattr(
        SportsNewsSummarizer,
        "_summarize_with_llm",
        lambda self, prompt, max_new_tokens: "n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
    )
    summarizer = SportsNewsSummarizer("mock-model")
    result = summarizer.summarize_corpus(
        [
            "Arsenal defeated a top rival in a crucial title race match and moved to the top position.",
            "Manchester City responded with a comeback win to keep pressure on the league leaders.",
        ]
    )

    assert result
    assert "n!!!!!!!!!!!!!!!!" not in result
    assert "Arsenal defeated" in result


def test_build_markdown_report_uses_placeholder_for_empty_executive_summary():
    content = build_markdown_report(executive_summary="   ", keywords=[], highlights=[])
    assert "No executive summary available." in content
