from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from app.config import Settings, settings


@dataclass
class VectorResult:
    text: str
    metadata: dict[str, Any]
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    a = np.array(left, dtype=np.float32)
    b = np.array(right, dtype=np.float32)
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def normalized_score(value: float) -> float:
    if math.isnan(value):
        return 0.0
    if value < 0:
        return max(0.0, min(1.0, (value + 1.0) / 2.0))
    return max(0.0, min(1.0, value))


class MetadataMixin:
    def __init__(self, persist_dir: Path) -> None:
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.meta_path = self.persist_dir / "index_meta.json"

    def read_metadata(self) -> dict[str, Any]:
        if not self.meta_path.exists():
            return {}
        try:
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def write_metadata(self, metadata: dict[str, Any]) -> None:
        self.meta_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class SimpleVectorStore(MetadataMixin):
    def __init__(self, persist_dir: Path) -> None:
        super().__init__(persist_dir)
        self.store_path = persist_dir / "simple_store.json"
        self._items: list[dict[str, Any]] = []
        self._load()

    @property
    def name(self) -> str:
        return "simple"

    def _load(self) -> None:
        if not self.store_path.exists():
            self._items = []
            return
        try:
            payload = json.loads(self.store_path.read_text(encoding="utf-8"))
            self._items = payload.get("items", [])
        except (OSError, json.JSONDecodeError):
            self._items = []

    def reset(self) -> None:
        self._items = []
        if self.store_path.exists():
            self.store_path.unlink()

    def add_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
        metadata: dict[str, Any],
    ) -> None:
        self._items = [
            {
                "id": chunk["id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "embedding": embeddings[index],
            }
            for index, chunk in enumerate(chunks)
        ]
        self.store_path.write_text(
            json.dumps({"items": self._items}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.write_metadata({**metadata, "vector_store": self.name})

    def query(self, query_embedding: list[float], top_k: int) -> list[VectorResult]:
        results: list[VectorResult] = []
        for item in self._items:
            score = normalized_score(cosine_similarity(query_embedding, item.get("embedding", [])))
            results.append(VectorResult(text=item["text"], metadata=item["metadata"], score=score))
        return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]

    def stats(self) -> dict[str, Any]:
        documents = {item["metadata"].get("doc_id") for item in self._items}
        categories = sorted({item["metadata"].get("category", "未分类") for item in self._items})
        metadata = self.read_metadata()
        return {
            "document_count": len(documents),
            "chunk_count": len(self._items),
            "categories": categories,
            "vector_store": self.name,
            "embedding_provider": metadata.get("embedding_provider"),
        }


class ChromaVectorStore(MetadataMixin):
    def __init__(self, persist_dir: Path) -> None:
        super().__init__(persist_dir)
        try:
            import chromadb
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("ChromaDB is not installed.") from exc

        self._client = chromadb.PersistentClient(path=str(persist_dir / "chroma"))
        self._collection_name = "knowledge_chunks"
        self._collection = self._client.get_or_create_collection(self._collection_name)

    @property
    def name(self) -> str:
        return "chroma"

    def reset(self) -> None:
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(self._collection_name)

    def add_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
        metadata: dict[str, Any],
    ) -> None:
        self.reset()
        if not chunks:
            self.write_metadata({**metadata, "vector_store": self.name})
            return
        self._collection.add(
            ids=[chunk["id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks],
        )
        self.write_metadata({**metadata, "vector_store": self.name})

    def query(self, query_embedding: list[float], top_k: int) -> list[VectorResult]:
        if self._collection.count() == 0:
            return []
        payload = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        documents = payload.get("documents", [[]])[0]
        metadatas = payload.get("metadatas", [[]])[0]
        distances = payload.get("distances", [[]])[0]
        results: list[VectorResult] = []
        for index, document in enumerate(documents):
            distance = float(distances[index]) if index < len(distances) else 1.0
            score = max(0.0, min(1.0, 1.0 - distance))
            results.append(
                VectorResult(
                    text=document,
                    metadata=dict(metadatas[index] or {}),
                    score=score,
                )
            )
        return sorted(results, key=lambda result: result.score, reverse=True)

    def stats(self) -> dict[str, Any]:
        count = self._collection.count()
        categories: set[str] = set()
        doc_ids: set[str] = set()
        if count:
            payload = self._collection.get(include=["metadatas"])
            for metadata in payload.get("metadatas", []):
                if not metadata:
                    continue
                categories.add(str(metadata.get("category", "未分类")))
                doc_ids.add(str(metadata.get("doc_id", "")))
        metadata = self.read_metadata()
        return {
            "document_count": len(doc_ids),
            "chunk_count": count,
            "categories": sorted(categories),
            "vector_store": self.name,
            "embedding_provider": metadata.get("embedding_provider"),
        }


def _metadata_for_dir(persist_dir: Path) -> dict[str, Any]:
    path = persist_dir / "index_meta.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def create_vector_store(config: Settings = settings, force_simple: bool = False, prefer_config: bool = False):
    config.vector_store_dir.mkdir(parents=True, exist_ok=True)
    metadata = _metadata_for_dir(config.vector_store_dir)
    if force_simple or (metadata.get("vector_store") == "simple" and not prefer_config):
        return SimpleVectorStore(config.vector_store_dir)
    if config.vector_store == "chroma":
        try:
            return ChromaVectorStore(config.vector_store_dir)
        except RuntimeError:
            return SimpleVectorStore(config.vector_store_dir)
    return SimpleVectorStore(config.vector_store_dir)


def reset_vector_store_files(config: Settings = settings) -> None:
    if config.vector_store_dir.exists():
        for child in config.vector_store_dir.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
