from __future__ import annotations

import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.demo_llm import generate_mock_answer
from app.ollama_client import OllamaClient, OllamaError
from app.rag.embeddings import EmbeddingError
from app.rag.prompt_builder import build_rag_prompt
from app.rag.retriever import Retriever, build_index, get_index_stats
from app.schemas import (
    ChatMetrics,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ProcessStep,
    RebuildIndexResponse,
    StatsResponse,
)


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=settings.frontend_dir), name="static")


SAMPLE_QUESTIONS = [
    # Section 12 main demo question.
    "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，用来回答 Ara240、LLM Edge Studio 和边缘 AI 部署相关问题。请问这个系统应该采用什么整体架构？知识库怎么构建？用户提问后 RAG 的完整流程是什么？本地部署相比云端调用有什么优势？",
    # Section 12 backup questions.
    "用户提问后，RAG 智能客服系统是如何从知识库中找到资料并生成回答的？",
    "LLM Edge Studio 和普通云端大模型调用有什么区别？它为什么适合边缘端智能应用？",
    "Ara240 DNPU 在边缘 AI 视觉分析任务中主要承担什么作用？",
    "为什么这个项目不直接使用通用大模型回答，而要加入本地知识库和 RAG 检索？",
    # Section 4 API examples.
    "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，应该采用什么整体架构？",
    "用户提问后，RAG 智能客服系统的完整处理流程是什么？",
    "本地大模型部署相比云端大模型调用有什么优势？",
    "LLM Edge Studio 的核心目标是什么？",
    "Ara240 DNPU 在边缘 AI 视觉任务中有什么作用？",
    "为什么智能客服系统需要知识库检索，而不是直接让大模型回答？",
]


def _initial_process() -> list[ProcessStep]:
    names = [
        "接收用户问题",
        "问题向量化",
        "知识库检索",
        "Prompt 构造",
        "本地大模型生成",
        "返回答案与来源",
    ]
    return [ProcessStep(step=index + 1, name=name, status="waiting", detail="等待执行。") for index, name in enumerate(names)]


def _set_step(process: list[ProcessStep], step: int, status: str, detail: str) -> None:
    process[step - 1].status = status
    process[step - 1].detail = detail


def _safe_stats() -> dict:
    try:
        return get_index_stats(settings)
    except Exception:
        return {"document_count": 0, "chunk_count": 0, "categories": [], "vector_store": "unknown"}


def _index_ready() -> bool:
    meta_path = settings.vector_store_dir / "index_meta.json"
    if not meta_path.exists():
        return False
    try:
        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return int(metadata.get("chunk_count", 0) or 0) > 0


@app.get("/")
def index() -> FileResponse:
    return FileResponse(Path(settings.frontend_dir) / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    stats = _safe_stats()
    ollama = OllamaClient(settings).health_check()
    connected = bool(ollama.get("connected"))
    missing_models = []
    if connected and not ollama.get("llm_model_available"):
        missing_models.append(settings.llm_model)
    if connected and not ollama.get("embed_model_available"):
        missing_models.append(settings.embed_model)
    healthy = connected and not missing_models
    status = "ok" if healthy else "degraded"
    if healthy:
        message = None
    elif connected:
        message = f"Ollama is running, but required model is unavailable: {', '.join(missing_models)}."
    else:
        message = "Ollama is not running or model is unavailable."
    return HealthResponse(
        status=status,
        ollama_connected=connected,
        llm_model=settings.llm_model,
        embed_model=settings.embed_model,
        knowledge_base_loaded=stats.get("document_count", 0) > 0,
        document_count=stats.get("document_count", 0),
        chunk_count=stats.get("chunk_count", 0),
        vector_store=stats.get("vector_store", settings.vector_store),
        message=message,
    )


@app.get("/api/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    current = _safe_stats()
    return StatsResponse(
        document_count=current.get("document_count", 0),
        chunk_count=current.get("chunk_count", 0),
        categories=current.get("categories", []),
    )


@app.get("/api/sample-questions")
def sample_questions() -> list[str]:
    return SAMPLE_QUESTIONS


@app.post("/api/rebuild-index", response_model=RebuildIndexResponse)
def rebuild_index() -> RebuildIndexResponse:
    try:
        result = build_index(settings)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"索引重建失败：{exc}") from exc
    return RebuildIndexResponse(
        status="success",
        document_count=result["document_count"],
        chunk_count=result["chunk_count"],
        message="Index rebuilt successfully.",
        vector_store=result.get("vector_store"),
        embedding_provider=result.get("embedding_provider"),
        details=result,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    started = time.time()
    process = _initial_process()
    top_k = request.top_k or settings.top_k
    question = request.question.strip()
    sources = []
    answer = ""

    _set_step(process, 1, "done", "后端成功接收用户输入。")
    try:
        if not _index_ready():
            build_index(settings)

        retriever = Retriever(settings)
        _set_step(process, 2, "running", f"正在使用 {retriever.embedding_provider_name} 将问题转换为向量。")
        try:
            sources = retriever.retrieve(question, top_k=top_k, min_score=settings.min_score)
        except EmbeddingError as exc:
            _set_step(process, 2, "failed", f"问题向量化失败：{exc}")
            _set_step(process, 3, "failed", "无法完成知识库检索。")
            _set_step(process, 4, "waiting", "未构造生成 Prompt。")
            _set_step(process, 5, "waiting", "未调用本地大模型。")
            _set_step(process, 6, "done", "返回模型/embedding 不可用的友好提示。")
            latency_ms = int((time.time() - started) * 1000)
            return ChatResponse(
                answer=(
                    "本地 embedding 模型不可用，无法完成知识库检索。"
                    "请确认 Ollama 已启动并已拉取 nomic-embed-text；"
                    "课堂临时演示可以设置 EMBED_PROVIDER=tfidf 和 MOCK_LLM=true。"
                ),
                sources=[],
                process=process,
                metrics=ChatMetrics(
                    latency_ms=latency_ms,
                    top_k=top_k,
                    retrieved_count=0,
                    model=settings.llm_model if not settings.mock_llm else "MOCK_LLM",
                ),
            )
        _set_step(process, 2, "done", f"使用 {retriever.embedding_provider_name} 将问题转换为向量。")
        _set_step(process, 3, "done", f"从本地知识库中检索 Top-{top_k} 相关片段，命中 {len(sources)} 条。")

        if not sources:
            _set_step(process, 4, "done", "没有足够检索资料，未构造生成 Prompt。")
            _set_step(process, 5, "done", "跳过模型生成，直接返回资料不足提示。")
            answer = "当前知识库中没有找到明确依据，建议补充相关资料后再查询。"
        else:
            messages = build_rag_prompt(question, sources)
            _set_step(process, 4, "done", "将用户问题和检索资料拼接成 RAG Prompt。")
            if settings.mock_llm:
                answer = generate_mock_answer(question, sources)
                _set_step(process, 5, "done", "MOCK_LLM=true，已生成演示回答。")
            else:
                try:
                    answer = OllamaClient(settings).chat(
                        messages,
                        model=settings.llm_model,
                        temperature=settings.temperature,
                    )
                    _set_step(process, 5, "done", f"调用 Ollama 本地模型 {settings.llm_model} 生成回答。")
                except OllamaError as exc:
                    _set_step(process, 5, "failed", f"本地模型调用失败：{exc}")
                    answer = (
                        "已完成知识库检索，但调用本地 Ollama 模型失败。"
                        "请确认 Ollama 已启动，并已拉取所需模型；也可以临时设置 MOCK_LLM=true 演示前端流程。"
                    )
        _set_step(process, 6, "done", "返回客服回答、检索来源和流程信息。")
    except Exception as exc:
        for step in process:
            if step.status == "waiting":
                step.status = "failed"
                step.detail = f"流程中断：{exc}"
                break
        answer = f"系统处理失败：{exc}"

    latency_ms = int((time.time() - started) * 1000)
    return ChatResponse(
        answer=answer,
        sources=sources,
        process=process,
        metrics=ChatMetrics(
            latency_ms=latency_ms,
            top_k=top_k,
            retrieved_count=len(sources),
            model=settings.llm_model if not settings.mock_llm else "MOCK_LLM",
        ),
    )
