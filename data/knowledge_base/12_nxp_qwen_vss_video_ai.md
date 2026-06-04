---
title: Qwen2.5-VL-7B 视频分析与 VSS 视频检索方案
category: Edge AI
source: nxp_aiot_cloud_official
url: https://aiotcloud.nxp.com.cn/ai-solution/ai-use-case
collected_at: 2026-06-04
---

资料来源：NXP AIoT Cloud 公开的 Qwen2.5-VL-7B 视频分析文档和 VSS（Video Search Summarization）文档。两者都属于边缘端多模态生成式 AI 示例，重点展示视频理解、视觉语言模型、RAG 检索和端侧推理。

Qwen2.5-VL-7B 视频分析：

- 目标：展示 Ara-2 NPU 在边缘侧加速多模态生成式 AI 的能力。
- 支持 SoC：i.MX 95、i.MX 8M Plus。
- 外接加速：Ara-2 NPU 通过 M.2 接口以 PCIe 方式连接开发板，配备独立 16 GB LPDDR4 内存用于 AI 模型。
- UI：Qt6 Quick / QML 图形界面。
- 视频处理：GStreamer 用于摄像头模式和视频模式；图像缩放、色彩空间转换可借助 2D-GPU。
- 模型组件：Qwen2.5-VL-7B 结合视觉编码器和语言模型，流程包括图像/文本输入处理、视觉特征提取、特征融合、语言模型生成、文本输出。
- 应用模式：视频文件模式和摄像头录制模式。摄像头模式会录制短视频，再把视频内容与用户问题送入模型。

Qwen 示例中的性能信息：

| 项目 | 官方文档中的数据 |
| --- | --- |
| 视觉编码器 | 约 4.5 秒 |
| Qwen2.5-VL-7B token 生成 | 约 6.1 tokens/s |
| 新视频 TTFT | 约 9.3 秒或按场景约 14.5 秒 |
| 缓存视频追问 TTFT | 约 1 秒 |
| FFmpeg + TorchCodec 端到端首 Token 前总延迟 | 约 32.3 秒 |

VSS 视频检索方案：

- 运行平台：FRDM i.MX 95 PRO。
- 目标：面向长期视频监控，把视频片段转换为可检索的语义描述，并支持用户用自然语言查询相关片段。
- VLM：Qwen2.5-VL-7B 处理 8 秒视频片段，每段采样 16 帧，生成自然语言描述。
- RAG：存储并检索视频描述，使用户查询能定位相关视频片段。
- LLM：Llama-3.2-3B-Instruct 用于理解用户提示词并结合 RAG 结果交互回答。
- 并行视觉流水线：Yolov8n-640 在 i.MX95 Neutron NPU 上实时运行，用于目标检测。

VSS 性能信息：

| 组件 | 输出 Token 速率 | 首 Token 时间 |
| --- | --- | --- |
| Llama3.2-3B | 14 tokens/s | 0.7 秒 |
| Qwen2.5-VL-7B | 5.15 tokens/s | 10.5 秒或 2.4 秒 |

和本项目 RAG 客服的关系：

- VSS 是 NXP 官方示例里明确出现 RAG 的视频检索方案：先把视频描述结构化存储，再根据用户问题检索相关片段。
- 本项目采用同一类思想，但对象从“视频片段描述”换成“官网技术资料文档片段”。
- 本项目的回答应先检索本地文档库，再由本地 LLM 组织答案；不能只靠模型记忆回答。

检索关键词：Qwen2.5-VL-7B，VSS，Video Search Summarization，视频检索，RAG，Llama3.2-3B，Ara-2 NPU，FRDM i.MX 95 PRO，GStreamer，Qt6，视觉语言模型。
