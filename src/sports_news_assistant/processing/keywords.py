from __future__ import annotations

import html
import json
import re

from sklearn.feature_extraction.text import TfidfVectorizer

from sports_news_assistant.processing.llm_loader import load_text_generator

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
    "sân",
    "bóng",
    "điểm",
    "vào",
]
SPORTS_STOP_WORDS_SET = set(SPORTS_STOP_WORDS)

GENERIC_KEYWORDS = {
    "anh",
    "tôi",
    "ông",
    "phút",
    "này",
    "ngày"
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


def extract_keywords(
    texts: list[str],
    top_n: int = 10,
    llm_filter_model_id: str | None = None,
    llm_filter_max_candidates: int = 30,
) -> list[dict]:
    documents = [_normalize_document(text) for text in texts if text and text.strip()]
    if not documents:
        return []

    min_df = 2 if len(documents) >= 12 else 1
    max_df = 0.85 if len(documents) >= 10 else 1.0
    vectorizer = TfidfVectorizer(
        max_features=200,
        ngram_range=(1, 2),
        stop_words=SPORTS_STOP_WORDS,
        lowercase=True,
        token_pattern=r"(?u)\b[\w\-]+\b",
        min_df=min_df,
        max_df=max_df,
    )

    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return []

    if matrix.shape[1] == 0:
        return []

    scores = matrix.mean(axis=0).A1
    features = vectorizer.get_feature_names_out()

    ranked = sorted(zip(features, scores), key=lambda item: item[1], reverse=True)
    candidate_pool = max(top_n * 5, 50)
    cleaned = _clean_ranked_keywords(ranked[:candidate_pool])
    refined = _drop_redundant_short_terms(cleaned)
    if llm_filter_model_id and refined:
        refined = _apply_llm_keyword_filter(
            refined,
            model_id=llm_filter_model_id,
            max_candidates=llm_filter_max_candidates,
        )
    return [{"keyword": keyword, "score": round(float(score), 4)} for keyword, score in refined[:top_n]]


def _normalize_document(text: str) -> str:
    normalized = html.unescape(text)
    return re.sub(r"\s+", " ", normalized).strip()


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
    if keyword in SPORTS_STOP_WORDS_SET or keyword in GENERIC_KEYWORDS:
        return False
    if keyword.isdigit():
        return False
    if "http" in keyword or "www" in keyword:
        return False

    tokens = keyword.split()
    if len(tokens) > 4:
        return False
    if all(len(token) <= 2 for token in tokens):
        return False
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


def _apply_llm_keyword_filter(
    ranked: list[tuple[str, float]],
    model_id: str,
    max_candidates: int,
) -> list[tuple[str, float]]:
    candidate_limit = max(5, max_candidates)
    candidates = ranked[:candidate_limit]
    keep_keywords = _select_keywords_with_llm(
        candidates=[keyword for keyword, _ in candidates],
        model_id=model_id,
    )
    if not keep_keywords:
        return ranked

    promoted = [item for item in ranked if item[0] in keep_keywords]
    if len(promoted) < min(3, len(candidates)):
        return ranked

    demoted = [item for item in ranked if item[0] not in keep_keywords]
    return promoted + demoted


def _select_keywords_with_llm(candidates: list[str], model_id: str) -> set[str]:
    if not candidates:
        return set()

    prompt = (
        "You are filtering keyword candidates for Vietnamese sports-news trend analytics.\n"
        "Keep only specific and informative keywords such as teams, players, coaches, tournaments, "
        "transfers, incidents, or venues.\n"
        "Drop generic language, filler words, and broad sports terms.\n"
        "Return strict JSON only with this schema: {\"keep\": [\"keyword1\", \"keyword2\"]}.\n"
        f"Candidates: {json.dumps(candidates, ensure_ascii=False)}"
    )

    try:
        generator = load_text_generator(model_id)
        result = generator(
            prompt,
            max_new_tokens=200,
            do_sample=False,
            temperature=0.0,
            return_full_text=False,
        )
    except Exception:
        return set()

    if not result:
        return set()

    generated_text = str(result[0].get("generated_text", "")).strip()
    return _extract_keep_keywords_from_response(generated_text, candidates)


def _extract_keep_keywords_from_response(response_text: str, candidates: list[str]) -> set[str]:
    if not response_text:
        return set()

    candidate_lookup = {keyword.lower() for keyword in candidates}
    match = re.search(r"\{.*\}", response_text, flags=re.DOTALL)
    if not match:
        return set()

    payload_text = match.group(0)
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return set()

    keep_values = payload.get("keep")
    if not isinstance(keep_values, list):
        return set()

    selected: set[str] = set()
    for value in keep_values:
        normalized = _normalize_keyword(str(value))
        if normalized in candidate_lookup:
            selected.add(normalized)
    return selected
