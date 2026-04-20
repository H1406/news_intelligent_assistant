import sports_news_assistant.processing.keywords as keywords_module
from sports_news_assistant.processing.keywords import _is_meaningful_keyword, extract_keywords


def test_extract_keywords_returns_ranked_terms():
    texts = [
        "Vietnam won an important football match in the regional tournament.",
        "The football team continued strong form with another win.",
    ]

    keywords = extract_keywords(texts, top_n=5)

    assert keywords
    assert all("keyword" in item and "score" in item for item in keywords)


def test_is_meaningful_keyword_drops_generic_noise_terms():
    assert not _is_meaningful_keyword("đội")
    assert not _is_meaningful_keyword("http://example.com")
    assert not _is_meaningful_keyword("12")
    assert _is_meaningful_keyword("champions league")


def test_extract_keywords_applies_llm_filter_when_available(monkeypatch):
    texts = [
        "Arsenal beat Tottenham in a Premier League derby and Odegaard scored.",
        "Manchester City are chasing Arsenal in the Premier League title race.",
        "Arsenal prepare for a Champions League knockout tie this week.",
    ]

    def fake_llm_selector(candidates: list[str], model_id: str) -> set[str]:
        assert model_id == "mock-model"
        return {"arsenal", "premier league", "champions league"} & set(candidates)

    monkeypatch.setattr(keywords_module, "_select_keywords_with_llm", fake_llm_selector)
    keywords = extract_keywords(
        texts,
        top_n=4,
        llm_filter_model_id="mock-model",
        llm_filter_max_candidates=10,
    )

    assert keywords
    assert keywords[0]["keyword"] in {"arsenal", "premier league", "champions league"}


def test_extract_keywords_falls_back_when_llm_filter_returns_empty(monkeypatch):
    texts = [
        "Arsenal beat Tottenham in a Premier League derby and Odegaard scored.",
        "Manchester City are chasing Arsenal in the Premier League title race.",
        "Arsenal prepare for a Champions League knockout tie this week.",
    ]

    baseline = extract_keywords(texts, top_n=5)
    monkeypatch.setattr(keywords_module, "_select_keywords_with_llm", lambda candidates, model_id: set())

    with_llm = extract_keywords(
        texts,
        top_n=5,
        llm_filter_model_id="mock-model",
        llm_filter_max_candidates=10,
    )

    assert with_llm == baseline
