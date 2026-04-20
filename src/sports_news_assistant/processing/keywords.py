from __future__ import annotations

import html
import re

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
    "có",
    "không",
    "đội",
    "trận",
    "thủ",
    "nam",
    "anh",
    "amp",
    "cầu thủ",
    "bóng đá",
    "thể thao việt nam",
    "việt nam",
    "thể thao",
    "the thao",
    "giải",
    "mùa",
    "ngày",
    "lượt",
    "vòng",
    "hạng",
    "thắng",
    "thua",
    "hòa",
    "đấu",
    "ghi",
    "bàn",
    "huấn luyện viên",
    "hlv",
    "thể thao",
    "the thao",
]

GENERIC_KEYWORDS = {
    "anh",
    "amp",
    "bàn",
    "có",
    "cầu thủ",
    "ghi",
    "giải",
    "hạng",
    "hlv",
    "hòa",
    "huấn luyện viên",
    "không",
    "lượt",
    "man",
    "mùa",
    "nam",
    "ngày",
    "thắng",
    "thua",
    "thủ",
    "trận",
    "vòng",
    "đấu",
    "đội",
}


def extract_keywords(texts: list[str], top_n: int = 10) -> list[dict]:
    documents = [text.strip() for text in texts if text and text.strip()]
    if not documents:
        return []

    vectorizer = TfidfVectorizer(
        max_features=200,
        ngram_range=(1, 2),
        stop_words=SPORTS_STOP_WORDS,
        lowercase=True,
        token_pattern=r"(?u)\b[\w\-]+\b",
    )
    matrix = vectorizer.fit_transform(documents)
    scores = matrix.mean(axis=0).A1
    features = vectorizer.get_feature_names_out()

    ranked = sorted(zip(features, scores), key=lambda item: item[1], reverse=True)
    candidate_pool = max(top_n * 4, 40)
    cleaned = _clean_ranked_keywords(ranked[:candidate_pool])
    refined = _drop_redundant_short_terms(cleaned)
    return [{"keyword": keyword, "score": round(float(score), 4)} for keyword, score in refined[:top_n]]


def _clean_ranked_keywords(ranked: list[tuple[str, float]]) -> list[tuple[str, float]]:
    merged_scores: dict[str, float] = {}

    for raw_keyword, score in ranked:
        keyword = _normalize_keyword(raw_keyword)
        if not _is_meaningful_keyword(keyword):
            continue
        merged_scores[keyword] = max(merged_scores.get(keyword, 0.0), float(score))

    return sorted(merged_scores.items(), key=lambda item: item[1], reverse=True)


def _normalize_keyword(keyword: str) -> str:
    keyword = html.unescape(keyword).lower().strip()
    keyword = re.sub(r"\bamp\b", " ", keyword)
    keyword = re.sub(r"[^\w\s\-]", " ", keyword)
    keyword = re.sub(r"\s+", " ", keyword).strip()
    return keyword


def _is_meaningful_keyword(keyword: str) -> bool:
    if not keyword or len(keyword) < 3:
        return False
    if keyword in SPORTS_STOP_WORDS or keyword in GENERIC_KEYWORDS:
        return False
    if keyword.isdigit():
        return False

    tokens = keyword.split()
    if len(tokens) == 1 and keyword in GENERIC_KEYWORDS:
        return False

    return True


def _drop_redundant_short_terms(ranked: list[tuple[str, float]]) -> list[tuple[str, float]]:
    longer_terms = [keyword for keyword, _ in ranked if len(keyword.split()) > 1]
    refined: list[tuple[str, float]] = []

    for keyword, score in ranked:
        if len(keyword.split()) == 1:
            if any(keyword in long_keyword.split() for long_keyword in longer_terms):
                continue
        refined.append((keyword, score))

    return refined
