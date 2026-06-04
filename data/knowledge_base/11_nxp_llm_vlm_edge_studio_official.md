---
title: LLM Edge Studio 与 VLM Edge Studio 官方资料
category: Edge AI
source: nxp_aiot_cloud_official
url: https://aiotcloud.nxp.com.cn/ai-solution/ai-use-case
collected_at: 2026-06-04
---

资料来源：NXP AIoT Cloud 公开的 LLM Edge Studio 和 VLM Edge Studio Markdown 文档。两者都是面向边缘设备的交互式启动器应用，用于在 NXP 平台上加载模型、选择模型、输入提示词并运行本地推理。

共同架构：

- 运行平台：FRDM i.MX 8M Plus、FRDM i.MX 95。
- 加速硬件：Ara240 DNPU。
- 中间层：eIQ AAF Connector 提供 HTTP/REST 访问，Ara240 Runtime SDK 负责与加速器运行时通信。
- 应用层：图形界面负责模型选择、提示词输入、结果展示。
- 通信路径：应用通过 Connector 访问服务端，服务端把 prompt 和模型请求交给 Optimum Ara / Runtime SDK，再由 DNPU 执行模型。
- 限制：单个程序实例一次只选择并运行一个模型，不在不同端点上同时运行多个模型。

LLM Edge Studio：

| 支持模型 | 参数量 | 首 Token 时间 | 平均 Token 速率 | 模型用途 |
| --- | --- | --- | --- | --- |
| Qwen2.5-coder-1.5B | 约 1.54B | 0.26 - 9.51 秒 | 14.92 tokens/s | 轻量代码/文本生成 |
| Qwen2.5-7B-Instruct | 约 7.61B | 1.85 - 16.73 秒 | 5.99 tokens/s | 通用指令问答 |

VLM Edge Studio：

| 支持模型 | 参数量 | 首 Token 时间 | 平均 Token 速率 | 模型用途 |
| --- | --- | --- | --- | --- |
| Qwen2.5-VL-7B | 7B | 1 - 14.26 秒 | 6.255 tokens/s | 图像/视频与文本联合理解 |

适合回答的问题：

- LLM Edge Studio 是什么？
- VLM Edge Studio 和 LLM Edge Studio 有什么区别？
- NXP 的边缘大模型示例支持哪些平台？
- Ara240 DNPU、eIQ AAF Connector、Runtime SDK 在架构中分别做什么？
- 本地模型推理为什么要关注 TTFT 和 token 速率？

检索关键词：LLM Edge Studio，VLM Edge Studio，Ara240，DNPU，eIQ AAF Connector，Optimum Ara，FRDM i.MX 95，FRDM i.MX 8M Plus，Qwen2.5，Qwen2.5-VL-7B，TTFT。
