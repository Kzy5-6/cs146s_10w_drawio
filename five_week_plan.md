# CS146S 五周压缩学习计划

课程按五周安排，涵盖 LLM、Coding Agent、开发工具、测试安全、应用构建与部署后运维。HW1–HW8 的任务与提交要求以各自作业文件为准。课程不设期末项目。每周的两场英文视频均为第三方补充材料，不是 Stanford 原始课堂录播。

## 第 1 周：LLM、提示与 Coding Agent

### 学习目标

- 了解 LLM 的训练、推理、能力边界和常见安全问题。
- 通过提示实验观察格式遵循、准确性与幻觉。
- 理解 Coding Agent 的循环、工具调用、MCP 和程序侧校验。

### 学习材料

- [LLM 导论](slides/Fall2025/week01-0922-intro-to-llms.pptx)、[有效提示](slides/Fall2025/week01-0926-effective-prompting.pptx)
- [构建 Coding Agent](slides/Fall2025/week02-0929-building-a-coding-agent.pptx)、[自定义 MCP Server](slides/Fall2025/week02-1003-custom-mcp-server.pptx)
- 实验代码：[提示实验](week01/prompt_lab.py)、[连通性检查](week01/smoke_test.py)、[Agent 起始代码](week02/agent.py)

### 英文 Lecture

- [Intro to Large Language Models](https://www.youtube.com/watch?v=zjkBMFhNj_g) — Andrej Karpathy
- [Building a coding agent from scratch with Zain Hasan - Together AI](https://www.youtube.com/watch?v=lxgfhPQ1GSI) — Zain Hasan / Together AI

### 作业

- HW1：[本地模型部署与提示实验](week01/assignment.md)
- HW2：[用本地模型构建最小 Coding Agent](week02/assignment.md)

## 第 2 周：AI IDE、项目上下文与 Agent 工作流

### 学习目标

- 使用 AI IDE 理解已有代码库，并编写清晰的项目上下文与需求验收条件。
- 练习 Claude Code 等 Coding Agent 的计划、执行、验证和人工复核方式。
- 理解单 Agent 与多人/多 Agent 协作的任务边界和检查点。

### 学习材料

- [AI IDE 配置](slides/Fall2025/week03-1006-ai-ide-setup.pptx)、[Silas Alberti 演讲](slides/Fall2025/week03-1010-silas-alberti.pptx)
- [Agent Manager](slides/Fall2025/week04-1013-agent-manager.pptx)、[Boris Cherny 演讲](slides/Fall2025/week04-1017-boris-cherny.pptx)
- 贯穿代码：[课程项目说明](course_project/README.md)

### 英文 Lecture

- [Cursor Crash Course & AI Coding For Beginners](https://www.youtube.com/watch?v=5zR1ZE5aqho) — Traversy Media
- [The Build System: Mission Impossible with Eno Reyes, CTO Factory AI](https://www.youtube.com/watch?v=pHGGlrKSnJ8) — Eno Reyes / The Modern Software Developer

### 作业

- HW3：[把项目上下文交给 AI IDE](week03/assignment.md)
- HW4：[设计可监督的 Agent 工作流](week04/assignment.md)

## 第 3 周：现代终端、Agent 工作流、测试与安全

### 学习目标

- 使用 CLI 将开发任务做成可复用、可检查的工作流。
- 通过自动化测试和独立审查验证 AI 生成代码。
- 识别输入校验、日志隐私、依赖和提示注入等风险，并对修复进行复核。

### 学习材料

- [AI 开发者产品](slides/Fall2025/week05-1020-ai-developer-product.pptx)、[CLI 起始代码](week05/cli_starter.py)
- [AI QA、SAST 与 DAST](slides/Fall2025/week06-1027-ai-qa-sast-dast.pptx)
- 贯穿代码：[课程项目说明](course_project/README.md)

### 英文 Lecture

- [Warp 2.0: the Agentic Development Environment](https://www.youtube.com/watch?v=0ZCMPodISoE) — Zach Lloyd；Latent Space 对谈
- [Prompt Hardening - Secure Code Generation Using AI](https://www.youtube.com/watch?v=bKphnQByVZI) — Sean Sinclair / NDC Conferences

### 作业

- HW5：[用终端工作流重复开发任务](week05/assignment.md)
- HW6：[测试与安全审查 AI 生成代码](week06/assignment.md)

安全视频聚焦提示与代码生成，不覆盖全部自动化测试、SAST/DAST 和作业要求；按 HW6 说明完成并提交。

## 第 4 周：AI Code Review、自动化 UI 与全栈应用

### 学习目标

- 以需求、差异和可复现证据核验 Agent 的 Code Review 意见。
- 从 PRD 和验收条件出发，构建连通 UI、API 与数据流的应用。
- 使用安全 DOM 操作，并检查加载、成功、空状态和错误状态。

### 学习材料

- [AI Code Review](slides/Fall2025/week07-1103-ai-code-review.pptx)、[Tomas Reimers 演讲](slides/Fall2025/week07-1107-tomas-reimers-slides.pdf)
- [端到端应用](slides/Fall2025/week08-1110-end-to-end-app.pptx)
- 贯穿代码：[课程项目说明](course_project/README.md)、[前端页面](course_project/frontend/index.html)、[前端代码](course_project/frontend/app.js)

### 英文 Lecture

- [Reading Code - Marit van Dijk - NDC London 2025](https://www.youtube.com/watch?v=8xKQ2cX-h5E) — Marit van Dijk / NDC Conferences
- [Build Web Apps with AI—No Coding Required! Full Lovable Tutorial](https://www.youtube.com/watch?v=c0zhLzcVJRI) — Lovable

### 作业

- HW7：[进行有证据的 Agentic Code Review](week07/assignment.md)
- HW8（开始）：[从需求构建端到端应用](week08/assignment.md)。按作业要求继续实现和记录；第 5 周完成并统一验收。

课件及英文视频不能替代 HW7/HW8 中的 AI PR Review、界面状态、代码和验收要求。

## 第 5 周：部署后 Agent、可观测性、故障响应与软件工程未来

### 学习目标

- 理解 Agent 在部署后排障、日志观测和故障响应中的用法与边界。
- 将需求、实现、Review、测试和运行反馈连成可追溯的软件交付流程。
- 完成 HW8 的代码、运行说明和验证材料，并进行统一验收。

### 学习材料

- [事件响应与 DevOps](slides/Fall2025/week09-1117-incident-response-devops.pptx)、[Resolve 演讲课件](slides/Fall2025/week09-1121-resolve-guest-lecture-slides.pdf)
- 贯穿代码：[课程项目说明](course_project/README.md)、[API 入口](course_project/app/main.py)

### 英文 Lecture

- [AWS re:Invent 2025 - Ditch your old SRE playbook: AI SRE for root cause in minutes](https://www.youtube.com/watch?v=YrdtOwMzJCU) — Spiros Xanthos / AWS re:Invent
- [The Modern Software Engineer](https://www.youtube.com/watch?v=jOe4fJSc2IE) — Mihail Eric；Demetrios Brinkmann 主持 / AAIF Live

### 作业与验收

- 完成 HW8（[作业要求](week08/assignment.md)），不增加新的编程作业或期末项目。
- 统一检查 HW1–HW8 各自作业文件中列出的提交物、运行说明和验证记录。
- 验收 HW8 的需求与界面、API 连通、主要状态、错误处理、可运行代码及走查记录。
- 部署观测与课程回顾材料仅用于学习和讨论，不产生额外作业，也不要求提交新项目。

## 资源核验说明

视频链接的标题和发布频道已按 YouTube 条目信息核对并在计划中采用。若来源页面未将讲者与频道分开标注，计划注明频道或主持信息；个别标题和讲者写法已据视频页面校正。视频主题与课件内容并非完全重合，作业要求和覆盖范围以仓库内的课件、代码和 HW1–HW8 说明为准。
