# API Reference

## GET /

返回 `frontend/index.html`，即课堂演示页面。

## GET /api/health

返回系统健康状态。

示例响应：

```json
{
  "status": "ok",
  "ollama_connected": true,
  "llm_model": "qwen2.5:7b",
  "embed_model": "nomic-embed-text",
  "knowledge_base_loaded": true,
  "document_count": 7,
  "chunk_count": 30,
  "vector_store": "chroma",
  "message": null
}
```

Ollama 未连接时：

```json
{
  "status": "degraded",
  "ollama_connected": false,
  "llm_model": "qwen2.5:7b",
  "embed_model": "nomic-embed-text",
  "knowledge_base_loaded": true,
  "document_count": 7,
  "chunk_count": 30,
  "vector_store": "simple",
  "message": "Ollama is not running or model is unavailable."
}
```

## GET /api/stats

返回知识库统计信息。

```json
{
  "document_count": 7,
  "chunk_count": 30,
  "categories": ["项目目标", "系统架构", "NXP AIoT Cloud", "Ara240 / Edge AI", "LLM Edge Studio", "VLM Edge Studio", "RAG"]
}
```

## GET /api/sample-questions

返回课堂演示问题数组。

示例响应包含任务书要求的主演示问题、备用问题和 API 示例问题：

```json
[
  "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，用来回答 Ara240、LLM Edge Studio 和边缘 AI 部署相关问题。请问这个系统应该采用什么整体架构？知识库怎么构建？用户提问后 RAG 的完整流程是什么？本地部署相比云端调用有什么优势？",
  "用户提问后，RAG 智能客服系统是如何从知识库中找到资料并生成回答的？",
  "LLM Edge Studio 和普通云端大模型调用有什么区别？它为什么适合边缘端智能应用？",
  "Ara240 DNPU 在边缘 AI 视觉分析任务中主要承担什么作用？",
  "为什么这个项目不直接使用通用大模型回答，而要加入本地知识库和 RAG 检索？",
  "我想基于 NXP AIoT Cloud 搭建一个离线运行的网站智能客服系统，应该采用什么整体架构？",
  "用户提问后，RAG 智能客服系统的完整处理流程是什么？",
  "本地大模型部署相比云端大模型调用有什么优势？",
  "LLM Edge Studio 的核心目标是什么？",
  "Ara240 DNPU 在边缘 AI 视觉任务中有什么作用？",
  "为什么智能客服系统需要知识库检索，而不是直接让大模型回答？"
]
```

## POST /api/rebuild-index

重新读取 `data/knowledge_base` 下的 `.md`、`.txt`、`.json` 文件，切分文本并构建向量索引。

示例响应：

```json
{
  "status": "success",
  "document_count": 7,
  "chunk_count": 30,
  "message": "Index rebuilt successfully.",
  "vector_store": "simple",
  "embedding_provider": "tfidf",
  "details": {
    "elapsed_ms": 120
  }
}
```

## POST /api/chat

请求：

```json
{
  "question": "用户提问后，RAG 智能客服系统的完整处理流程是什么？",
  "top_k": 3
}
```

响应：

```json
{
  "answer": "根据知识库资料，RAG 智能客服系统会先接收用户问题...",
  "sources": [
    {
      "rank": 1,
      "title": "RAG 智能客服问答流程",
      "source": "demo_knowledge_base",
      "category": "RAG",
      "score": 0.82,
      "content": "RAG 即检索增强生成..."
    }
  ],
  "process": [
    {
      "step": 1,
      "name": "接收用户问题",
      "status": "done",
      "detail": "后端成功接收用户输入。"
    }
  ],
  "metrics": {
    "latency_ms": 2350,
    "top_k": 3,
    "retrieved_count": 3,
    "model": "qwen2.5:7b"
  }
}
```

约束：

- `sources` 只来自实际检索结果。
- 检索不到资料时回答包含“当前知识库中没有找到明确依据，建议补充相关资料后再查询。”
- 模型调用失败时不让后端崩溃，返回友好提示和已检索来源。
