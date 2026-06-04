from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = ROOT_DIR / "data" / "knowledge_base"


DOCUMENTS = {
    "01_project_goal.md": {
        "title": "实习项目的技术目标与学习目标",
        "category": "项目目标",
        "source": "demo_knowledge_base",
        "content": "本项目目标是构建基于 Ollama 本地大语言模型和 RAG 技术的网站智能客服系统，完成从用户提问、知识库检索、大模型生成到网页展示的完整问答闭环。系统围绕 NXP AIoT Cloud、边缘 AI、本地大模型部署等资料构建本地知识库。学习目标包括掌握大模型本地推理、RAG 检索增强生成流程、文本切分、相似度检索、Prompt 构造、模块化后端开发和网页交互展示。",
    },
    "02_system_architecture.md": {
        "title": "网站智能客服系统的架构组成",
        "category": "系统架构",
        "source": "demo_knowledge_base",
        "content": "网站智能客服系统整体分为用户交互层、后端服务层、AI 服务与 RAG 模块、数据存储层。用户交互层通过网页界面接收用户问题并展示智能客服回答。后端服务层负责接收请求、调用 RAG 模块、调用本地大模型并整合返回结果。AI 服务与 RAG 模块负责问题向量化、知识库相似度检索、Prompt 构造和自然语言答案生成。数据存储层包含原始知识库文档和向量数据库，用于长期保存资料并支持后续扩展。",
    },
    "03_nxp_aiot_cloud.md": {
        "title": "NXP AIoT Cloud 与 Cloud Lab",
        "category": "NXP AIoT Cloud",
        "source": "demo_knowledge_base",
        "content": "NXP AIoT Cloud / Cloud Lab 面向开发者提供在线化的技术体验和方案学习环境，帮助用户远程了解开发板、软件工具和边缘智能解决方案。对于智能客服系统而言，NXP AIoT Cloud 相关资料可以作为领域知识库来源。系统可以整理平台介绍、用例说明、AI solution、开发板资源、边缘 AI 实践案例等内容，并通过 RAG 检索方式在用户提问时提供更加准确的回答。",
    },
    "04_ara240_edge_ai.md": {
        "title": "Ara240 DNPU 与边缘 AI 视觉示例",
        "category": "Ara240 / Edge AI",
        "source": "demo_knowledge_base",
        "content": "Ara240 是面向边缘端 AI 加速场景的独立神经网络处理单元 DNPU，可以与 NXP i.MX 系列处理器配合，用于视觉检测、视频分析和生成式 AI 等任务。在边缘 AI 视觉示例中，系统可以通过 GStreamer 构建多媒体处理管线，接入多路视频流，并结合 YOLOv8n 等轻量级检测模型完成目标检测。该类方案体现了边缘计算的特点，即尽量在数据产生端完成处理，降低云端依赖、减少延迟并提升隐私性。",
    },
    "05_llm_edge_studio.md": {
        "title": "LLM Edge Studio：边缘端大模型部署工具",
        "category": "LLM Edge Studio",
        "source": "demo_knowledge_base",
        "content": "LLM Edge Studio 是面向边缘端大语言模型部署的图形化工具，目标是降低开发者在资源受限硬件上部署 LLM 的门槛。它可以帮助用户选择、加载和运行经过硬件适配的轻量级大语言模型，并支持模型参数配置、推理调用和结果调试。该工具体现了从云端大模型到端侧小模型的工程转化路径，适合用于离线智能问答、嵌入式代码辅助生成和本地交互式应用。",
    },
    "06_vlm_edge_studio.md": {
        "title": "VLM Edge Studio：边缘多模态 AI 演示",
        "category": "VLM Edge Studio",
        "source": "demo_knowledge_base",
        "content": "VLM Edge Studio 面向边缘端多模态生成式 AI 场景，重点展示视觉语言模型在边缘设备上的应用。与单纯的大语言模型不同，视觉语言模型能够同时处理图像或视频与文本指令，使设备具备视觉问答和场景理解能力。在边缘端部署 VLM 可以让系统直接在本地处理摄像头画面和自然语言问题，适用于智能安防、工业检测、物流识别和现场辅助决策等场景。",
    },
    "07_rag_customer_service.md": {
        "title": "RAG 智能客服问答流程",
        "category": "RAG",
        "source": "demo_knowledge_base",
        "content": "RAG 即检索增强生成，是将外部知识库检索与大语言模型生成能力结合的方法。在网站智能客服系统中，用户输入问题后，系统首先将问题转换为向量，然后在本地知识库中检索最相关的文档片段。接着系统将检索到的资料和用户问题拼接成 Prompt，交给本地大模型生成回答。相比直接让大模型回答，RAG 可以减少幻觉，提高专业领域问答的准确性，并且能够在网页上展示参考来源，使回答更加可解释。",
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
