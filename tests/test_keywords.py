from sports_news_assistant.processing.keywords import extract_keywords


def test_extract_keywords_returns_ranked_terms():
    texts = [
        "Vietnam won an important football match in the regional tournament.",
        "The football team continued strong form with another win.",
    ]

    keywords = extract_keywords(texts, top_n=5)

    assert keywords
    assert all("keyword" in item and "score" in item for item in keywords)
