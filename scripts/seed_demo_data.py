from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = ROOT_DIR / "data" / "knowledge_base"


DOCUMENTS = {
    "01_project_goal.md": {
        "title": "实习项目的技术目标与学习目标",
        "category": "项目目标",
        "source": "demo_knowledge_base",
        "content": (
            "本项目目标是构建基于 Ollama 本地大语言模型和 RAG 技术的网站智能客服系统，完成从用户提问、知识库检索、大模型生成到网页展示的完整问答闭环。系统围绕 NXP AIoT Cloud、边缘 AI、本地大模型部署等资料构建本地知识库。学习目标包括掌握大模型本地推理、RAG 检索增强生成流程、文本切分、相似度检索、Prompt 构造、模块化后端开发和网页交互展示。"
            "\n\n课堂展示时，老师重点关注的不是单次回答是否像通用聊天机器人，而是系统能否说明回答依据。网页需要同时展示用户问题、检索到的知识片段、相似度分数、Prompt 构造步骤和本地模型生成结果，从而证明系统是基于资料回答。"
            "\n\n项目可以拆分为四个学习任务：第一是 FastAPI 后端接口和错误处理；第二是知识库文档加载、chunk 切分、embedding 和向量库检索；第三是 Ollama 本地模型调用和 mock 演示模式；第四是原生前端页面，把状态、流程和来源可视化。"
            "\n\n最终交付应能在普通实验室电脑上演示。即使 Ollama 暂时没有启动，也应通过健康检查、友好错误和 TF-IDF fallback 说明问题原因，避免后端崩溃或网页白屏。"
        ),
    },
    "02_system_architecture.md": {
        "title": "网站智能客服系统的架构组成",
        "category": "系统架构",
        "source": "demo_knowledge_base",
        "content": (
            "网站智能客服系统整体分为用户交互层、后端服务层、AI 服务与 RAG 模块、数据存储层。用户交互层通过网页界面接收用户问题并展示智能客服回答。后端服务层负责接收请求、调用 RAG 模块、调用本地大模型并整合返回结果。AI 服务与 RAG 模块负责问题向量化、知识库相似度检索、Prompt 构造和自然语言答案生成。数据存储层包含原始知识库文档和向量数据库，用于长期保存资料并支持后续扩展。"
            "\n\n用户交互层采用原生 HTML、CSS 和 JavaScript，不需要 Node.js 构建环境。页面左侧显示 Ollama 连接状态、模型名称、知识库文档数、chunk 数和向量库类型，中间提供聊天输入和示例问题，右侧展示 RAG 六步流程和 Top-k 检索来源。"
            "\n\n后端服务层使用 FastAPI。它提供健康检查、知识库统计、示例问题、索引重建和聊天接口。聊天接口不会直接把问题交给模型，而是先调用检索器获得资料，再把资料和问题拼接成受约束的 Prompt。"
            "\n\nAI 服务与 RAG 模块由多个小文件组成，避免把所有逻辑写在 main.py。文档加载器负责读取 Markdown、TXT 和 JSON；chunker 负责按段落和句子切分；embedding provider 负责生成向量；vector store 负责持久化和相似度查询；prompt builder 负责生成面向客服场景的提示词。"
            "\n\n数据存储层默认使用 ChromaDB 持久化向量库，目录位于 data/vector_store。如果 ChromaDB 不可用，系统会退回到本地 JSON 保存 chunk 和向量，并使用 numpy 余弦相似度完成检索。"
        ),
    },
    "03_nxp_aiot_cloud.md": {
        "title": "NXP AIoT Cloud 与 Cloud Lab",
        "category": "NXP AIoT Cloud",
        "source": "demo_knowledge_base",
        "content": (
            "NXP AIoT Cloud / Cloud Lab 面向开发者提供在线化的技术体验和方案学习环境，帮助用户远程了解开发板、软件工具和边缘智能解决方案。对于智能客服系统而言，NXP AIoT Cloud 相关资料可以作为领域知识库来源。系统可以整理平台介绍、用例说明、AI solution、开发板资源、边缘 AI 实践案例等内容，并通过 RAG 检索方式在用户提问时提供更加准确的回答。"
            "\n\n在课堂 Demo 中，NXP AIoT Cloud 可以被理解为领域知识入口。智能客服并不需要把所有平台细节写死到代码里，而是把介绍资料、实验步骤、开发板说明、边缘 AI 示例和常见问题放入本地知识库。"
            "\n\n当用户询问整体架构或实验路线时，系统先检索和 NXP AIoT Cloud 相关的资料片段，再由本地模型整理成适合网站客服的回答。这样回答会带有明确来源，方便老师查看系统是否真的使用了知识库。"
            "\n\n后续扩展时，可以把真实官网资料、课程讲义、实验截图说明和小组报告整理为 Markdown 或 JSON 文件。只要放入 data/knowledge_base 并重建索引，前端就能展示新的检索来源。"
        ),
    },
    "04_ara240_edge_ai.md": {
        "title": "Ara240 DNPU 与边缘 AI 视觉示例",
        "category": "Ara240 / Edge AI",
        "source": "demo_knowledge_base",
        "content": (
            "Ara240 是面向边缘端 AI 加速场景的独立神经网络处理单元 DNPU，可以与 NXP i.MX 系列处理器配合，用于视觉检测、视频分析和生成式 AI 等任务。在边缘 AI 视觉示例中，系统可以通过 GStreamer 构建多媒体处理管线，接入多路视频流，并结合 YOLOv8n 等轻量级检测模型完成目标检测。该类方案体现了边缘计算的特点，即尽量在数据产生端完成处理，降低云端依赖、减少延迟并提升隐私性。"
            "\n\n对于网站智能客服项目，Ara240 相关资料可以作为边缘 AI 知识库的一部分。用户可能会询问 DNPU 的作用、视觉分析流程、端侧推理优势或与 i.MX 平台协同的方式，RAG 检索可以把这些资料片段找出来作为回答依据。"
            "\n\n边缘 AI 视觉任务通常包含视频输入、预处理、模型推理、后处理和结果展示几个阶段。将这些阶段写入知识库后，客服系统可以用自然语言解释技术路线，而不是只给出泛泛的模型回答。"
            "\n\n本地部署的价值在于减少对云端接口的依赖。对于摄像头画面、工业现场数据或课堂实验环境，端侧处理能够降低传输延迟，也更容易说明隐私保护和离线运行优势。"
        ),
    },
    "05_llm_edge_studio.md": {
        "title": "LLM Edge Studio：边缘端大模型部署工具",
        "category": "LLM Edge Studio",
        "source": "demo_knowledge_base",
        "content": (
            "LLM Edge Studio 是面向边缘端大语言模型部署的图形化工具，目标是降低开发者在资源受限硬件上部署 LLM 的门槛。它可以帮助用户选择、加载和运行经过硬件适配的轻量级大语言模型，并支持模型参数配置、推理调用和结果调试。该工具体现了从云端大模型到端侧小模型的工程转化路径，适合用于离线智能问答、嵌入式代码辅助生成和本地交互式应用。"
            "\n\n与直接调用云端大模型不同，边缘端部署更强调模型体积、推理速度、内存占用和硬件适配。课堂演示可以把 Ollama 看作本地模型服务，把 LLM Edge Studio 看作端侧模型部署理念的延伸。"
            "\n\n在智能客服系统中，本地 LLM 负责把检索到的知识片段组织成自然语言回答。它不是唯一的信息来源，真正的回答依据来自知识库，这一点可以通过前端的来源列表和参考资料部分展示。"
            "\n\n如果机器性能有限，可以选择较小或量化后的模型进行演示。项目默认使用 qwen2.5:7b，是为了在回答质量和普通本地硬件可运行性之间取得平衡。"
        ),
    },
    "06_vlm_edge_studio.md": {
        "title": "VLM Edge Studio：边缘多模态 AI 演示",
        "category": "VLM Edge Studio",
        "source": "demo_knowledge_base",
        "content": (
            "VLM Edge Studio 面向边缘端多模态生成式 AI 场景，重点展示视觉语言模型在边缘设备上的应用。与单纯的大语言模型不同，视觉语言模型能够同时处理图像或视频与文本指令，使设备具备视觉问答和场景理解能力。在边缘端部署 VLM 可以让系统直接在本地处理摄像头画面和自然语言问题，适用于智能安防、工业检测、物流识别和现场辅助决策等场景。"
            "\n\n虽然本项目当前实现的是文本智能客服，但它的架构可以扩展到多模态知识问答。未来可以把图片说明、视频分析流程、模型输入输出格式和边缘设备部署步骤整理成知识库资料。"
            "\n\nVLM 场景更需要解释性，因为用户往往会问模型为什么识别某个物体、视觉输入如何进入模型、结果如何回到应用界面。RAG 可以把流程文档和实验记录检索出来，帮助生成更可靠的说明。"
            "\n\n课堂讲解时，可以把 VLM Edge Studio 作为后续扩展方向：当前页面展示文本 RAG 闭环，后续加入图像上传、视觉检测结果和多模态回答后，仍然沿用本地模型和来源可视化的设计思想。"
        ),
    },
    "07_rag_customer_service.md": {
        "title": "RAG 智能客服问答流程",
        "category": "RAG",
        "source": "demo_knowledge_base",
        "content": (
            "RAG 即检索增强生成，是将外部知识库检索与大语言模型生成能力结合的方法。在网站智能客服系统中，用户输入问题后，系统首先将问题转换为向量，然后在本地知识库中检索最相关的文档片段。接着系统将检索到的资料和用户问题拼接成 Prompt，交给本地大模型生成回答。相比直接让大模型回答，RAG 可以减少幻觉，提高专业领域问答的准确性，并且能够在网页上展示参考来源，使回答更加可解释。"
            "\n\n完整流程可以分为六步：接收用户问题、问题向量化、知识库检索、Prompt 构造、本地模型生成、返回答案与来源。前端右侧需要把这六步按状态展示出来，让演示观众看到系统内部链路。"
            "\n\n检索来源必须来自真实向量库查询结果，不能由模型编造。每条来源应包含标题、类别、来源、相似度和内容片段。模型回答末尾列出参考资料标题，方便把答案和知识库片段对应起来。"
            "\n\n如果检索不到资料，系统应明确说明当前知识库中没有找到明确依据，建议补充相关资料后再查询。这比让模型自由发挥更适合专业网站客服场景。"
            "\n\n如果本地模型调用失败，系统仍应返回已完成的流程状态和清晰提示。课堂演示可以临时打开 MOCK_LLM 模式，但默认运行路径仍然是本地 Ollama。"
        ),
    },
}


def render_markdown(payload: dict[str, str]) -> str:
    return (
        "---\n"
        f"title: {payload['title']}\n"
        f"category: {payload['category']}\n"
        f"source: {payload['source']}\n"
        "---\n\n"
        f"{payload['content']}\n"
    )


def main() -> None:
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    for filename, payload in DOCUMENTS.items():
        path = KNOWLEDGE_BASE_DIR / filename
        path.write_text(render_markdown(payload), encoding="utf-8")
        print(f"written: {path.relative_to(ROOT_DIR)}")
    print(f"demo knowledge base ready: {len(DOCUMENTS)} documents")


if __name__ == "__main__":
    main()
