# NXP AIoT Cloud 官方资料采集报告

采集时间：2026-06-04
目标：从 NXP AIoT Cloud 官网整理结构化或半结构化资料，用于本地 RAG 知识库检索。

## 已使用来源

| 来源 | URL | 采集结果 |
| --- | --- | --- |
| 官网首页 | https://aiotcloud.nxp.com.cn/ | 确认 Cloud Lab 定位、导航结构和公开资源入口 |
| robots.txt | https://aiotcloud.nxp.com.cn/robots.txt | 未禁止抓取，提供 sitemap 地址 |
| 站点地图 | https://aiotcloud.nxp.com.cn/sitemap.xml | 获取产品、软件、方案、应用范例、详情页、文章等 URL 清单 |
| AI Hub | https://aiotcloud.nxp.com.cn/ai-solution | 获取 AI Hub、Model Zoo、DNPU AI 方案、模型转换工具等公开内容 |
| 软件页面 | https://aiotcloud.nxp.com.cn/software | 获取 DDR 工具和 Voice Plugins 工具摘要 |
| LLM Edge Studio 文档 | https://aiotcloud.nxp.com.cn/aisolutions/llm/docs/README_ch.md | 获取平台、架构、支持模型和性能指标 |
| VLM Edge Studio 文档 | https://aiotcloud.nxp.com.cn/aisolutions/vlm/docs/README_ch.md | 获取平台、架构、Qwen2.5-VL-7B 支持情况和性能指标 |
| Qwen 视频分析文档 | https://aiotcloud.nxp.com.cn/aisolutions/qwen/docs/README_ch.md | 获取 Ara-2 NPU、Qwen2.5-VL-7B、视频/摄像头模式和性能信息 |
| VSS 文档 | https://aiotcloud.nxp.com.cn/aisolutions/vss/docs/README_ch.md | 获取 VSS、视频描述 RAG、Llama3.2-3B、Qwen2.5-VL-7B 和 YOLOv8n 方案信息 |
| YOLOv8n 文档 | https://aiotcloud.nxp.com.cn/aisolutions/yolov8n/docs/README_ch.md | 获取八路视频流目标检测、GStreamer 管线和平台性能信息 |

## 已入库文档

| 本地文件 | 主题 |
| --- | --- |
| `data/knowledge_base/08_nxp_cloud_lab_official_overview.md` | Cloud Lab 官网总览、导航和资料入口 |
| `data/knowledge_base/09_nxp_ai_hub_model_zoo.md` | AI Hub、Model Zoo、模型类别和平台 |
| `data/knowledge_base/10_nxp_model_conversion_deployment_tools.md` | 模型格式、目标平台、量化、转换、部署和 benchmark |
| `data/knowledge_base/11_nxp_llm_vlm_edge_studio_official.md` | LLM/VLM Edge Studio 架构、平台和模型 |
| `data/knowledge_base/12_nxp_qwen_vss_video_ai.md` | Qwen2.5-VL-7B 视频分析、VSS、RAG 视频检索 |
| `data/knowledge_base/13_nxp_yolov8n_multistream_vision.md` | YOLOv8n 八路视频流目标检测 |
| `data/knowledge_base/14_nxp_cloud_lab_software_and_routes.md` | DDR、Voice Plugins、应用范例、系统方案和资料边界 |
| `data/knowledge_base/15_nxp_imx_use_case_api_catalog.md` | 登录态接口返回的 38 个 i.MX 产品应用范例 |
| `data/knowledge_base/16_nxp_mcu_partner_use_case_api_catalog.md` | 登录态接口返回的 MCU 与合作伙伴应用范例 |
| `data/knowledge_base/17_nxp_solution_api_catalog.md` | 登录态接口返回的 4 个系统方案 |

## 访问边界

官网的部分动态列表接口需要 NXP 登录态。未登录访问 `https://api.aiotcloud.nxp.com.cn/get_user_case` 时返回登录页。登录后，本轮补充抓取了 `应用范例` 与 `解决方案` 两类接口数据，并将目录、标题、关键词、分类和摘要整理为本地半结构化 Markdown。

接口返回的正文包含较长 HTML 内容。本项目没有把登录态正文整段搬入仓库，而是抽取目录和摘要用于 RAG 检索，避免知识库变成不可读的 HTML 转储。

## 对项目的意义

这些资料已按 RAG 检索友好的方式整理为 Markdown：包含标题、类别、来源、来源 URL、采集日期、主题表格、关键词和适合回答的问题。重建索引后，客服系统可以先检索这些本地资料，再由本地 LLM 生成回答。
