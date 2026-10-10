"""Starter for a small, locally executed tool-calling agent."""

import os
from typing import Any

from dotenv import load_dotenv
from ollama import chat


MODEL = "qwen3:4b"
MAX_TURNS = 5

# TODO: Define one or more narrow, deterministic local tools.
# Each tool should validate its arguments before doing any work.
TOOLS: list[dict[str, Any]] = []
TOOL_FUNCTIONS: dict[str, Any] = {}


def run_agent(user_request: str) -> str:
    """Run a bounded conversation and return the model's final text."""
    load_dotenv()
    model = os.getenv("OLLAMA_MODEL", MODEL)
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a careful assistant. Use an available tool only when it is "
                "needed. Never claim a tool succeeded unless its result is provided."
            ),
        },
        {"role": "user", "content": user_request},
    ]

    # TODO: Implement a bounded model/tool loop.
    # Validate requested tool names and arguments before calling local functions.
    # Append tool results to the conversation and stop after MAX_TURNS.
    response = chat(model=model, messages=messages, tools=TOOLS)
    return response.message.content.strip()


if __name__ == "__main__":
    request = input("Request: ").strip()
    if not request:
        raise SystemExit("Please enter a request.")
    print(run_agent(request))

