from __future__ import annotations

from pathlib import Path

from app.rag.chunker import TextChunker
from app.rag.document_loader import Document, load_documents
from app.rag.embeddings import TfidfEmbeddingProvider
from app.rag.prompt_builder import build_rag_prompt
from app.rag.vector_store import SimpleVectorStore
from app.schemas import ChatMetrics, ChatResponse, SourceItem


def test_knowledge_stats_answer_reports_counts() -> None:
    from app.main import _build_knowledge_stats_answer, _is_knowledge_stats_question

    question = "你有多少可用资料？"
    stats = {
        "document_count": 17,
        "chunk_count": 134,
        "vector_store": "chroma",
        "categories": ["NXP AIoT Cloud", "Edge AI"],
    }

    assert _is_knowledge_stats_question(question)
    answer = _build_knowledge_stats_answer(question, stats)
    assert "17 篇资料" in answer
    assert "134 个可检索片段" in answer
    assert "chroma" in answer


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
