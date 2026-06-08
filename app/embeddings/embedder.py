from __future__ import annotations

import os

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, model_name: str | None = None):
        self._model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self._model = SentenceTransformer(self._model_name)

    def encode(self, text: str) -> list[float]:
        return self._model.encode(text).tolist()

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()

    @property
    def dimension(self) -> int:
        return self._model.get_sentence_embedding_dimension()
