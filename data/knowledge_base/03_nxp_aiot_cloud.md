---
title: NXP AIoT Cloud 与 Cloud Lab
category: NXP AIoT Cloud
source: demo_knowledge_base
---

NXP AIoT Cloud / Cloud Lab 面向开发者提供在线化的技术体验和方案学习环境，帮助用户远程了解开发板、软件工具和边缘智能解决方案。对于智能客服系统而言，NXP AIoT Cloud 相关资料可以作为领域知识库来源。系统可以整理平台介绍、用例说明、AI solution、开发板资源、边缘 AI 实践案例等内容，并通过 RAG 检索方式在用户提问时提供更加准确的回答。

在课堂 Demo 中，NXP AIoT Cloud 可以被理解为领域知识入口。智能客服并不需要把所有平台细节写死到代码里，而是把介绍资料、实验步骤、开发板说明、边缘 AI 示例和常见问题放入本地知识库。

当用户询问整体架构或实验路线时，系统先检索和 NXP AIoT Cloud 相关的资料片段，再由本地模型整理成适合网站客服的回答。这样回答会带有明确来源，方便老师查看系统是否真的使用了知识库。

后续扩展时，可以把真实官网资料、课程讲义、实验截图说明和小组报告整理为 Markdown 或 JSON 文件。只要放入 data/knowledge_base 并重建索引，前端就能展示新的检索来源。
