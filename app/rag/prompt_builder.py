from __future__ import annotations

from app.schemas import SourceItem


SYSTEM_ROLE = (
    "你是 NXP AIoT Cloud 网站的智能客服。\n"
    "请严格根据“检索到的知识库资料”回答用户问题。\n"
    "不要编造知识库中没有的信息。\n"
    "如果资料中没有明确依据，请说：“当前知识库中没有找到明确依据。”\n"
    "回答要清晰、专业、适合网站客服场景。\n"
    "回答中可以使用编号或分点。\n"
    "回答最后必须列出“参考资料”。"
)


def build_context(sources: list[SourceItem]) -> str:
    if not sources:
        return "未检索到相关资料。"
    blocks = []
    for source in sources:
        blocks.append(
            "\n".join(
                [
                    f"[{source.rank}] 标题：{source.title}",
                    f"分类：{source.category}",
                    f"来源：{source.source}",
                    f"相似度：{source.score:.2f}",
                    f"内容：{source.content}",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_rag_prompt(question: str, sources: list[SourceItem]) -> list[dict[str, str]]:
    context = build_context(sources)
    user_prompt = f"""系统角色：
你是一个面向 NXP AIoT Cloud / Edge AI / 本地大模型实践项目的网站智能客服。你的回答必须基于本地知识库检索结果。

用户问题：
{question}

检索到的知识库资料：
{context}

回答要求：
1. 只根据资料回答。
2. 不要编造来源。
3. 如果资料不足，明确说明资料不足。
4. 用中文回答。
5. 适合课堂演示和网站客服场景。
6. 最后列出参考资料标题，格式为：
参考资料：
[1] 标题
[2] 标题
"""
    return [{"role": "system", "content": SYSTEM_ROLE}, {"role": "user", "content": user_prompt}]
