# 项目方案设计

## 项目背景

课程展示需要一个能运行、能讲清楚技术链路的网站智能客服系统。项目围绕 NXP AIoT Cloud、Cloud Lab、Ara240 DNPU、Edge AI、LLM Edge Studio、VLM Edge Studio 和本地大模型部署等主题，构建可扩展的本地知识库，并用 RAG 技术减少模型幻觉。

## 项目目标

- 实现网页端提问、后端接收、知识库检索、本地模型生成、来源展示的完整闭环。
- 默认使用本机 Ollama，不依赖云端大模型 API。
- 页面突出 RAG 流程，便于老师看到问题向量化、知识库检索、Prompt 构造和模型生成。
- 内置 demo 知识库，即使暂时没有真实资料也可以完成课堂演示。

## 系统架构

系统分为四层：

1. 用户交互层：原生 HTML/CSS/JS 三栏页面，展示系统状态、聊天、RAG 流程和检索来源。
2. 后端服务层：FastAPI 提供健康检查、统计、索引重建、聊天等接口。
3. AI 与 RAG 层：文档加载、文本切分、embedding、向量检索、Prompt 构造、Ollama 调用。
4. 数据存储层：`data/knowledge_base` 保存原始资料，`data/vector_store` 保存 ChromaDB 或 JSON fallback 索引。

## RAG 流程

1. 用户在网页输入问题。
2. FastAPI 接收请求并记录流程状态。
3. Retriever 使用 embedding provider 将问题转换为向量。
4. 向量库执行 Top-k 相似度检索，返回标题、类别、来源、分数和内容片段。
5. Prompt Builder 将问题和检索片段拼接成带约束的 RAG Prompt。
6. Ollama 本地模型通过 `/api/chat` 生成回答。
7. 前端展示回答、引用来源、流程状态和耗时指标。

## 技术选型

- FastAPI：接口定义清晰，适合快速构建 Demo。
- Ollama：本地部署 LLM 和 embedding 模型，符合离线演示需求。
- ChromaDB：作为优先向量库，支持持久化。
- SimpleVectorStore：当 ChromaDB 不可用时，用 JSON + numpy 余弦相似度保证可运行。
- TF-IDF fallback：当 Ollama embedding 不可用时，仍能完成基础检索。
- 原生前端：避免 Node.js 环境依赖，启动后端即可打开网页。

## 前端展示设计

页面采用三栏布局：

- 左侧显示模型连接、模型名称、知识库数量、向量库类型和重建索引按钮。
- 中间展示聊天消息、示例问题、Top-K 控制和输入框。
- 右侧展示六步 RAG 流程和 Top-k 检索来源，来源支持展开查看内容片段。

## 测评指标

- 能否启动服务并打开网页。
- 能否生成 demo 知识库和索引。
- 能否在无 Ollama 时优雅降级。
- 能否展示回答、来源、相似度和 RAG 流程。
- 代码结构是否清晰，是否便于小组后续分工。

## 风险与解决方案

- Ollama 未启动：返回降级状态，回答中提示启动 Ollama；可用 `MOCK_LLM=true` 演示。
- embedding 模型未拉取：构建索引自动退回 TF-IDF。
- ChromaDB 安装失败：自动退回 SimpleVectorStore。
- 知识库不足：回答明确说明资料不足，不编造来源。
- 演示网络不可用：所有 demo 资料本地内置，不依赖外网。
