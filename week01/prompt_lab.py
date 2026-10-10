"""Starter for comparing prompt variations with the local course model."""

import os

from dotenv import load_dotenv
from ollama import chat


MODEL = "qwen3:4b-q4_K_M"
SYSTEM_PROMPT = """TODO: 写一个清晰的系统提示词，说明模型要完成的文本整理任务、
输出格式和不确定时应遵守的规则。不要在提示词中预先写出目标答案。"""
USER_PROMPT = """整理下面的组会记录，提取待办事项并保留负责人和时间信息：

周三组会：陈同学周五前补充实验设置；赵同学下周一检查数据备份；
王同学负责约下次会议，时间待定。"""


def main() -> None:
    load_dotenv()
    model = os.getenv("OLLAMA_MODEL", MODEL)
    response = chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )
    print(f"Model: {model}\n")
    print(response.message.content)


if __name__ == "__main__":
    main()
