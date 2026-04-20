from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer


SPORTS_STOP_WORDS = [
    "và",
    "của",
    "là",
    "cho",
    "với",
    "trong",
    "được",
    "những",
    "một",
    "các",
    "khi",
    "đã",
    "đang",
    "tại",
    "sau",
    "trước",
    "thể thao",
    "the thao",
]


def extract_keywords(texts: list[str], top_n: int = 10) -> list[dict]:
    documents = [text.strip() for text in texts if text and text.strip()]
    if not documents:
        return []

    vectorizer = TfidfVectorizer(
        max_features=200,
        ngram_range=(1, 2),
        stop_words=SPORTS_STOP_WORDS,
        lowercase=True,
    )
    matrix = vectorizer.fit_transform(documents)
    scores = matrix.mean(axis=0).A1
    features = vectorizer.get_feature_names_out()

    ranked = sorted(zip(features, scores), key=lambda item: item[1], reverse=True)
    return [{"keyword": keyword, "score": round(float(score), 4)} for keyword, score in ranked[:top_n]]
