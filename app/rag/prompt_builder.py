from __future__ import annotations

from app.schemas import SourceItem


SYSTEM_ROLE = (
    "你是 NXP AIoT Cloud 网站的智能客服。\n"
    "请根据“系统运行上下文”和“检索到的知识库资料”回答用户问题。\n"
    "系统运行上下文由后端实时生成，可用于回答知识库数量、资料范围、索引状态等系统自身问题。\n"
    "检索到的知识库资料用于回答 NXP AIoT Cloud、Edge AI、应用范例和系统方案等领域问题。\n"
    "不要编造上下文和资料中没有的信息。\n"
    "如果两类依据都没有明确答案，请说：“当前知识库中没有找到明确依据。”\n"
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


def build_rag_prompt(
    question: str,
    sources: list[SourceItem],
    runtime_context: str | None = None,
) -> list[dict[str, str]]:
    context = build_context(sources)
    runtime = runtime_context or "未提供系统运行上下文。"
    user_prompt = f"""系统角色：
你是一个面向 NXP AIoT Cloud / Edge AI / 本地大模型实践项目的网站智能客服。你的回答必须基于后端提供的系统运行上下文和本地知识库检索结果。

系统运行上下文：
{runtime}

用户问题：
{question}

检索到的知识库资料：
{context}

回答要求：
1. 用户问系统自身、资料数量、资料范围、知识库规模、索引状态时，优先使用“系统运行上下文”。
2. 用户问具体 NXP 技术内容时，优先使用“检索到的知识库资料”。
3. 不要编造来源。
4. 如果依据不足，明确说明资料不足。
5. 用中文回答。
6. 适合课堂演示和网站客服场景。
7. 最后列出参考资料标题，格式为：
参考资料：
[1] 系统运行上下文
[2] 标题
"""
    return [{"role": "system", "content": SYSTEM_ROLE}, {"role": "user", "content": user_prompt}]
