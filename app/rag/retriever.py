from __future__ import annotations

import time
from typing import Any

from app.config import Settings, settings
from app.rag.chunker import TextChunker
from app.rag.document_loader import load_documents
from app.rag.embeddings import (
    EmbeddingError,
    TfidfEmbeddingProvider,
    create_embedding_provider,
)
from app.rag.vector_store import create_vector_store, reset_vector_store_files
from app.schemas import SourceItem


def build_index(config: Settings = settings) -> dict[str, Any]:
    started = time.time()
    documents = load_documents(config.knowledge_base_dir)
    chunker = TextChunker(config.chunk_size, config.chunk_overlap)
    chunks = chunker.chunk_documents(documents)
    texts = [chunk["text"] for chunk in chunks]

    if not chunks:
        reset_vector_store_files(config)
        store = create_vector_store(config, force_simple=True)
        store.add_chunks([], [], {"embedding_provider": "none", "embedding_model": ""})
        return {
            "document_count": 0,
            "chunk_count": 0,
            "vector_store": store.name,
            "embedding_provider": "none",
            "elapsed_ms": int((time.time() - started) * 1000),
        }

    embedding_provider_name = config.embed_provider
    provider_state: dict[str, Any] = {}
    force_simple_store = embedding_provider_name == "tfidf"

    try:
        provider = create_embedding_provider(config, embedding_provider_name)
        embeddings = provider.embed_documents(texts)
        provider_state = provider.get_state()
    except EmbeddingError:
        # TF-IDF keeps the classroom demo searchable when Ollama embeddings are unavailable.
        embedding_provider_name = "tfidf"
        provider = TfidfEmbeddingProvider()
        embeddings = provider.embed_documents(texts)
        provider_state = provider.get_state()
        force_simple_store = True

    if force_simple_store:
        reset_vector_store_files(config)
    store = create_vector_store(config, force_simple=force_simple_store, prefer_config=True)
    metadata = {
        "embedding_provider": embedding_provider_name,
        "embedding_model": config.embed_model if embedding_provider_name == "ollama" else "local-tfidf",
        "embedding_state": provider_state,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "categories": sorted({document.category for document in documents}),
    }
    store.add_chunks(chunks, embeddings, metadata)
    return {
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "vector_store": store.name,
        "embedding_provider": embedding_provider_name,
        "elapsed_ms": int((time.time() - started) * 1000),
    }


class Retriever:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.store = create_vector_store(config)
        metadata = self.store.read_metadata() if hasattr(self.store, "read_metadata") else {}
        provider_name = metadata.get("embedding_provider") or config.embed_provider
        provider_state = metadata.get("embedding_state") or {}
        self.embedding_provider_name = provider_name
        self.embedding_provider = create_embedding_provider(config, provider_name, provider_state)

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> list[SourceItem]:
        top_k = top_k or self.config.top_k
        min_score = self.config.min_score if min_score is None else min_score
        query_embedding = self.embedding_provider.embed_query(question)
        vector_results = self.store.query(query_embedding, top_k=top_k)

        sources: list[SourceItem] = []
        for rank, result in enumerate(vector_results, start=1):
            if result.score < min_score:
                continue
            metadata = result.metadata
            sources.append(
                SourceItem(
                    rank=rank,
                    title=str(metadata.get("title") or "未命名资料"),
                    source=str(metadata.get("source") or "local_knowledge_base"),
                    category=str(metadata.get("category") or "未分类"),
                    score=round(float(result.score), 4),
                    content=result.text,
                )
            )
        return sources


def get_index_stats(config: Settings = settings) -> dict[str, Any]:
    store = create_vector_store(config)
    stats = store.stats()
    if stats.get("document_count"):
        return stats

    documents = load_documents(config.knowledge_base_dir)
    chunks = TextChunker(config.chunk_size, config.chunk_overlap).chunk_documents(documents)
    return {
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "categories": sorted({document.category for document in documents}),
        "vector_store": stats.get("vector_store", "simple"),
        "embedding_provider": stats.get("embedding_provider"),
    }
