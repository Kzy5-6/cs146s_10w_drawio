"""Check that the local Ollama service can answer a simple prompt."""

import os
import time

from dotenv import load_dotenv
from ollama import chat


def main() -> None:
    load_dotenv()
    model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    started = time.perf_counter()
    try:
        response = chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "请用一句话介绍你能帮助完成的编程学习任务。",
                }
            ],
        )
    except Exception as exc:
        raise SystemExit(
            "无法连接本机 Ollama。请确认 Ollama 已启动、模型已下载，"
            "并检查 OLLAMA_MODEL 设置。\n"
            f"原始错误：{exc}"
        ) from exc

    elapsed = time.perf_counter() - started
    content = response.message.content.strip()
    if not content:
        raise SystemExit("模型返回了空内容；请检查 Ollama 服务和模型状态。")

    print(f"Model: {model}")
    print(f"Elapsed seconds: {elapsed:.2f}")
    print("Response:")
    print(content)


if __name__ == "__main__":
    main()
