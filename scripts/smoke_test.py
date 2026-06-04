from __future__ import annotations

import os
import sys
from pathlib import Path


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
    os.environ.setdefault("MOCK_LLM", "true")
    os.environ.setdefault("EMBED_PROVIDER", "tfidf")

    from fastapi.testclient import TestClient

    from app.config import get_settings
    from app.main import app
    from app.rag.chunker import TextChunker
    from app.rag.document_loader import load_documents
    from app.rag.retriever import build_index

    settings = get_settings()
    passed = []
    passed.append(check("import app", lambda: app.title))
    passed.append(check("load knowledge base", lambda: len(load_documents(settings.knowledge_base_dir))))
    passed.append(
        check(
            "chunk knowledge base",
            lambda: len(TextChunker(settings.chunk_size, settings.chunk_overlap).chunk_documents(load_documents(settings.knowledge_base_dir))),
        )
    )
    passed.append(check("build index", lambda: build_index(settings)))

    client = TestClient(app)
    passed.append(check("GET /api/health", lambda: client.get("/api/health").json()))
    passed.append(
        check(
            "POST /api/chat with MOCK_LLM",
            lambda: client.post(
                "/api/chat",
                json={"question": "用户提问后 RAG 的完整流程是什么？", "top_k": 3},
            ).json(),
        )
    )

    return 0 if all(passed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
