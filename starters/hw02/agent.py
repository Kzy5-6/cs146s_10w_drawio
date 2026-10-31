"""在 run_agent 中实现 Agent 控制循环；测试时可传入预设模型响应。"""
import os
import json
from pathlib import Path
from typing import Callable
from tools import TOOLS, dispatch, SNAPSHOTS

MAX_TURNS = 8
MAX_TOOL_CALLS = 12


def local_model(messages: list[dict], tools: list[dict]) -> dict:
    from dotenv import load_dotenv
    from ollama import Client
    load_dotenv(Path(__file__).with_name(".env"))
    client = Client(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"), timeout=300)
    return client.chat(model=os.getenv("OLLAMA_MODEL", "qwen3:4b-q4_K_M"), messages=messages, tools=tools).message.model_dump()


def _get_tool_call(call):
    """兼容字典和 Ollama 返回的工具调用对象。"""
    if isinstance(call, dict):
        function = call.get("function", {})
    else:
        function = getattr(call, "function", None)

    if isinstance(function, dict):
        name = function.get("name")
        arguments = function.get("arguments", {})
    else:
        name = getattr(function, "name", None)
        arguments = getattr(function, "arguments", {})

    return name, arguments


def run_agent(request: str, model: Callable = local_model) -> dict:
    if not isinstance(request, str) or not request.strip():
        return {
            "answer": "任务不能为空。",
            "stop_reason": "clarification",
            "events": [],
        }

    # 每次 Agent 运行使用独立的快照表。
    SNAPSHOTS.clear()

    messages = [
        {
            "role": "system",
            "content": (
                "你是 Draw.io 图表操作助手。"
                "先读取图表，再根据需要检查和修改。"
                "修改后必须调用 inspect_diagram 或 compare_changes "
                "验证结果，验证成功后才能向用户报告完成。"
                "如果无法确定要修改的页面或节点，请先向用户询问。"
                "工具调用必须使用提供的工具和参数格式。"
            ),
        },
        {"role": "user", "content": request},
    ]

    events = []
    tool_calls_count = 0
    turns = 0
    modified = False
    verified = False
    tool_failed = False
    answer = ""
    stop_reason = None

    def record(event_type, tool=None, arguments=None, result=None):
        events.append({
            "seq": len(events) + 1,
            "type": event_type,
            "tool": tool,
            "arguments": arguments,
            "result": result,
            "version": (
                result.get("data", {}).get("version")
                if isinstance(result, dict)
                and isinstance(result.get("data"), dict)
                else None
            ),
        })

    while turns < MAX_TURNS:
        turns += 1

        try:
            response = model(messages, TOOLS)
        except Exception as exc:
            answer = f"模型请求失败：{exc}"
            stop_reason = "model_error"
            record("model_error", result={"message": str(exc)})
            break

        if not isinstance(response, dict):
            answer = "模型返回格式无效。"
            stop_reason = "model_error"
            record("model_error", result={"message": "响应必须是字典"})
            break

        content = response.get("content") or ""
        calls = response.get("tool_calls") or []

        # 将 assistant 原始消息追加到上下文。
        assistant_message = {
            "role": "assistant",
            "content": content,
        }
        if calls:
            assistant_message["tool_calls"] = calls
        messages.append(assistant_message)

        record("assistant", result={
            "content": content,
            "tool_call_count": len(calls),
        })

        if not calls:
            answer = content

            if modified and not verified:
                messages.append({
                    "role": "system",
                    "content": (
                        "你已经执行过修改，但尚未成功验证。"
                        "请调用 inspect_diagram 或 compare_changes "
                        "检查修改结果，再给出最终答复。"
                    ),
                })
                continue

            if tool_failed:
                stop_reason = "tool_error"
            elif "?" in content or "？" in content:
                stop_reason = "clarification"
            else:
                stop_reason = "answered"
            break

        for call in calls:
            if tool_calls_count >= MAX_TOOL_CALLS:
                answer = "已达到工具调用次数上限，停止执行。"
                stop_reason = "limit"
                break

            tool_calls_count += 1
            name, arguments = _get_tool_call(call)

            if not isinstance(arguments, dict):
                result = {
                    "ok": False,
                    "data": None,
                    "error": {
                        "code": "invalid_arguments",
                        "message": "工具参数必须是对象",
                    },
                }
            else:
                try:
                    result = dispatch(name, arguments)
                except Exception as exc:
                    result = {
                        "ok": False,
                        "data": None,
                        "error": {
                            "code": "tool_exception",
                            "message": str(exc),
                        },
                    }

            if not result.get("ok", False):
                error = result.get("error") or {}
                error_code = error.get("code", "")

                # 这些属于可恢复的调用错误，不视为执行故障
                if error_code not in {"unknown_tool", "invalid_arguments"}:
                    tool_failed = True

            record(
                "tool",
                tool=name,
                arguments=arguments,
                result=result,
            )

            if name == "apply_changes" and result.get("ok"):
                modified = True
                verified = False

            if name == "inspect_diagram" and result.get("ok"):
                data = result.get("data") or {}
                if modified and data.get("issue_count") == 0:
                    verified = True

            if name == "compare_changes" and result.get("ok"):
                if modified:
                    verified = True

            messages.append({
                "role": "tool",
                "tool_name": str(name or "unknown"),
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                    default=str,
                ),
            })

        if stop_reason == "limit":
            break

    else:
        stop_reason = "limit"
        answer = "已达到模型请求轮数上限，停止执行。"

    if not answer:
        answer = "Agent 已停止，未生成最终答复。"

    return {
        "answer": answer,
        "stop_reason": stop_reason,
        "events": events,
    }


if __name__ == "__main__":
    import json
    request = input("请输入任务: ").strip()
    if not request:
        raise SystemExit("任务不能为空")
    print(json.dumps(run_agent(request), ensure_ascii=False, indent=2))
