from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


def check(name: str, func) -> bool:
    try:
        result = func()
        print(f"[PASS] {name}: {result}")
        return True
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        return False


def main() -> int:
    # Smoke tests must be runnable on a classroom machine before Ollama is ready.
    os.environ["MOCK_LLM"] = "true"
    os.environ["EMBED_PROVIDER"] = "tfidf"

    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import app
    from app.rag.chunker import TextChunker
    from app.rag.document_loader import load_documents
    from app.rag.retriever import build_index

    settings = get_settings()

    def assert_response(response, expected_status: int = 200) -> Any:
        assert response.status_code == expected_status, response.text
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def assert_homepage() -> str:
        text = assert_response(client.get("/"))
        assert "NXP AIoT Cloud 智能客服系统" in text
        return "homepage html ok"

    def assert_health() -> dict[str, Any]:
        data = assert_response(client.get("/api/health"))
        assert data["knowledge_base_loaded"] is True
        assert data["document_count"] >= 7
        assert data["chunk_count"] >= 30
        return {
            "status": data["status"],
            "documents": data["document_count"],
            "chunks": data["chunk_count"],
            "vector_store": data["vector_store"],
        }

    def assert_stats() -> dict[str, Any]:
        data = assert_response(client.get("/api/stats"))
        assert data["document_count"] >= 7
        assert data["chunk_count"] >= 30
        assert "RAG" in data["categories"]
        return data

    def assert_sample_questions() -> str:
        data = assert_response(client.get("/api/sample-questions"))
        assert len(data) >= 6
        assert "RAG" in " ".join(data)
        return f"{len(data)} questions"

    def assert_rebuild_index() -> dict[str, Any]:
        data = assert_response(client.post("/api/rebuild-index"))
        assert data["status"] == "success"
        assert data["document_count"] >= 7
        assert data["chunk_count"] >= 30
        return {
            "documents": data["document_count"],
            "chunks": data["chunk_count"],
            "embedding_provider": data["embedding_provider"],
        }

    def assert_chat() -> dict[str, Any]:
        data = assert_response(
            client.post(
                "/api/chat",
                json={"question": "用户提问后 RAG 的完整流程是什么？", "top_k": 3},
            )
        )
        assert data["answer"]
        assert data["metrics"]["model"] == "MOCK_LLM"
        assert data["metrics"]["retrieved_count"] > 0
        assert len(data["sources"]) > 0
        assert len(data["process"]) == 6
        assert all(step["status"] in {"done", "failed", "waiting", "running"} for step in data["process"])
        return {
            "retrieved_count": data["metrics"]["retrieved_count"],
            "latency_ms": data["metrics"]["latency_ms"],
            "first_source": data["sources"][0]["title"],
        }

    passed = []
    passed.append(check("import app", lambda: app.title))
    passed.append(check("load knowledge base", lambda: len(load_documents(settings.knowledge_base_dir))))
    passed.append(
        check(
            "chunk knowledge base",
            lambda: _assert_min_chunks(
                len(TextChunker(settings.chunk_size, settings.chunk_overlap).chunk_documents(load_documents(settings.knowledge_base_dir))),
            ),
        )
    )
    passed.append(check("build index", lambda: build_index(settings)))

    client = TestClient(app)
    passed.append(check("GET /", assert_homepage))
    passed.append(check("GET /api/health", assert_health))
    passed.append(check("GET /api/stats", assert_stats))
    passed.append(check("GET /api/sample-questions", assert_sample_questions))
    passed.append(check("POST /api/rebuild-index", assert_rebuild_index))
    passed.append(check("POST /api/chat with MOCK_LLM", assert_chat))

    return 0 if all(passed) else 1


def _assert_min_chunks(chunk_count: int) -> int:
    assert chunk_count >= 30
    return chunk_count


if __name__ == "__main__":
    raise SystemExit(main())
