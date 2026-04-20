from __future__ import annotations

import re

from sports_news_assistant.processing.llm_loader import load_text_generator


class SportsNewsSummarizer:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def summarize_article(self, text: str, max_sentences: int = 2) -> str:
        if not text.strip():
            return "No content available."

        llm_summary = self._summarize_with_llm(
            prompt=(
                "Summarize this Vietnamese sports news article in English within 2 concise sentences. "
                "Focus on the key event, people or teams involved, and why it matters.\n\n"
                f"Article:\n{text[:2500]}"
            ),
            max_new_tokens=120,
        )
        if self._is_usable_summary(llm_summary, min_alpha_chars=25):
            return llm_summary  # type: ignore[return-value]
        return self._extractive_summary(text, max_sentences=max_sentences)

    def summarize_corpus(self, texts: list[str]) -> str:
        joined = "\n\n".join([text for text in texts if text.strip()][:10])
        if not joined:
            return "No executive summary available."

        llm_summary = self._summarize_with_llm(
            prompt=(
                "You are preparing a weekly executive summary for Vietnamese sports news. "
                "Write one short paragraph in English covering the main themes, standout matches, "
                "transfers, tournaments, or athlete storylines from these articles.\n\n"
                f"Articles:\n{joined[:5000]}"
            ),
            max_new_tokens=180,
        )
        if self._is_usable_summary(llm_summary, min_alpha_chars=40):
            return llm_summary  # type: ignore[return-value]

        return self._extractive_summary(joined, max_sentences=4)

    def _summarize_with_llm(self, prompt: str, max_new_tokens: int) -> str | None:
        try:
            generator = load_text_generator(self.model_id)
        except Exception:
            return None

        result = generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.1,
            return_full_text=False,
        )
        if not result:
            return None
        return str(result[0]["generated_text"]).strip()

    @staticmethod
    def _extractive_summary(text: str, max_sentences: int = 2) -> str:
        sentences = [segment.strip() for segment in text.replace("\n", " ").split(".") if len(segment.strip()) > 30]
        if not sentences:
            fallback = text[:240].strip()
            return fallback or "No summary available."
        summary = ". ".join(sentences[:max_sentences]).strip()
        return (summary + ".") if summary else "No summary available."

    @staticmethod
    def _is_usable_summary(text: str | None, min_alpha_chars: int) -> bool:
        if text is None:
            return False

        summary = text.strip()
        if len(summary) < 30:
            return False
        if re.search(r"(.)\1{10,}", summary):
            return False
        if re.fullmatch(r"[\W_]+", summary):
            return False

        alpha_count = sum(char.isalpha() for char in summary)
        if alpha_count < min_alpha_chars:
            return False

        punctuation_count = sum(char in "!?:;,.-" for char in summary)
        if punctuation_count / max(len(summary), 1) > 0.35:
            return False

        return True
