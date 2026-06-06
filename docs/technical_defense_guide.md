# 技术细节与答辩准备

## 1. 项目一句话说明

本项目是一个基于本地大模型和 RAG 技术的网站智能客服系统。它把 NXP AIoT Cloud、Cloud Lab、Ara240、Edge AI、LLM Edge Studio、VLM Edge Studio 等资料整理成本地知识库，用户在网页提问后，系统先检索相关资料，再把检索片段和问题一起交给本地 Ollama 模型生成回答，并在页面上展示回答依据、相似度和处理流程。

项目重点不是简单调用大模型，而是完整展示“资料入库、文本切分、向量化、检索、Prompt 构造、本地生成、来源追溯”的闭环。

## 2. 技术架构

系统分为四层：

1. 前端交互层

   使用原生 HTML、CSS、JavaScript 实现三栏页面。左侧显示模型和知识库状态，中间是聊天区和问题输入，右侧展示 RAG 六步流程和检索来源。没有引入 React、Vue 或外部 CDN，降低课堂演示环境依赖。

2. 后端服务层

   使用 FastAPI 提供接口，Uvicorn 作为 ASGI 服务器。后端负责接收问题、检查知识库索引、调用检索模块、构造 Prompt、调用 Ollama，并把回答、来源和指标返回给前端。

3. RAG 检索层

   知识库文件保存在 `data/knowledge_base/`，索引保存在 `data/vector_store/`。系统通过文档加载、chunk 切分、embedding 向量化、向量检索和关键词补充分数找到最相关的资料片段。

4. 本地模型层

   默认使用 Ollama 本地服务，LLM 模型是 `qwen2.5:7b`，embedding 模型是 `nomic-embed-text`。默认不依赖 OpenAI、ChatGPT API 或其他云端大模型接口。

## 3. 核心请求流程

用户点击发送后，主要流程如下：

1. `POST /api/chat` 接收用户问题。
2. 后端检查 `data/vector_store/index_meta.json`，如果索引不存在或为空，会自动构建索引。
3. 如果是问系统状态、资料数量、知识库范围等问题，后端直接使用运行时上下文回答，避免无意义检索。
4. 普通业务问题会进入 Retriever，先把问题转换成 embedding 向量。
5. 向量库返回候选片段，同时系统计算关键词匹配分数。
6. 后端融合向量结果和关键词结果，按文档聚合，返回 Top-K 来源。
7. Prompt Builder 把系统角色、运行上下文、用户问题和检索资料拼成 RAG Prompt。
8. Ollama 使用 `qwen2.5:7b` 生成回答。
9. 前端展示回答、参考资料、相似度、耗时和六步流程状态。

对应代码入口：

- `app/main.py`：FastAPI 接口、聊天流程、健康检查。
- `app/rag/retriever.py`：索引构建、向量检索、关键词补充分数、结果融合。
- `app/rag/embeddings.py`：Ollama embedding 和 TF-IDF fallback。
- `app/rag/vector_store.py`：ChromaDB 和 SimpleVectorStore。
- `app/rag/prompt_builder.py`：RAG Prompt 约束。
- `app/ollama_client.py`：Ollama 本地服务调用。

## 4. 知识库与索引设计

知识库使用 Markdown 文件维护，优点是易读、易改、适合课程展示。每份文档包含标题、分类、来源和正文。系统加载文档后按固定 chunk 大小切分，默认参数是：

- `CHUNK_SIZE=500`
- `CHUNK_OVERLAP=80`
- `TOP_K=3`
- `MIN_SCORE=0.1`

chunk overlap 的作用是避免关键信息刚好被切断。例如一个概念的定义在上一个片段末尾，应用场景在下一个片段开头，如果没有重叠，检索可能只拿到半段信息。

当前知识库覆盖 NXP AIoT Cloud / Cloud Lab、AI Hub、Model Zoo、LLM/VLM Edge Studio、Qwen/VSS、YOLOv8n、Ara240、i.MX、MCU 应用和系统方案等内容。

## 5. 向量库与降级机制

系统优先使用 ChromaDB 持久化向量库。ChromaDB 不可用时，会退回到项目自带的 `SimpleVectorStore`，它用 JSON 保存 chunk、metadata 和 embedding，再用 numpy 计算余弦相似度。

embedding 默认由 Ollama 的 `nomic-embed-text` 生成。如果 Ollama 或 embedding 模型不可用，构建索引时会退回 TF-IDF。TF-IDF 不是大模型语义向量，但能保证课堂演示时仍然可以完成“检索来源、展示流程、生成 mock 回答”的基本闭环。

这个设计的目的不是让降级效果超过 embedding，而是保证系统具有可演示性和容错性。

## 6. Prompt 设计

Prompt 分为 system role 和 user prompt 两部分。核心约束包括：

- 回答必须依据系统运行上下文或检索到的本地知识库资料。
- 不允许编造来源。
- 如果依据不足，要明确说“当前知识库中没有找到明确依据”。
- 回答最后必须列出实际使用的参考资料。
- 如果问题是系统自身状态，参考资料列“系统运行上下文”。

这样做可以减少大模型幻觉，并让老师看到 RAG 相比直接问大模型的优势：答案不是凭空生成，而是和本地资料片段绑定。

## 7. API 设计

主要接口如下：

- `GET /`：返回前端页面。
- `GET /api/health`：返回 Ollama 连接状态、模型名、知识库文档数、chunk 数和向量库类型。
- `GET /api/stats`：返回知识库统计。
- `GET /api/sample-questions`：返回演示问题。
- `POST /api/rebuild-index`：重新构建知识库索引。
- `POST /api/chat`：执行 RAG 检索和本地模型回答。

`/api/health` 是演示时很重要的接口。它能快速判断问题出在模型服务、模型文件、知识库还是前端页面。

## 8. 本地部署细节

正式部署时 Ollama 安装在常见系统位置：

- 可执行文件：`/usr/local/bin/ollama`
- 实际安装目录：`/usr/local/lib/ollama`
- systemd 服务：`ollama.service`
- 模型目录：`/home/zhangzhao/.ollama/models`
- 服务地址：`http://127.0.0.1:11434`

已准备的模型：

- `qwen2.5:7b`：负责生成客服回答。
- `nomic-embed-text`：负责问题和文档片段向量化。

启动项目：

```bash
cd nxp-aiot-local-chatbot
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

检查状态：

```bash
curl http://127.0.0.1:8000/api/health
ollama list
systemctl status ollama
```

## 9. 项目亮点

1. 本地化部署

   默认不调用云端大模型 API，适合隐私敏感、网络不稳定或边缘端场景。

2. RAG 全流程可视化

   页面展示接收问题、向量化、检索、Prompt 构造、模型生成、返回答案六个步骤，便于答辩讲解。

3. 来源可追溯

   回答会返回参考资料标题、分类、来源和相似度，不是只给一个无法验证的自然语言答案。

4. 多级降级

   ChromaDB 不可用时退回 SimpleVectorStore，Ollama embedding 不可用时退回 TF-IDF，模型不可用时可用 `MOCK_LLM=true` 演示页面流程。

5. 易扩展

   后续可以增加知识库上传、多轮会话、用户反馈、模型切换、后台管理和真实设备资料同步。

## 10. 演示检查清单

答辩前建议按顺序检查：

```bash
systemctl is-active ollama
ollama list
python scripts/build_index.py
python scripts/smoke_test.py
python scripts/acceptance_check.py
pytest -q
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

打开浏览器访问：

```text
http://127.0.0.1:8000/
```

重点演示：

- 左侧模型连接状态是正常。
- 知识库文档数和 chunk 数能显示。
- 点击示例问题能自动填入输入框。
- 发送问题后右侧 RAG 流程逐步完成。
- 回答下面能看到检索来源和相似度。
- 关闭 Ollama 后 `/api/health` 会变成 degraded，页面不会白屏。

## 11. 老师可能提问与回答

### 1. 这个项目和普通 ChatGPT 网页套壳有什么区别？

普通套壳主要是把用户问题直接发给大模型。本项目的重点是 RAG：先从本地知识库检索资料，再把资料片段和问题一起交给本地模型生成回答。回答有来源、有相似度、有处理流程展示，而且默认不依赖云端 API。

### 2. 为什么要用 RAG，不直接让大模型回答？

直接问大模型容易出现两个问题：一是模型可能不知道项目内的专有资料，二是可能编造答案。RAG 把回答限制在本地知识库范围内，可以提高专业资料问答的准确性，也方便展示“答案来自哪份文档”。

### 3. 为什么选择本地大模型？

本地大模型有三个优势：数据不出本机、网络不可用时仍可运行、演示成本可控。这个项目定位是 NXP AIoT / Edge AI 场景，边缘端和本地部署本身就是重要主题，所以使用 Ollama 更符合项目设定。

### 4. 为什么选择 FastAPI？

FastAPI 写接口很清晰，支持 Pydantic 数据模型，适合快速实现结构化 API。这个项目需要返回回答、来源、流程步骤和耗时指标，FastAPI 能比较自然地表达这些响应结构。

### 5. 为什么前端不用 React 或 Vue？

课堂 Demo 更看重可运行和可解释。原生 HTML/CSS/JS 不需要 Node.js、构建工具和外部 CDN，启动后端就能打开页面，部署风险更低。

### 6. ChromaDB 的作用是什么？

ChromaDB 用来持久化保存文档片段的 embedding 向量和 metadata。用户提问时，系统把问题也向量化，然后在向量库中找相似度最高的片段，这就是 RAG 检索的核心。

### 7. SimpleVectorStore 是不是重复造轮子？

它不是为了替代 ChromaDB，而是 fallback。课堂环境中可能遇到 ChromaDB 安装失败、依赖冲突等问题，SimpleVectorStore 可以保证演示不中断。正式场景仍优先使用 ChromaDB。

### 8. TF-IDF fallback 有什么意义？

TF-IDF 的语义能力不如 embedding，但它不依赖 Ollama 模型，可以在本地模型不可用时保证基础检索流程能跑通。它体现的是系统容错设计。

### 9. 你们怎么减少模型幻觉？

主要有三点：第一，Prompt 明确要求只能根据系统上下文和检索资料回答；第二，回答最后必须列出实际使用的参考资料；第三，如果资料不足，要直接说明没有明确依据，而不是编造。

### 10. 如果检索出来的资料不相关怎么办？

系统有 `MIN_SCORE` 阈值和 Top-K 控制，低于阈值的片段不会进入来源列表。Prompt 也要求如果检索资料与问题不相关，要回答“当前知识库中没有找到明确依据”。

### 11. 关键词检索为什么还要保留？

纯向量检索有时会漏掉专有名词、型号或缩写。项目中加入关键词补充分数，可以提高 Ara240、LLM Edge Studio、Qwen、VSS 这类关键词的召回稳定性。

### 12. chunk 大小为什么设为 500，重叠为什么是 80？

500 字左右能保留一个相对完整的知识点，又不会让 Prompt 过长。80 的重叠可以避免切分边界把一个概念拆断。这个参数不是唯一答案，可以根据资料长度和模型上下文窗口继续调优。

### 13. Top-K 为什么默认是 3？

Top-K 太小可能漏资料，太大会把不相关内容塞进 Prompt，增加噪声。对于课堂 Demo 和当前知识库规模，3 个来源比较容易讲清楚，也能控制回答长度。

### 14. 这个项目能不能支持多轮对话？

当前版本主要做单轮 RAG 问答，重点展示检索增强流程。要支持多轮，可以在后端增加会话 ID 和历史消息存储，再把最近几轮对话摘要加入 Prompt。

### 15. 这个系统如何更新知识库？

目前可以把 Markdown、TXT、JSON 资料放进 `data/knowledge_base/`，然后调用 `POST /api/rebuild-index` 或运行 `python scripts/build_index.py` 重建索引。后续可以增加网页上传和后台管理。

### 16. 如果资料很多，系统会有什么瓶颈？

主要瓶颈在 embedding 构建耗时、向量库查询性能、Prompt 长度和模型生成速度。解决方向包括批量 embedding、增量索引、使用更专业的向量数据库、重排序模型和更强的本地推理硬件。

### 17. 为什么健康检查接口很重要？

因为本地 RAG 系统涉及前端、后端、Ollama、LLM 模型、embedding 模型、知识库索引多个环节。`/api/health` 可以快速定位当前是否是模型没启动、模型没拉取、知识库没加载或向量库异常。

### 18. 项目如何保证没有依赖云端大模型？

代码中默认调用的是本机 `OLLAMA_BASE_URL=http://localhost:11434`。验收脚本也检查了 OpenAI、Anthropic、DashScope、Moonshot 等云端 API 关键词，避免误引入云端模型依赖。

### 19. 你们的知识库资料是否实时？

当前知识库是本地静态资料，优点是离线稳定，缺点是不会自动同步最新官网内容。后续可以增加资料爬取、人工审核和定时重建索引流程。

### 20. 如果老师现场关闭 Ollama，会发生什么？

系统不会白屏。`/api/health` 会显示 degraded，聊天接口会返回友好提示；如果设置 `MOCK_LLM=true`，还可以继续演示前端、检索来源和 RAG 流程。

### 21. 这个项目和 NXP AIoT Cloud 本体是什么关系？

本项目不是 NXP AIoT Cloud 在线平台本体，而是围绕 NXP AIoT / Edge AI 相关资料构建的本地智能客服 Demo。它展示的是如何用本地 RAG 技术帮助用户理解这些资料和方案。

### 22. 你认为项目最大的技术难点是什么？

难点不是单独启动一个模型，而是把资料管理、检索质量、Prompt 约束、前端可视化和异常降级串成稳定闭环。尤其是本地环境中模型、向量库和依赖都可能不可用，所以需要多级 fallback。

### 23. 如果要上线生产环境，还需要补什么？

需要增加用户鉴权、日志审计、会话管理、知识库上传审核、增量索引、回答质量评估、敏感信息过滤、模型资源监控和更完善的错误告警。

### 24. 这个项目怎么体现工程完整性？

它不仅有功能代码，还有 README、API 文档、设计文档、演示脚本、验收脚本、测试用例和降级方案。答辩时可以从“能运行、能解释、能验证、能扩展”四个角度说明。

## 12. 答辩时推荐讲解顺序

1. 先打开页面，说明这是本地 RAG 智能客服，不是云端 API 套壳。
2. 展示左侧健康状态，说明 Ollama、模型、知识库和向量库都可观测。
3. 发送主演示问题，观察右侧六步 RAG 流程。
4. 展示回答下面的参考资料和相似度，强调来源可追溯。
5. 简单打开 `app/main.py` 和 `app/rag/retriever.py`，说明接口入口和检索融合逻辑。
6. 最后讲降级机制：Ollama、ChromaDB、embedding 出问题时系统如何保证演示不中断。

