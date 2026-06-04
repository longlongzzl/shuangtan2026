from __future__ import annotations

import logging
from typing import Any

import requests

from app.config import Settings, settings


logger = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    """Readable wrapper for Ollama connection and response errors."""


class OllamaClient:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.base_url = config.ollama_base_url.rstrip("/")
        self.timeout = config.request_timeout

    def health_check(self) -> dict[str, Any]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = {item.get("name") for item in models if isinstance(item, dict)}
            return {
                "connected": True,
                "models": sorted(name for name in model_names if name),
                "llm_model_available": self.config.llm_model in model_names,
                "embed_model_available": self.config.embed_model in model_names,
            }
        except requests.RequestException as exc:
            logger.info("Ollama health check failed: %s", exc)
            return {
                "connected": False,
                "models": [],
                "llm_model_available": False,
                "embed_model_available": False,
                "error": str(exc),
            }

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        payload = {
            "model": model or self.config.llm_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            logger.info("Ollama chat request failed: %s", exc)
            raise OllamaError(f"Ollama chat request failed: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama chat returned invalid JSON.") from exc

        message = data.get("message") if isinstance(data, dict) else None
        if isinstance(message, dict) and message.get("content"):
            return str(message["content"]).strip()
        if isinstance(data, dict) and data.get("response"):
            return str(data["response"]).strip()
        raise OllamaError("Ollama chat response did not include answer content.")

    def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        if not texts:
            return []
        embed_model = model or self.config.embed_model
        try:
            return self._embed_batch(texts, embed_model)
        except OllamaError as batch_error:
            logger.info("Ollama /api/embed failed, trying /api/embeddings: %s", batch_error)
            vectors = [self._embed_single(text, embed_model) for text in texts]
            return vectors

    def _embed_batch(self, texts: list[str], model: str) -> list[list[float]]:
        payload = {"model": model, "input": texts}
        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise OllamaError(f"Ollama embed request failed: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama embed returned invalid JSON.") from exc

        embeddings = data.get("embeddings") if isinstance(data, dict) else None
        if isinstance(embeddings, list) and len(embeddings) == len(texts):
            return [[float(value) for value in vector] for vector in embeddings]

        embedding = data.get("embedding") if isinstance(data, dict) else None
        if len(texts) == 1 and isinstance(embedding, list):
            return [[float(value) for value in embedding]]

        raise OllamaError("Ollama /api/embed response did not include embeddings.")

    def _embed_single(self, text: str, model: str) -> list[float]:
        payload = {"model": model, "prompt": text}
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise OllamaError(f"Ollama embeddings request failed: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama embeddings returned invalid JSON.") from exc

        embedding = data.get("embedding") if isinstance(data, dict) else None
        if isinstance(embedding, list):
            return [float(value) for value in embedding]
        embeddings = data.get("embeddings") if isinstance(data, dict) else None
        if isinstance(embeddings, list) and embeddings:
            return [float(value) for value in embeddings[0]]
        raise OllamaError("Ollama /api/embeddings response did not include an embedding.")
