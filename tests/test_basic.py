from __future__ import annotations

from pathlib import Path

from app.rag.chunker import TextChunker
from app.rag.document_loader import Document, load_documents
from app.rag.embeddings import TfidfEmbeddingProvider
from app.rag.prompt_builder import build_rag_prompt
from app.rag.retriever import _keyword_score
from app.rag.vector_store import SimpleVectorStore
from app.schemas import ChatMetrics, ChatResponse, SourceItem


def test_runtime_context_is_injected_into_prompt() -> None:
    from app.main import _build_runtime_context

    stats = {
        "document_count": 17,
        "chunk_count": 134,
        "vector_store": "chroma",
        "categories": ["NXP AIoT Cloud", "Edge AI"],
    }

    runtime_context = _build_runtime_context(stats)
    messages = build_rag_prompt("你的资料数是多少？", [], runtime_context=runtime_context)
    full_prompt = "\n".join(message["content"] for message in messages)

    assert "当前本地知识库文档数量：17 篇" in full_prompt
    assert "当前可检索片段数量：134 个 chunks" in full_prompt
    assert "系统运行上下文" in full_prompt


def test_runtime_context_question_detector_handles_natural_variants() -> None:
    from app.main import _is_runtime_context_question

    assert _is_runtime_context_question("你的资料数是多少？")
    assert _is_runtime_context_question("你有多少可用资料")
    assert _is_runtime_context_question("当前知识库有哪些内容")
    assert _is_runtime_context_question("这系统能做啥啊")
    assert not _is_runtime_context_question("介绍一下 rag 智能客服")
    assert not _is_runtime_context_question("NXP Cloud Lab 系统方案有哪些")


def test_chunker_returns_non_empty_chunks() -> None:
    document = Document(
        doc_id="doc-1",
        title="测试文档",
        category="测试",
        source="pytest",
        content="第一段介绍 RAG 智能客服。第二段介绍本地大模型部署。第三段介绍知识库检索。",
        path="test.md",
    )
    chunks = TextChunker(chunk_size=120, chunk_overlap=20).chunk_documents([document])
    assert chunks
    assert all(chunk["text"].strip() for chunk in chunks)


def test_keyword_score_prefers_rag_customer_service_content() -> None:
    rag_chunk = {
        "text": "RAG 即检索增强生成，用户问题会先进入知识库检索，再构造 Prompt 给本地大模型生成智能客服回答。",
        "metadata": {"title": "RAG 智能客服问答流程", "category": "RAG", "source": "demo"},
    }
    unrelated_chunk = {
        "text": "Qwen2.5-VL 可用于视频分析和 VSS 视频检索场景。",
        "metadata": {"title": "Qwen2.5-VL 视频分析与 VSS 视频检索方案", "category": "VLM", "source": "demo"},
    }
    broad_project_chunk = {
        "text": "本项目目标是构建基于 Ollama 本地大语言模型和 RAG 技术的网站智能客服系统，完成从用户提问、知识库检索、大模型生成到网页展示的完整问答闭环。",
        "metadata": {"title": "实习项目的技术目标与学习目标", "category": "项目目标", "source": "demo"},
    }

    question = "介绍一下 rag 智能客服"
    long_question = "用户提问后 RAG 智能客服系统的完整处理流程是什么？"

    assert _keyword_score(question, rag_chunk) > 0.45
    assert _keyword_score(question, rag_chunk) > _keyword_score(question, unrelated_chunk)
    assert _keyword_score(long_question, rag_chunk) > _keyword_score(long_question, broad_project_chunk)


def test_prompt_builder_contains_question_and_context() -> None:
    source = SourceItem(
        rank=1,
        title="RAG 智能客服问答流程",
        source="demo",
        category="RAG",
        score=0.9,
        content="用户问题会先进入知识库检索，再构造 Prompt。",
    )
    messages = build_rag_prompt("RAG 如何工作？", [source])
    full_prompt = "\n".join(message["content"] for message in messages)
    assert "RAG 如何工作？" in full_prompt
    assert "用户问题会先进入知识库检索" in full_prompt
    assert "不要编造" in full_prompt
    assert "参考资料" in full_prompt


def test_document_loader_supports_md_txt_json(tmp_path: Path) -> None:
    (tmp_path / "plain.md").write_text("没有元数据的 Markdown 文档。", encoding="utf-8")
    (tmp_path / "with_meta.txt").write_text(
        "---\ntitle: TXT 标题\ncategory: TXT 分类\nsource: txt_source\n---\n\nTXT 正文。",
        encoding="utf-8",
    )
    (tmp_path / "structured.json").write_text(
        '{"title":"JSON 标题","category":"JSON 分类","source":"json_source","content":"JSON 正文。"}',
        encoding="utf-8",
    )

    documents = load_documents(tmp_path)
    by_title = {document.title: document for document in documents}

    assert len(documents) == 3
    assert "plain" in by_title
    assert by_title["TXT 标题"].category == "TXT 分类"
    assert by_title["TXT 标题"].source == "txt_source"
    assert by_title["JSON 标题"].category == "JSON 分类"
    assert by_title["JSON 标题"].source == "json_source"


def test_schemas_can_serialize() -> None:
    response = ChatResponse(
        answer="回答",
        sources=[],
        process=[],
        metrics=ChatMetrics(latency_ms=1, top_k=3, retrieved_count=0, model="mock"),
    )
    assert response.model_dump()["answer"] == "回答"


def test_simple_vector_store_cosine_similarity(tmp_path: Path) -> None:
    chunks = [
        {"id": "a", "text": "RAG 知识库检索", "metadata": {"doc_id": "1", "title": "RAG", "source": "demo", "category": "RAG"}},
        {"id": "b", "text": "Ara240 边缘 AI", "metadata": {"doc_id": "2", "title": "Ara240", "source": "demo", "category": "Edge AI"}},
    ]
    provider = TfidfEmbeddingProvider()
    embeddings = provider.embed_documents([chunk["text"] for chunk in chunks])
    store = SimpleVectorStore(tmp_path)
    store.add_chunks(
        chunks,
        embeddings,
        {"embedding_provider": "tfidf", "embedding_state": provider.get_state()},
    )
    query = provider.embed_query("RAG 检索")
    results = store.query(query, top_k=1)
    assert results[0].metadata["title"] == "RAG"
