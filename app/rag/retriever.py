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
from app.rag.vector_store import VectorResult, create_vector_store, reset_vector_store_files
from app.schemas import SourceItem


_QUERY_STOP_TERMS = {
    "介绍",
    "绍一",
    "一下",
    "用户",
    "提问",
    "问题",
    "当前",
    "多少",
    "几个",
    "几篇",
    "有哪",
    "哪些",
    "是什",
    "什么",
    "怎么",
    "如何",
}


def _term_weight(term: str) -> float:
    if not term:
        return 0.0
    if term.isascii():
        return 1.0
    if len(term) >= 2:
        return 0.65
    return 0.15


def _query_terms(question: str, focused: bool = False) -> set[str]:
    terms = set(TfidfEmbeddingProvider.tokenize(question))
    if not focused:
        return terms
    focused_terms = {
        term
        for term in terms
        if (term.isascii() or len(term) >= 2) and term not in _QUERY_STOP_TERMS
    }
    return focused_terms or terms


def _weighted_overlap_score(query_terms: set[str], text: str) -> float:
    if not query_terms:
        return 0.0
    text_terms = set(TfidfEmbeddingProvider.tokenize(text))
    total = sum(_term_weight(term) for term in query_terms)
    if total <= 0:
        return 0.0
    matched = sum(_term_weight(term) for term in query_terms if term in text_terms)
    return max(0.0, min(1.0, matched / total))


def _best_overlap_score(query_terms: set[str], focused_terms: set[str], text: str) -> float:
    return max(
        _weighted_overlap_score(query_terms, text),
        _weighted_overlap_score(focused_terms, text),
    )


def _query_covers_text_score(question: str, text: str) -> float:
    query_terms = _query_terms(question, focused=True)
    text_terms = _query_terms(text, focused=True)
    if not query_terms or not text_terms:
        return 0.0
    total = sum(_term_weight(term) for term in text_terms)
    if total <= 0:
        return 0.0
    matched = sum(_term_weight(term) for term in text_terms if term in query_terms)
    return max(0.0, min(1.0, matched / total))


def _keyword_score(question: str, chunk: dict[str, Any]) -> float:
    query_terms = _query_terms(question)
    focused_terms = _query_terms(question, focused=True)
    metadata = chunk.get("metadata", {})
    title = str(metadata.get("title") or "")
    category = str(metadata.get("category") or "")
    source = str(metadata.get("source") or "")
    body = str(chunk.get("text") or "")

    title_score = _best_overlap_score(query_terms, focused_terms, title)
    title_coverage_score = _query_covers_text_score(question, title)
    category_score = _best_overlap_score(query_terms, focused_terms, category)
    source_score = _best_overlap_score(query_terms, focused_terms, source)
    body_score = _best_overlap_score(query_terms, focused_terms, body)
    return max(
        min(1.0, body_score * 0.95),
        min(1.0, title_score * 1.45),
        min(1.0, title_coverage_score * 1.3),
        min(1.0, category_score * 0.8),
        min(1.0, source_score * 0.45),
    )


def _result_key(text: str, metadata: dict[str, Any]) -> str:
    chunk_id = metadata.get("chunk_id")
    if chunk_id:
        return str(chunk_id)
    return f"{metadata.get('doc_id', '')}:{metadata.get('title', '')}:{text[:120]}"


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

    if force_simple_store or config.vector_store == "chroma":
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
        self.keyword_chunks = TextChunker(config.chunk_size, config.chunk_overlap).chunk_documents(
            load_documents(config.knowledge_base_dir)
        )

    def retrieve(
        self,
        question: str,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> list[SourceItem]:
        top_k = top_k or self.config.top_k
        min_score = self.config.min_score if min_score is None else min_score
        query_embedding = self.embedding_provider.embed_query(question)
        candidate_k = max(top_k * 4, 12)
        vector_results = self.store.query(query_embedding, top_k=candidate_k)
        keyword_results = self._keyword_results(question, limit=candidate_k)

        ranked_results = self._merge_results(vector_results, keyword_results)

        source_groups: dict[str, dict[str, Any]] = {}
        ordered_doc_keys: list[str] = []
        for result in ranked_results:
            if result.score < min_score:
                continue
            metadata = result.metadata
            doc_key = str(metadata.get("doc_id") or metadata.get("title") or _result_key(result.text, metadata))
            if doc_key not in source_groups:
                if len(ordered_doc_keys) >= top_k:
                    continue
                source_groups[doc_key] = {
                    "metadata": metadata,
                    "score": float(result.score),
                    "contents": [],
                }
                ordered_doc_keys.append(doc_key)
            group = source_groups[doc_key]
            contents = group["contents"]
            if not isinstance(contents, list) or len(contents) >= 2:
                continue
            contents.append(result.text)
            group["score"] = max(float(group["score"]), float(result.score))

        sources: list[SourceItem] = []
        for doc_key in ordered_doc_keys:
            group = source_groups[doc_key]
            metadata = dict(group["metadata"])
            contents = group["contents"] if isinstance(group["contents"], list) else []
            sources.append(
                SourceItem(
                    rank=len(sources) + 1,
                    title=str(metadata.get("title") or "未命名资料"),
                    source=str(metadata.get("source") or "local_knowledge_base"),
                    category=str(metadata.get("category") or "未分类"),
                    score=round(float(group["score"]), 4),
                    content="\n".join(str(content) for content in contents),
                )
            )
        return sources

    def _keyword_results(self, question: str, limit: int) -> list[VectorResult]:
        results: list[VectorResult] = []
        for chunk in self.keyword_chunks:
            score = _keyword_score(question, chunk)
            if score <= 0:
                continue
            results.append(
                VectorResult(
                    text=str(chunk.get("text") or ""),
                    metadata=dict(chunk.get("metadata") or {}),
                    score=score,
                )
            )
        return sorted(results, key=lambda result: result.score, reverse=True)[:limit]

    @staticmethod
    def _merge_results(
        vector_results: list[VectorResult],
        keyword_results: list[VectorResult],
    ) -> list[VectorResult]:
        merged: dict[str, dict[str, Any]] = {}

        for result in vector_results:
            key = _result_key(result.text, result.metadata)
            merged[key] = {
                "text": result.text,
                "metadata": dict(result.metadata),
                "vector_score": max(0.0, min(1.0, float(result.score))),
                "keyword_score": 0.0,
            }

        for result in keyword_results:
            key = _result_key(result.text, result.metadata)
            item = merged.setdefault(
                key,
                {
                    "text": result.text,
                    "metadata": dict(result.metadata),
                    "vector_score": 0.0,
                    "keyword_score": 0.0,
                },
            )
            item["keyword_score"] = max(float(item["keyword_score"]), max(0.0, min(1.0, float(result.score))))

        reranked: list[VectorResult] = []
        for item in merged.values():
            vector_score = float(item["vector_score"])
            keyword_score = float(item["keyword_score"])
            combined_score = max(vector_score * 0.85, keyword_score)
            if keyword_score >= 0.35:
                combined_score = max(combined_score, 0.75 + keyword_score * 0.25)
            elif keyword_score >= 0.2:
                combined_score = max(combined_score, 0.55 + keyword_score * 0.25)
            reranked.append(
                VectorResult(
                    text=str(item["text"]),
                    metadata=dict(item["metadata"]),
                    score=max(0.0, min(1.0, combined_score)),
                )
            )

        return sorted(reranked, key=lambda result: result.score, reverse=True)


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
