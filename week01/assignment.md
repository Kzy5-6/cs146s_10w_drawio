# 第 1 周：本地模型部署与提示实验

## 目标

在自己的电脑上安装 Ollama，根据显卡可用显存下载并运行 Qwen3 4B 的推荐量化版本，再通过 Python 客户端完成一次本地推理。通过本机服务完成实验，不需要把提示词或输入内容发到第三方模型 API。

### 推荐 Ollama 模型标签

使用表中完整标签，避免 `qwen3:4b` 这种未写明量化后缀的简写。表中的“权重 + KV Cache”是运行时显存的估算下限；实际还要为推理缓冲区、图形界面和其他 GPU 程序留空间。

Ollama 当前默认上下文是 4096 tokens。按 [Qwen3 4B 模型配置](https://huggingface.co/Qwen/Qwen3-4B/blob/main/config.json)中的 36 层、8 个 KV heads、每个 head 128 维估算，若 KV Cache 使用 16-bit 数值，4K 上下文约需 576 MiB；上下文增大时，缓存需求也会增加。以下加总只包含模型包和这部分缓存，尚未计入推理缓冲区等开销：

| 显卡标称显存 | 推荐完整标签 | 量化 | 模型包大小（约） | 权重 + 4K KV Cache（约） | 总显存判断 |
|---:|---|---|---:|---:|---|
| 4 GB | `qwen3:4b-q4_K_M` | Q4_K_M | 2.6 GB | 3.2 GB | 临界；低上下文、少占用时可试，不能保证模型完全驻留 GPU |
| 6 GB | `qwen3:4b-q4_K_M` | Q4_K_M | 2.6 GB | 3.2 GB | 保守；为推理开销和其他显存使用留出余量 |
| 8 GB | `qwen3:4b-q8_0` | Q8_0 | 4.4 GB | 5.0 GB | 保守起点；若可用显存不足则退回 Q4_K_M |
| 12 GB | `qwen3:4b-fp16` | F16 | 8.1 GB | 8.7 GB | 保守起点；若 GPU 同时承担较重的显示或计算任务则退回 Q8_0 |

这里的“权重 + 4K KV Cache”不是完整的运行总量，Ollama 还需要推理缓冲区，显卡也可能被显示器和其他程序占用。因此 4 GB 档的 Q4_K_M 只是这个模型家族中较可行的低显存选择，不承诺全程 100% GPU；加载后用 `ollama ps` 查看 `PROCESSOR` 和 `CONTEXT`，并观察系统实际显存。若显示为 CPU/GPU 混合，说明发生了部分卸载，仍可完成本地实验，但速度会受影响。提高上下文长度会增加显存需求；先保持默认 4K，不要为了追求长上下文而挤掉推理所需余量。Ollama 不会因为显存较小就自动改用另一种量化。参见 Ollama 的 [Q4_K_M](https://ollama.com/library/qwen3:4b-q4_K_M)、[Q8_0](https://ollama.com/library/qwen3:4b-q8_0)、[F16](https://ollama.com/library/qwen3:4b-fp16) 模型条目，以及其关于[上下文长度](https://github.com/ollama/ollama/blob/main/docs/context-length.mdx)和[`ollama ps`](https://github.com/ollama/ollama/blob/main/docs/faq.mdx) 的说明。模型包大小或标签可能随模型库更新；报告中记录本机实际安装的完整标签和量化格式。

## 环境准备

1. 从 [Ollama 官方下载页](https://ollama.com/download) 安装适用于自己操作系统的版本，并启动 Ollama。
2. 按上表选择标签。以下用 4 GB 档的 Q4_K_M 演示；其他显存档位请把命令中的标签替换成表中对应的完整标签。

   ```bash
   ollama --version
   ollama pull qwen3:4b-q4_K_M
   ollama run qwen3:4b-q4_K_M
   ```

   运行 `ollama show qwen3:4b-q4_K_M` 可核对当前标签的量化格式；使用其他档位时同样替换成所选标签。

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

1. 复制 `.env.example` 为 `.env`。将 `OLLAMA_MODEL` 设为上表中适合自己显存的完整标签；默认值是 `qwen3:4b-q4_K_M`。Python 实验会按此变量请求 Ollama 中相同名称的模型。
2. 运行 `python smoke_test.py`，确认 Python 能连接本机 Ollama 服务并打印非空回复。
3. 打开 `prompt_lab.py`，完成 `TODO` 提示词并运行实验。保留原始输入文本，至少尝试两种提示写法，比较输出是否完整、格式是否稳定、是否出现无依据内容。
4. 修改提示后重复运行，记录每次的模型标签、提示词、输出摘要、耗时和你做出的判断。不要只记录“效果更好”，要给出可复查的观察依据。

## 提交内容

提交一个 `report.md`，包括：

- 操作系统、Python 版本、Ollama 版本及 `ollama show` 显示的模型完整标签、量化格式和包大小；
- 连通性检查是否成功、一次推理耗时和你观察到的资源使用情况；另记录运行时 `ollama ps` 中的 `PROCESSOR`、`CONTEXT`，以及系统显示的实际显存占用；
- 你尝试的至少两版提示词，以及各自的输出摘要；
- 对准确性、格式遵循、响应速度和局限的简短比较；
- 遇到的问题及解决步骤。

不要提交 `.env`、模型权重、访问密钥、完整私人聊天记录或整份模型内部推理文本。模型运行检查只验证本地服务可用，不以固定答案判分。

