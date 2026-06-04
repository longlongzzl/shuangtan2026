---
title: 网站智能客服系统的架构组成
category: 系统架构
source: demo_knowledge_base
---

网站智能客服系统整体分为用户交互层、后端服务层、AI 服务与 RAG 模块、数据存储层。用户交互层通过网页界面接收用户问题并展示智能客服回答。后端服务层负责接收请求、调用 RAG 模块、调用本地大模型并整合返回结果。AI 服务与 RAG 模块负责问题向量化、知识库相似度检索、Prompt 构造和自然语言答案生成。数据存储层包含原始知识库文档和向量数据库，用于长期保存资料并支持后续扩展。

用户交互层采用原生 HTML、CSS 和 JavaScript，不需要 Node.js 构建环境。页面左侧显示 Ollama 连接状态、模型名称、知识库文档数、chunk 数和向量库类型，中间提供聊天输入和示例问题，右侧展示 RAG 六步流程和 Top-k 检索来源。

后端服务层使用 FastAPI。它提供健康检查、知识库统计、示例问题、索引重建和聊天接口。聊天接口不会直接把问题交给模型，而是先调用检索器获得资料，再把资料和问题拼接成受约束的 Prompt。

AI 服务与 RAG 模块由多个小文件组成，避免把所有逻辑写在 main.py。文档加载器负责读取 Markdown、TXT 和 JSON；chunker 负责按段落和句子切分；embedding provider 负责生成向量；vector store 负责持久化和相似度查询；prompt builder 负责生成面向客服场景的提示词。

数据存储层默认使用 ChromaDB 持久化向量库，目录位于 data/vector_store。如果 ChromaDB 不可用，系统会退回到本地 JSON 保存 chunk 和向量，并使用 numpy 余弦相似度完成检索。
