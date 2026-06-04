---
title: NXP Cloud Lab 系统方案目录
category: NXP AIoT Cloud
source: nxp_aiot_cloud_authenticated_api
url: https://aiotcloud.nxp.com.cn/solution
collected_at: 2026-06-04
---

资料来源：登录 NXP AIoT Cloud 后访问 `get_user_case` 与 `get_user_case_by_type` 接口得到的系统方案目录。接口返回 4 个可见方案：EdgeLock 2GO 解决方案、基于 i.MX RT700 的智能手势识别平台、实时边缘 EtherCAT 解决方案、EasyEVSE 开发平台。

系统方案目录：

| 方案 | url_id | 关键能力 | 适合回答的问题 |
| --- | --- | --- | --- |
| EdgeLock 2GO 解决方案 | `EdgeLock2Go Solution` | EdgeLock 2GO 是 NXP 用于 IoT 设备配置和管理的服务平台，用于把密钥和证书安全安装到设备中。Cloud Lab 方案结合 EdgeLock 2GO 平台和专用 i.MX 硬件，演示安全配置能力。 | EdgeLock 2GO 是什么；它和 IoT 设备证书、密钥、OTA、CRA 合规有什么关系；Cloud Lab 如何演示安全配置 |
| 基于 i.MX RT700 的智能手势识别平台 | `intelligent-gesture-recognition-on-rt700-platform` | 在单片 MCU 上演示多个 AI 模型，借助 NPU 加速完成手部定位、关键点检测和手势识别；通过内存时间共享机制应对内存限制；Cloud Lab 提供交互界面、视频流输入和实时监控。 | RT700 如何做手势识别；MCU 上如何运行多模型视觉链路；Cloud Lab 如何远程体验视觉 AI |
| 实时边缘 EtherCAT 解决方案 | `realtime-edge-ethercat-solution` | 使用 Real-time Edge 架构构建多轴伺服同步控制系统；通过 EtherCAT 将多达 60 个电机进行实时同步控制；方案使用 i.MX93 作为 EtherCAT 主站，结合 30 个 i.MXRT1180 EtherCAT 从站控制 60 个轴。 | NXP 的实时边缘方案如何做多轴控制；EtherCAT 主从站如何配合；i.MX93 和 i.MXRT1180 在方案中分别做什么 |
| EasyEVSE 开发平台 | `easyevse-development-platform` | 提供软件、电路板、连接线、设计文件和文档，用于模拟充电站与电动汽车之间的充电控制会话；支持安全无线云连接、精确能源计费、安全控制、NFC 认证和基于 HomePlug Green PHY 的 ISO15118 电力线通信；Cloud Lab 提供实时监控、EVSE/EV 调试控制台和 GUI 映射。 | EasyEVSE 是什么；如何远程体验充电站解决方案；EVSE/EV 调试、NFC 认证、ISO15118 和能源计费如何出现在方案中 |

和本项目 RAG 客服的关系：

- 这些系统方案适合回答“行业场景如何落地到 NXP 硬件和 Cloud Lab 体验”的问题。
- 与 AI Hub 模型页面不同，系统方案更强调业务场景、硬件组合、控制链路和远程交互体验。
- RAG 检索时，如果用户问安全配置、EVSE 充电、EtherCAT 控制或 RT700 手势识别，应优先命中本目录。

检索关键词：EdgeLock 2GO，IoT 证书，密钥配置，OTA，CRA，i.MX RT700，智能手势识别，NPU，EtherCAT，i.MX93，i.MXRT1180，EasyEVSE，ISO15118，HomePlug Green PHY，NFC 认证，EVSE。
