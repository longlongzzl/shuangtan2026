from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

import numpy as np

from app.config import Settings, settings
from app.ollama_client import OllamaClient, OllamaError


class EmbeddingError(RuntimeError):
    """Raised when an embedding provider cannot generate vectors."""


class OllamaEmbeddingProvider:
    name = "ollama"

    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.client = OllamaClient(config)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            return self.client.embed(texts, model=self.config.embed_model)
        except OllamaError as exc:
            raise EmbeddingError(str(exc)) from exc

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]

    def get_state(self) -> dict[str, Any]:
        return {}


class TfidfEmbeddingProvider:
    name = "tfidf"

    def __init__(
        self,
        vocabulary: dict[str, int] | None = None,
        idf: list[float] | None = None,
    ) -> None:
        self.vocabulary = vocabulary or {}
        self.idf = np.array(idf or [], dtype=np.float32)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        lowered = text.lower()
        latin_terms = re.findall(r"[a-z0-9][a-z0-9_.:+-]*", lowered)
        cjk_chars = re.findall(r"[\u4e00-\u9fff]", lowered)
        cjk_bigrams = [f"{cjk_chars[index]}{cjk_chars[index + 1]}" for index in range(len(cjk_chars) - 1)]
        return latin_terms + cjk_chars + cjk_bigrams

    def fit(self, texts: list[str]) -> None:
        doc_freq: Counter[str] = Counter()
        for text in texts:
            doc_freq.update(set(self.tokenize(text)))
        self.vocabulary = {term: index for index, term in enumerate(sorted(doc_freq))}
        document_count = max(1, len(texts))
        self.idf = np.zeros(len(self.vocabulary), dtype=np.float32)
        for term, index in self.vocabulary.items():
            self.idf[index] = math.log((1 + document_count) / (1 + doc_freq[term])) + 1

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not self.vocabulary:
            self.fit(texts)
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        if not self.vocabulary:
            raise EmbeddingError("TF-IDF provider has not been fitted.")
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = np.zeros(len(self.vocabulary), dtype=np.float32)
        tokens = self.tokenize(text)
        counts = Counter(token for token in tokens if token in self.vocabulary)
        for token, count in counts.items():
            vector[self.vocabulary[token]] = float(count)
        if len(vector) and len(self.idf) == len(vector):
            vector *= self.idf
        norm = float(np.linalg.norm(vector))
        if norm > 0:
            vector /= norm
        return vector.astype(float).tolist()

    def get_state(self) -> dict[str, Any]:
        return {"vocabulary": self.vocabulary, "idf": self.idf.astype(float).tolist()}

    @classmethod
    def from_state(cls, state: dict[str, Any] | None) -> "TfidfEmbeddingProvider":
        state = state or {}
        return cls(vocabulary=state.get("vocabulary") or {}, idf=state.get("idf") or [])


def create_embedding_provider(
    config: Settings = settings,
    provider_name: str | None = None,
    state: dict[str, Any] | None = None,
):
    provider = (provider_name or config.embed_provider).lower()
    if provider == "tfidf":
        return TfidfEmbeddingProvider.from_state(state)
    if provider == "ollama":
        return OllamaEmbeddingProvider(config)
    raise EmbeddingError(f"Unsupported EMBED_PROVIDER: {provider}")
