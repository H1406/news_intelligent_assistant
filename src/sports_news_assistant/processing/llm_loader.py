from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=2)
def load_text_generator(model_id: str):
    from transformers import pipeline

    return pipeline("text-generation", model=model_id, tokenizer=model_id)
