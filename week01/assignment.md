# 第 1 周：本地模型部署与提示实验

## 目标

在自己的电脑上安装 Ollama，下载并运行课程统一模型 `qwen3:4b`，再通过 Python 客户端完成一次本地推理。通过本机服务完成实验，不需要把提示词或输入内容发到第三方模型 API。

本周使用的 Ollama 模型标签为 `qwen3:4b`。Ollama 模型库当前标出的默认量化包约为 2.5 GB；这只是模型文件大小，运行时还会占用额外内存和显存。参见 [Qwen3 4B 模型条目](https://ollama.com/library/qwen3:4b)。模型标签和文件大小可能变化，提交时记录实际安装的标签。机器是否能够顺畅运行还取决于显存、系统内存、上下文长度及其他程序占用。

## 环境准备

1. 从 [Ollama 官方下载页](https://ollama.com/download) 安装适用于自己操作系统的版本，并启动 Ollama。
2. 在终端执行：

   ```bash
   ollama --version
   ollama pull qwen3:4b
   ollama run qwen3:4b
   ```

3. 在交互界面输入一条简单问题，确认有回复后输入 `/bye` 退出。
4. 建议使用 Python 3.10 或更新版本。在本目录安装客户端：

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

## 实验步骤

1. 复制 `.env.example` 为 `.env`。如果使用其他本地模型标签，可以设置 `OLLAMA_MODEL`；本周报告仍需说明是否使用了课程基线模型。
2. 运行 `python smoke_test.py`，确认 Python 能连接本机 Ollama 服务并打印非空回复。
3. 打开 `prompt_lab.py`，完成 `TODO` 提示词并运行实验。保留原始输入文本，至少尝试两种提示写法，比较输出是否完整、格式是否稳定、是否出现无依据内容。
4. 修改提示后重复运行，记录每次的模型标签、提示词、输出摘要、耗时和你做出的判断。不要只记录“效果更好”，要给出可复查的观察依据。

## 提交内容

提交一个 `report.md`，包括：

- 操作系统、Python 版本、Ollama 版本及 `ollama list` 中的模型标签；
- 连通性检查是否成功、一次推理耗时和你观察到的资源使用情况；
- 你尝试的至少两版提示词，以及各自的输出摘要；
- 对准确性、格式遵循、响应速度和局限的简短比较；
- 遇到的问题及解决步骤。

不要提交 `.env`、模型权重、访问密钥、完整私人聊天记录或整份模型内部推理文本。模型运行检查只验证本地服务可用，不以固定答案判分。

