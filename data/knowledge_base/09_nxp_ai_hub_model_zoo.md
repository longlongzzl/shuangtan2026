---
title: NXP AI Hub 与 Model Zoo 官方资料
category: NXP AI Hub
source: nxp_aiot_cloud_official
url: https://aiotcloud.nxp.com.cn/ai-solution
collected_at: 2026-06-04
---

资料来源：NXP AIoT Cloud 官网 AI Hub 页面和公开前端静态资源。AI Hub 面向边缘计算场景，围绕模型集成、模型体验、模型部署和设备连接提供入口。页面将能力组织为三块：NXP Model Zoo、NXP i.MX + DNPU Ara-2 AI 方案、模型转换与部署工具。

核心定位：

- AI Hub 用于把 AI 模型与 NXP 边缘硬件连接起来，帮助开发者从模型选择走到设备部署。
- Model Zoo 提供经过优化的边缘 AI 模型集合，支持在 NXP i.MX 平台上体验和部署。
- AI 方案区聚焦视觉 AI 与生成式 AI，特别是基于 NXP i.MX 与 DNPU Ara-2 的端侧运行能力。
- 模型转换工具面向已训练模型，支持格式转换、量化、编译、部署和性能评估。

Model Zoo 公开页面中出现的模型类型：

| 类别 | 模型示例 | 典型用途 |
| --- | --- | --- |
| 目标检测 | YOLOv8、YOLOv4-tiny、UltraFace-slim、FaceDet、SSDLite MobileNetV2、CenterNet、NanoDet | 摄像头检测、人脸检测、多目标识别 |
| 图像分类 | EfficientNet-lite、MobileNet V1/V2、Deepface-emotion、Tiny ResNet、Visual Wake Word、MNasNet、ResNet | 图片分类、情绪识别、唤醒检测 |
| 深度估计 | MiDaS | 单目深度估计、视觉感知 |
| 语义分割 | DeepLabV3、Selfie Segmenter General、YOLACT-Edge | 前景分割、语义分割、实例分割 |
| 低照度增强 | SCI | 暗光图像增强 |
| 姿态与头部方向 | MoveNet、WHENet | 人体姿态、头部姿态估计 |
| 超分辨率 | Fast-SRGAN | 图像增强、分辨率提升 |
| 音频模型 | Deep AutoEncoder、Microspeech LSTM、DS CNN、Wav2Letter | 音频降噪、关键词识别、语音识别 |

公开页面中出现的硬件平台包括 i.MX93、i.MX8MP、i.MX95、i.MX8QuadXPlus 等。不同模型和工具的可用平台不完全相同，实际运行应以对应模型页面、开发板页面或实验预约页面为准。

与本项目 RAG 客服的关系：

- 当用户询问 NXP AI Hub 能做什么，系统应回答“模型选择、模型转换、模型部署、端侧 AI 方案体验”这些具体能力。
- 当用户询问有哪些模型，系统可按目标检测、分类、分割、音频、生成式 AI 等类别回答。
- 当用户询问本项目是否是 RAG 知识库，系统应说明：本项目把官网资料整理到本地 Markdown 文档，构建向量索引，问答时先检索资料再调用本地 LLM 生成回答。

检索关键词：NXP AI Hub，NXP Model Zoo，i.MX，i.MX93，i.MX8MP，i.MX95，DNPU，Ara-2，边缘 AI，模型部署，模型转换。
