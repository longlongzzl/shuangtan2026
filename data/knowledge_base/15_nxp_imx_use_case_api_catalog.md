---
title: NXP Cloud Lab i.MX 产品应用范例目录
category: NXP AIoT Cloud
source: nxp_aiot_cloud_authenticated_api
url: https://aiotcloud.nxp.com.cn/use-case-show/imx-poducts-function-experience
collected_at: 2026-06-04
---

资料来源：登录 NXP AIoT Cloud 后访问 `get_user_case` 与 `get_user_case_by_type` 接口得到的 i.MX 产品应用范例目录。该目录显示 i.MX 产品应用范例下有 38 个可见条目，覆盖 Linux 基础服务、内核调试、网络、Weston/Wayland、DRM/V4L2、i.MX93、i.MX8MP、i.MX8ULP 墨水屏和 Linux 内核驱动实验。

通用范例：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| Systemd 自启动服务应用案例 | `systemd-auto-boot-program` | systemd、Linux 服务管理、systemctl、i.MX 远程开发板 |
| Linux 驱动调试之 printk | `using-printk-for-linux-driver-debugging` | printk、dev_info、pr_debug、Linux 内核调试、驱动调试 |
| 开发板网口功能测试案例 | `network-cases` | 以太网、网卡、ethtool、网络接口测试 |
| Weston 应用案例 | `weston-use-cases` | Weston、systemctl、桌面服务启停、Kernel 启动 logo |
| Core Dump 应用案例 | `core-dump-use-case` | coredump、core 文件生成、异常分析 |
| 编译内核镜像并在云实验室开发板运行 | `Compiling Kernel Image and Running on the cloud laboratory development board` | Ubuntu 主机、交叉编译工具链、内核源码、镜像替换 |

i.MX 9 系列应用范例：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| i.MX93 Perf 应用案例 | `imx93-perf-use-cases` | i.MX93 性能测试和性能观察 |
| i.MX93 IO 应用案例 | `imx93-io-use-cases` | i.MX93 输入输出接口体验 |
| i.MX93 PXP 应用案例 | `imx93-pxp-use-cases` | PXP 图像处理相关体验 |

i.MX 8 系列应用范例：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| i.MX8MP perf 使用案例 | `perf-use-cases` | i.MX8MP 性能测试 |
| i.MX8MP 视频编解码应用案例 | `video-use-cases` | 视频编解码、多媒体处理 |
| i.MX8MP GStreamer Python 应用案例 | `imx8mp-gstreame-python` | GStreamer、Python、多媒体流水线 |
| i.MX8MP GStreamer pipeline 应用案例 | `imx8mp-gstreamer-pipeline` | GStreamer pipeline、视频流处理 |
| i.MX8MP IO 应用范例 | `io` | i.MX8MP IO 接口 |
| i.MX8MP 显示应用范例 | `display` | 显示输出、图形显示 |
| i.MX8MP 摄像头应用范例 | `camera` | 摄像头、图像采集、视频输入 |

Linux 显示 DRM 和摄像头 V4L2：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| V4L2 应用程序的编译和运行 | `V4L2 Chapter (2) Compilation and Running of V4L2 Applications` | V4L2 应用编译、i.MX camera/display unit test |
| V4L2 基本介绍和测试命令 | `Linux V4L2(1) Brief Introduction and Basic Test Command` | V4L2 多媒体架构、v4l2-ctl |
| Wayland & Weston 显示服务启动流程 | `Wayland & Weston booting logic` | Wayland、Weston、启动 log、i.MX93 EVK |
| i.MX93 视觉机器学习手势识别 | `i.MX93 ML Demo (Gesture Recognition)` | i.MX93、Ethos-U65 NPU、机器学习、手势识别 |
| DRM 显示关闭和资源释放 | `DRM user space code (4) finish display and release the resource` | DRM 用户层、资源释放、显示关闭 |
| DRM Pingpong buffer | `DRM user space code (3) Pingpong buffer` | Linux DRM、乒乓缓冲、双缓存 |
| DRM 内存申请和模式配置 | `DRM userspace code(2) memory allocation and mode set` | 内存申请、mmap、mode set、buffer 绘制 |
| DRM CRTC/encoder/connector 获取 | `DRM userspace API - get CRTC/encoder/connector` | libdrm、CRTC、encoder、connector |
| DRM 基本介绍和 modetest 测试 | `basic introduction of DRM and modetest command test` | DRM 架构、modetest 命令、显示设备枚举 |
| GCC 编译含 libdrm 的 C 程序 | `gcc compile c code with libdrm` | GCC、编译链接、libdrm |
| Linux Weston 和系统服务 | `Linux Weston and System Service` | Weston、DRM、Linux service、systemctl |
| Linux signal 机制 | `Linux signal processing mechanism` | signal 函数、多线程、Linux 信号处理 |

Linux 内核驱动应用范例：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| 实验 task struct（1） | `Experiment task struct on the cloud lab i.MX board (1)` | Linux task_struct、进程线程结构 |
| 实验 task struct（2） | `Experiment task struct on the cloud lab i.MX board (2)` | 进程状态、优先级、调度策略 |
| 实验 task struct（3） | `Experiment task struct on the cloud lab i.MX board (3)` | mm_struct、进程内存字段 |
| 实验 mutex | `Experiment with mutex on the Cloud board` | Linux 内核 mutex、同步机制 |
| 实验 spinlock | `Experiment spinlock mechanism on the Cloud board` | spinlock、自旋锁、内核同步 |
| ARM64 开发板上运行第一个字符设备驱动 | `The first character device driver runs on the Cloud ARM64 board` | 字符设备驱动、ARM64、内核驱动 |
| ARM64 开发板上运行最简单驱动程序 | `Running the simplest driver on the Cloud ARM64 board` | 简单驱动、驱动加载 |
| 云实验室开发板上运行第一个驱动程序 | `Run first linux driver on cloud i.MX board` | Linux 驱动入门、i.MX 开发板 |

i.MX8ULP 墨水屏应用：

| 主题 | url_id | 关键词与用途 |
| --- | --- | --- |
| 墨水屏控制器 EPDC 参数设置 | `EPDC parameters setting` | i.MX8ULP、EPDC、电子墨水屏、参数配置 |
| 电子墨水屏显示原理 | `logic of EPD` | EPD、反射式双稳态显示、电子墨水屏原理 |

适合回答的问题：

- NXP Cloud Lab 的 i.MX 应用范例有哪些？
- 如果要学习 Linux DRM、V4L2、Weston，应看哪些应用范例？
- i.MX93 和 i.MX8MP 在 Cloud Lab 中有哪些体验条目？
- 云实验室是否有 Linux 内核驱动、mutex、spinlock、字符设备驱动实验？
