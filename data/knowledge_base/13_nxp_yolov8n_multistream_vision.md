---
title: YOLOv8n 八路视频流目标检测示例
category: Edge AI
source: nxp_aiot_cloud_official
url: https://aiotcloud.nxp.com.cn/ai-solution/ai-use-case
collected_at: 2026-06-04
---

资料来源：NXP AIoT Cloud 公开的 YOLOv8n 多路流 GStreamer 示例文档。该示例展示在 FRDM i.MX 8M Plus 和 FRDM i.MX 95 平台上，使用 NXP Ara240 DNPU 加速 YOLOv8n 进行多路目标检测。

示例目标：

- 使用 GStreamer 管线处理最多 8 路并发视频流。
- 每一路视频流独立解码、预处理和推理。
- 推理结果由应用绘制到对应画面上。
- 多路画面通过 compositor 合成为统一的马赛克显示画面。
- 适合展示边缘端视频分析、目标检测、多摄像头监控和端侧视觉 AI 性能。

GStreamer 管线关键组件：

| 组件 | 作用 |
| --- | --- |
| multifilesrc | 读取每一路视频文件 |
| h264parse / v4l2h264dec | 解析和硬件解码 H.264 视频 |
| tee | 将每路视频分成推理分支和显示分支 |
| dvPre / dvInf / dvPost | 对接 DNPU 推理前处理、推理和后处理 |
| appsink | 把推理结果交给 C++ 应用 |
| cairooverlay | 绘制检测框和可视化信息 |
| imxcompositor_g2d | 合成多路画面，形成网格显示 |
| waylandsink | 全屏输出显示 |

性能摘要：

| 平台 | 适合的同步流数量 | 备注 |
| --- | --- | --- |
| FRDM i.MX 95 | 最多约 6 路可维持 30 FPS 同步表现 | 7 路和 8 路同步模式性能开始下降；sync=false 下可继续展示多路推理 |
| FRDM i.MX 8M Plus | 最多约 3 路同步表现较好 | 4 路及以上受 CPU 限制更明显，建议优先使用 sync=false |

与 NXP AI Hub 的关系：

- YOLOv8n 属于 Model Zoo / AI use case 中的视觉模型示例。
- 它不是大语言模型，但能作为边缘 AI 能力的典型资料进入客服知识库。
- 当用户询问“AI Hub 是否只有大模型”时，系统应说明 AI Hub 同时覆盖视觉检测、分类、分割、音频和生成式 AI 示例。

检索关键词：YOLOv8n，八路视频流，GStreamer，目标检测，FRDM i.MX 95，FRDM i.MX 8M Plus，Ara240 DNPU，dvPre，dvInf，dvPost，imxcompositor_g2d，waylandsink。
