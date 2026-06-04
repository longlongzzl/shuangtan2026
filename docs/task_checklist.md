# 任务书逐项检查清单

检查对象：根目录 `codex开发任务书.md`

## 逐项状态

| 任务书章节 | 检查结果 |
| --- | --- |
| 一、总体要求 | 已完成 Python + FastAPI + Ollama + RAG + 原生前端；默认本地 Ollama；无云端大模型 API；支持 MOCK_LLM 但默认关闭。 |
| 二、技术栈 | 已使用 FastAPI、Uvicorn、Requests、Pydantic、python-dotenv、numpy、ChromaDB；前端为 HTML/CSS/JS。 |
| 三、项目目录结构 | 已创建指定目录和文件，并保留额外测试、文档和本机运行文件忽略规则。 |
| 四、后端接口设计 | 已实现 `GET /`、`/api/health`、`/api/stats`、`/api/sample-questions`、`/api/rebuild-index`、`/api/chat`。 |
| 五、RAG 具体实现 | 已实现文档加载、段落/句子切分、Ollama embedding、TF-IDF fallback、ChromaDB、SimpleVectorStore、Retriever、Prompt Builder。 |
| 六、Ollama 客户端要求 | 已实现 `health_check()`、`chat()`、`embed()`；支持 `/api/embed` 和 `/api/embeddings` fallback；请求带 timeout；错误可读。 |
| 七、前端页面要求 | 已实现三栏页面：系统状态、聊天区、RAG 流程和检索来源；无 React/Vue；无外部 CDN。 |
| 八、Demo 知识库内容 | 已通过 `scripts/seed_demo_data.py` 生成 7 个 Markdown 文件，并扩展为 30 个可检索 chunk。 |
| 九、README 要求 | README 已包含项目简介、mermaid 架构图、技术栈、目录、环境、Ollama、依赖、初始化、索引、启动、演示、排查、分工、扩展方向。 |
| 十、.env.example 要求 | 已按任务书提供默认配置，包括 qwen2.5:7b、nomic-embed-text、TOP_K、MIN_SCORE、CHUNK_SIZE、MOCK_LLM 等。 |
| 十一、文档要求 | 已完成 `project_design.md`、`demo_script.md`、`api_reference.md`。 |
| 十二、演示问题设计 | 已内置主演示问题和备用问题，并写入 README 与演示脚本。 |
| 十三、页面展示重点 | 前端右侧清楚展示问题向量化、知识库检索、Prompt 构造、本地模型生成和答案返回。 |
| 十四、测试要求 | 已实现 `scripts/smoke_test.py` 和 `tests/test_basic.py`，无 Ollama 时可用 MOCK/TF-IDF 测试。 |
| 十五、验收标准 | 已验证 seed、build_index、后端启动、网页健康检查、chat、RAG 流程、检索来源、无云端 API。 |
| 十六、代码质量要求 | 代码按模块拆分，路径使用 pathlib，错误处理清晰，前端 JS 独立，README 命令完整。 |
| 十七、实现顺序 | 已按要求从目录创建、配置、Ollama、RAG、接口、前端、文档、测试完成。 |
| 十八、不要做的事情 | 未使用 OpenAI API、云端大模型、登录注册、后台管理、React/Vue、外部 CDN；无来源时不编造来源。 |
| 十九、最终交付格式 | 最终回复将给出位置、文件、运行命令、模型准备、初始化、构建、启动、演示问题、完成项和验证结果。 |

## 最新验证结果

- `python scripts/seed_demo_data.py`：通过，生成 7 个 demo 文档。
- `python scripts/build_index.py`：通过，`document_count=7`，`chunk_count=30`，`vector_store=chroma`，`embedding_provider=ollama`。
- `python -m py_compile app/*.py app/rag/*.py scripts/*.py tests/*.py`：通过。
- `pytest -q`：通过，4 项测试。
- `python scripts/smoke_test.py`：通过，覆盖首页、健康检查、统计、示例问题、重建索引和 MOCK_LLM 聊天。
- 真实后端健康检查：通过，`ollama_connected=true`，模型为 `qwen2.5:7b` 和 `nomic-embed-text`。
