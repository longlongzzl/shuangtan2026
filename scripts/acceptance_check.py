from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))


SECTION_4_QUESTIONS = [
    "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，应该采用什么整体架构？",
    "用户提问后，RAG 智能客服系统的完整处理流程是什么？",
    "本地大模型部署相比云端大模型调用有什么优势？",
    "LLM Edge Studio 的核心目标是什么？",
    "Ara240 DNPU 在边缘 AI 视觉任务中有什么作用？",
    "为什么智能客服系统需要知识库检索，而不是直接让大模型回答？",
]

SECTION_12_QUESTIONS = [
    "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，用来回答 Ara240、LLM Edge Studio 和边缘 AI 部署相关问题。请问这个系统应该采用什么整体架构？知识库怎么构建？用户提问后 RAG 的完整流程是什么？本地部署相比云端调用有什么优势？",
    "用户提问后，RAG 智能客服系统是如何从知识库中找到资料并生成回答的？",
    "LLM Edge Studio 和普通云端大模型调用有什么区别？它为什么适合边缘端智能应用？",
    "Ara240 DNPU 在边缘 AI 视觉分析任务中主要承担什么作用？",
    "为什么这个项目不直接使用通用大模型回答，而要加入本地知识库和 RAG 检索？",
]

PROCESS_NAMES = [
    "接收用户问题",
    "问题向量化",
    "知识库检索",
    "Prompt 构造",
    "本地大模型生成",
    "返回答案与来源",
]

FRONTEND_PROCESS_LABELS = [
    "接收用户问题",
    "问题向量化",
    "知识库检索",
    "Prompt 构造",
    "本地模型生成",
    "返回答案与来源",
]

REQUIRED_ENV = {
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "LLM_MODEL": "qwen2.5:7b",
    "EMBED_MODEL": "nomic-embed-text",
    "EMBED_PROVIDER": "ollama",
    "VECTOR_STORE": "chroma",
    "TOP_K": "3",
    "MIN_SCORE": "0.1",
    "CHUNK_SIZE": "500",
    "CHUNK_OVERLAP": "80",
    "MOCK_LLM": "false",
    "TEMPERATURE": "0.2",
    "REQUEST_TIMEOUT": "120",
}

REQUIRED_FILES = [
    "app/__init__.py",
    "app/main.py",
    "app/config.py",
    "app/schemas.py",
    "app/ollama_client.py",
    "app/demo_llm.py",
    "app/rag/__init__.py",
    "app/rag/document_loader.py",
    "app/rag/chunker.py",
    "app/rag/embeddings.py",
    "app/rag/vector_store.py",
    "app/rag/retriever.py",
    "app/rag/prompt_builder.py",
    "frontend/index.html",
    "frontend/style.css",
    "frontend/app.js",
    "data/knowledge_base/01_project_goal.md",
    "data/knowledge_base/02_system_architecture.md",
    "data/knowledge_base/03_nxp_aiot_cloud.md",
    "data/knowledge_base/04_ara240_edge_ai.md",
    "data/knowledge_base/05_llm_edge_studio.md",
    "data/knowledge_base/06_vlm_edge_studio.md",
    "data/knowledge_base/07_rag_customer_service.md",
    "data/vector_store/.gitkeep",
    "scripts/seed_demo_data.py",
    "scripts/build_index.py",
    "scripts/smoke_test.py",
    "scripts/acceptance_check.py",
    "docs/project_design.md",
    "docs/demo_script.md",
    "docs/api_reference.md",
    ".env.example",
    ".gitignore",
    "requirements.txt",
    "README.md",
    "tests/test_basic.py",
]


def pass_line(name: str, detail: Any = "ok") -> None:
    print(f"[PASS] {name}: {detail}")


def fail(name: str, detail: Any) -> None:
    raise AssertionError(f"{name}: {detail}")


def read(path: str) -> str:
    return (ROOT_DIR / path).read_text(encoding="utf-8")


def assert_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT_DIR / path).is_file()]
    if missing:
        fail("required file structure", missing)
    pass_line("required file structure", f"{len(REQUIRED_FILES)} files")


def assert_env_example() -> None:
    values: dict[str, str] = {}
    for line in read(".env.example").splitlines():
        if not line.strip() or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    missing_or_wrong = {key: expected for key, expected in REQUIRED_ENV.items() if values.get(key) != expected}
    if missing_or_wrong:
        fail(".env.example defaults", missing_or_wrong)
    pass_line(".env.example defaults", values)


def assert_no_cloud_api_dependency() -> None:
    banned_terms = ["api.openai", "openai.ChatCompletion", "anthropic", "dashscope", "zhipu", "moonshot"]
    checked_files = [
        *ROOT_DIR.glob("app/**/*.py"),
        *ROOT_DIR.glob("frontend/*"),
        *ROOT_DIR.glob("scripts/*.py"),
        *ROOT_DIR.glob("tests/*.py"),
        ROOT_DIR / "requirements.txt",
    ]
    hits: list[str] = []
    for path in checked_files:
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for term in banned_terms:
            if term.lower() in text:
                hits.append(f"{path.relative_to(ROOT_DIR)}:{term}")
    if hits:
        fail("no cloud model API dependency", hits)
    pass_line("no cloud model API dependency")


def assert_frontend_static_requirements() -> None:
    html = read("frontend/index.html")
    css = read("frontend/style.css")
    js = read("frontend/app.js")
    required_html = [
        "NXP AIoT Cloud 智能客服系统",
        "本地模型连接",
        "LLM 模型",
        "Embedding 模型",
        "知识库文档数",
        "知识库 Chunk 数",
        "向量库类型",
        "RAG 模式",
        "重建知识库索引",
        "清空聊天",
        "检索来源",
    ]
    missing_html = [item for item in required_html if item not in html]
    missing_steps = [item for item in FRONTEND_PROCESS_LABELS if item not in js]
    required_fetches = ["/api/health", "/api/sample-questions", "/api/rebuild-index", "/api/chat"]
    missing_fetches = [item for item in required_fetches if item not in js]
    frontend_text = f"{html}\n{css}\n{js}".lower()
    forbidden_frontend = [term for term in ["react", "vue", "cdn.jsdelivr", "unpkg.com", "http://", "https://"] if term in frontend_text]
    if missing_html or missing_steps or missing_fetches or forbidden_frontend:
        fail(
            "frontend static requirements",
            {
                "missing_html": missing_html,
                "missing_steps": missing_steps,
                "missing_fetches": missing_fetches,
                "forbidden_frontend": forbidden_frontend,
            },
        )
    if "questionInput.value = questions[index]" not in js:
        fail("sample question click fills input", "frontend/app.js does not set questionInput.value")
    if "chatForm.requestSubmit()" not in js:
        fail("enter key send", "frontend/app.js does not submit form on Enter")
    pass_line("frontend static requirements")


def assert_readme_and_docs() -> None:
    readme = read("README.md")
    required_readme_terms = [
        "项目简介",
        "mermaid",
        "技术栈",
        "目录结构",
        "环境准备",
        "Ollama 安装和模型准备",
        "安装依赖",
        "初始化知识库",
        "构建索引",
        "启动后端",
        "http://localhost:8000",
        "演示问题",
        "常见问题排查",
        "项目分工建议",
        "后续扩展方向",
        "python -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "ollama pull qwen2.5:7b",
        "ollama pull nomic-embed-text",
        "cp .env.example .env",
        "python scripts/seed_demo_data.py",
        "python scripts/build_index.py",
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        ".venv\\Scripts\\activate",
    ]
    missing_readme = [term for term in required_readme_terms if term not in readme]
    missing_questions = [question for question in SECTION_4_QUESTIONS + SECTION_12_QUESTIONS if question not in readme]
    project_design = read("docs/project_design.md")
    demo_script = read("docs/demo_script.md")
    api_reference = read("docs/api_reference.md")
    design_terms = ["项目背景", "项目目标", "系统架构", "RAG 流程", "技术选型", "前端展示设计", "测评指标", "风险与解决方案"]
    demo_terms = ["开场介绍", "系统架构讲解", "主演示问题", "演示步骤", "重点说明", "备用问题", "现场翻车时的备用讲法"]
    api_terms = ["/api/health", "/api/stats", "/api/sample-questions", "/api/rebuild-index", "/api/chat"]
    missing_docs = {
        "project_design": [term for term in design_terms if term not in project_design],
        "demo_script": [term for term in demo_terms if term not in demo_script],
        "api_reference": [term for term in api_terms if term not in api_reference],
        "demo_questions": [question for question in SECTION_12_QUESTIONS if question not in demo_script],
    }
    missing_docs = {key: value for key, value in missing_docs.items() if value}
    if missing_readme or missing_questions or missing_docs:
        fail(
            "README and docs",
            {
                "missing_readme": missing_readme,
                "missing_questions": missing_questions,
                "missing_docs": missing_docs,
            },
        )
    pass_line("README and docs")


def assert_seed_loader_chunker() -> tuple[Any, Any, list[dict[str, Any]]]:
    subprocess.run([sys.executable, "scripts/seed_demo_data.py"], cwd=ROOT_DIR, check=True, capture_output=True, text=True)

    from app.config import get_settings
    from app.rag.chunker import TextChunker
    from app.rag.document_loader import load_documents

    settings = get_settings()
    documents = load_documents(settings.knowledge_base_dir)
    chunks = TextChunker(settings.chunk_size, settings.chunk_overlap).chunk_documents(documents)
    if len(documents) != 7:
        fail("seed/load demo documents", len(documents))
    if len(chunks) != 30:
        fail("chunk demo knowledge base", len(chunks))
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        for key in ["doc_id", "title", "source", "category", "chunk_id"]:
            if not metadata.get(key):
                fail("chunk metadata", {"chunk": chunk.get("id"), "missing": key})
    pass_line("seed/load/chunk demo knowledge base", {"documents": len(documents), "chunks": len(chunks)})
    return settings, documents, chunks


def assert_index_and_api(settings: Any) -> None:
    from fastapi.testclient import TestClient

    from app.main import app
    from app.rag.retriever import build_index

    index_result = build_index(settings)
    if index_result["document_count"] != 7 or index_result["chunk_count"] != 30:
        fail("build index", index_result)
    pass_line("build index", index_result)

    client = TestClient(app)
    response = client.get("/")
    if response.status_code != 200 or "NXP AIoT Cloud 智能客服系统" not in response.text:
        fail("GET / homepage", {"status": response.status_code, "body": response.text[:120]})
    pass_line("GET / homepage")

    health = client.get("/api/health").json()
    if health["status"] != "degraded" or health["ollama_connected"] is not False or "Ollama is not running" not in health.get("message", ""):
        fail("GET /api/health degraded without Ollama", health)
    if health["document_count"] != 7 or health["chunk_count"] != 30:
        fail("GET /api/health knowledge stats", health)
    pass_line("GET /api/health degraded without Ollama", health)

    stats = client.get("/api/stats").json()
    if stats["document_count"] != 7 or stats["chunk_count"] != 30 or "RAG" not in stats["categories"]:
        fail("GET /api/stats", stats)
    pass_line("GET /api/stats", stats)

    questions = client.get("/api/sample-questions").json()
    missing_questions = [question for question in SECTION_4_QUESTIONS + SECTION_12_QUESTIONS if question not in questions]
    if missing_questions:
        fail("GET /api/sample-questions", missing_questions)
    pass_line("GET /api/sample-questions", f"{len(questions)} questions")

    rebuild = client.post("/api/rebuild-index").json()
    if rebuild["status"] != "success" or rebuild["document_count"] != 7 or rebuild["chunk_count"] != 30:
        fail("POST /api/rebuild-index", rebuild)
    pass_line("POST /api/rebuild-index", rebuild)

    chat = client.post(
        "/api/chat",
        json={"question": "用户提问后，RAG 智能客服系统的完整处理流程是什么？", "top_k": 3},
    ).json()
    if not chat["answer"] or len(chat["sources"]) == 0 or len(chat["process"]) != 6:
        fail("POST /api/chat mock response", chat)
    if [step["name"] for step in chat["process"]] != PROCESS_NAMES:
        fail("POST /api/chat process names", chat["process"])
    if not all(0.0 <= source["score"] <= 1.0 for source in chat["sources"]):
        fail("POST /api/chat normalized scores", chat["sources"])
    if chat["metrics"]["model"] != "MOCK_LLM" or chat["metrics"]["retrieved_count"] != len(chat["sources"]):
        fail("POST /api/chat metrics", chat["metrics"])
    pass_line(
        "POST /api/chat mock response",
        {"sources": len(chat["sources"]), "process": len(chat["process"]), "model": chat["metrics"]["model"]},
    )

    no_source = client.post("/api/chat", json={"question": "zzzzzzzzzzzzzzzzzzzz", "top_k": 3}).json()
    expected = "当前知识库中没有找到明确依据，建议补充相关资料后再查询。"
    if expected not in no_source["answer"] or no_source["sources"]:
        fail("POST /api/chat no-source behavior", no_source)
    pass_line("POST /api/chat no-source behavior")


def assert_chat_with_ollama_down_subprocess() -> None:
    code = r'''
import os
import sys
from pathlib import Path

ROOT_DIR = Path.cwd()
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.rag.vector_store import reset_vector_store_files

settings = get_settings()
reset_vector_store_files(settings)
client = TestClient(app)
response = client.post(
    "/api/chat",
    json={"question": "用户提问后，RAG 智能客服系统的完整处理流程是什么？", "top_k": 3},
)
if response.status_code != 200:
    raise SystemExit(f"unexpected status: {response.status_code} {response.text}")
data = response.json()
if "调用本地 Ollama 模型失败" not in data["answer"]:
    raise SystemExit(f"missing friendly Ollama failure answer: {data['answer']}")
if not data["sources"]:
    raise SystemExit("chat should still return retrieved sources when only LLM generation fails")
if not any(step["status"] == "failed" for step in data["process"]):
    raise SystemExit(f"process should include failed step: {data['process']}")
print({"sources": len(data["sources"]), "failed_steps": [step["name"] for step in data["process"] if step["status"] == "failed"]})
'''
    env = os.environ.copy()
    env.update(
        {
            "MOCK_LLM": "false",
            "EMBED_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": "http://127.0.0.1:9",
        }
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    pass_line("POST /api/chat with Ollama down", completed.stdout.strip())


def configure_no_ollama_acceptance_env() -> None:
    os.environ["MOCK_LLM"] = "true"
    os.environ["EMBED_PROVIDER"] = "tfidf"
    os.environ["OLLAMA_BASE_URL"] = "http://127.0.0.1:9"


def main() -> int:
    configure_no_ollama_acceptance_env()
    checks = [
        ("required file structure", assert_required_files),
        (".env.example defaults", assert_env_example),
        ("no cloud model API dependency", assert_no_cloud_api_dependency),
        ("frontend static requirements", assert_frontend_static_requirements),
        ("README and docs", assert_readme_and_docs),
    ]
    for _name, check in checks:
        check()
    settings, _documents, _chunks = assert_seed_loader_chunker()
    assert_index_and_api(settings)
    assert_chat_with_ollama_down_subprocess()
    print("[PASS] task acceptance check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
