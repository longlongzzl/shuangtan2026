from __future__ import annotations

from app.schemas import SourceItem


def generate_mock_answer(question: str, sources: list[SourceItem]) -> str:
    if not sources:
        return "当前知识库中没有找到明确依据，建议补充相关资料后再查询。"

    lines = [
        "以下回答来自 MOCK_LLM 模式，便于在没有 Ollama 的环境中演示完整流程。",
        "",
        f"针对问题“{question}”，可以根据知识库这样理解：",
    ]
    for index, source in enumerate(sources, start=1):
        snippet = source.content.strip().replace("\n", " ")
        lines.append(f"{index}. {source.title}：{snippet[:160]}")

    lines.extend(
        [
            "",
            "总结来看，系统应先建设本地知识库并完成向量化索引，用户提问后通过 RAG 检索获得依据，再把依据交给本地大模型生成客服回答。",
            "",
            "参考资料：",
        ]
    )
    lines.extend(f"[{index}] {source.title}" for index, source in enumerate(sources, start=1))
    return "\n".join(lines)
