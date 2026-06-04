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
    "回答最后必须列出实际使用的“参考资料”。"
)


def build_context(sources: list[SourceItem]) -> str:
    if not sources:
        return "本轮没有可用的知识库资料片段；如果用户问题属于系统自身、资料数量或资料范围，请直接依据系统运行上下文回答。"

    grouped: dict[tuple[str, str, str], dict[str, object]] = {}
    for source in sources:
        key = (source.title, source.category, source.source)
        group = grouped.setdefault(
            key,
            {
                "title": source.title,
                "category": source.category,
                "source": source.source,
                "score": source.score,
                "contents": [],
            },
        )
        group["score"] = max(float(group["score"]), source.score)
        contents = group["contents"]
        if isinstance(contents, list):
            contents.append(source.content)

    blocks = []
    for rank, group in enumerate(grouped.values(), start=1):
        contents = group["contents"] if isinstance(group["contents"], list) else []
        content_text = "\n".join(f"- {content}" for content in contents)
        blocks.append(
            "\n".join(
                [
                    f"[{rank}] 标题：{group['title']}",
                    f"分类：{group['category']}",
                    f"来源：{group['source']}",
                    f"最高相似度：{float(group['score']):.2f}",
                    f"内容：\n{content_text}",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_rag_prompt(
    question: str,
    sources: list[SourceItem],
    runtime_context: str | None = None,
    runtime_only: bool = False,
) -> list[dict[str, str]]:
    context = "本轮问题属于系统自身、资料数量、资料范围或能力问题，无需知识库资料片段。" if runtime_only else build_context(sources)
    runtime = runtime_context or "本轮未提供系统运行上下文。"
    mode_instruction = (
        "本轮请直接依据系统运行上下文回答，不要因为没有知识库片段而说资料不足；如果用户问系统能做什么，请回答本地 RAG 客服系统能力，不要把 NXP AIoT Cloud 平台能力说成本系统能力。"
        if runtime_only
        else "本轮请优先依据检索到的知识库资料回答；如果系统运行上下文显示未提供，不要引用它。"
    )
    reference_example = "[1] 系统运行上下文" if runtime_context else "[1] 标题"
    user_prompt = f"""系统角色：
你是一个面向 NXP AIoT Cloud / Edge AI / 本地大模型实践项目的网站智能客服。你的回答必须基于本轮提供的系统运行上下文或本地知识库检索结果。

本轮回答模式：
{mode_instruction}

系统运行上下文：
{runtime}

用户问题：
{question}

检索到的知识库资料：
{context}

回答要求：
1. 用户问系统自身、资料数量、资料范围、知识库规模、索引状态时，优先使用“系统运行上下文”。
2. 用户问具体 NXP 技术内容或 RAG 业务内容时，优先使用“检索到的知识库资料”；不要主动加入文档数量、向量库名称等运行状态，除非用户明确询问。
3. 不要编造来源。
4. 如果依据不足，明确说明资料不足。
5. 用中文回答。
6. 适合课堂演示和网站客服场景。
7. 最后只列出实际使用的参考资料标题；同一标题只列一次；如果答案依据系统运行上下文，必须列出“系统运行上下文”；如果没有使用系统运行上下文，不要把它列入参考资料。
8. 如果检索资料与用户问题不相关，应回答“当前知识库中没有找到明确依据。”，参考资料写“无”。
参考资料格式为：
参考资料：
{reference_example}
"""
    return [{"role": "system", "content": SYSTEM_ROLE}, {"role": "user", "content": user_prompt}]
