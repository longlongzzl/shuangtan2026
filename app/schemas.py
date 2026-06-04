from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    rank: int
    title: str
    source: str
    category: str
    score: float = Field(ge=0.0, le=1.0)
    content: str


class ProcessStep(BaseModel):
    step: int
    name: str
    status: str
    detail: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class ChatMetrics(BaseModel):
    latency_ms: int
    top_k: int
    retrieved_count: int
    model: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    process: list[ProcessStep]
    metrics: ChatMetrics


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    llm_model: str
    embed_model: str
    knowledge_base_loaded: bool
    document_count: int
    chunk_count: int
    vector_store: str
    message: str | None = None


class StatsResponse(BaseModel):
    document_count: int
    chunk_count: int
    categories: list[str]


class RebuildIndexResponse(BaseModel):
    status: str
    document_count: int
    chunk_count: int
    message: str
    vector_store: str | None = None
    embedding_provider: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
