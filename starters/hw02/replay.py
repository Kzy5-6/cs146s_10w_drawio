"""按顺序返回预设模型消息；消息用尽时抛出 replay_exhausted。"""
import argparse
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import agent as agent_module
import tools as tools_module
from agent import run_agent

class ReplayModel:
    """按顺序返回预设模型消息。"""

    def __init__(self, messages):
        self.messages = iter(messages)
        self.calls = 0

    def __call__(self, messages, tools):
        self.calls += 1

        try:
            response = next(self.messages)
        except StopIteration as exc:
            raise RuntimeError("replay_exhausted") from exc

        if "raise" in response:
            raise ConnectionError(response["raise"])

        return response


def run_case(case):
    """运行单个 JSON 案例。"""
    model = ReplayModel(case["messages"])
    result = run_agent(case["request"], model=model)

    return {
        "result": result,
        "model_calls": model.calls,
    }

def make_call(name, arguments):
    """构造 ReplayModel 使用的工具调用。"""
    return {
        "function": {
            "name": name,
            "arguments": arguments,
        }
    }


def make_message(*calls):
    return {
        "content": "",
        "tool_calls": list(calls),
    }


def prepare_test_workspace(temp_dir):
    """
    从当前练习图复制一份测试图到临时工作区。
    返回临时工作区、文件名和一个真实节点。
    """
    source = tools_module.WORKSPACE / "practice.drawio"

    if not source.is_file():
        raise FileNotFoundError(
            f"测试需要现有练习图：{source}"
        )

    workspace = Path(temp_dir)
    name = "injection-test.drawio"
    target = workspace / name

    shutil.copy2(source, target)

    snapshot = tools_module.read_diagram(workspace, name)

    page = snapshot["pages"][0]
    node = next(
        (
            cell for cell in page["cells"]
            if cell.get("vertex") == "1"
        ),
        None,
    )

    if node is None:
        raise AssertionError("测试图中没有可改名的节点")

    return workspace, name, page["id"], node["id"]


def run_injection_tests():
    """测试工具异常、重复写入和版本冲突。"""

    passed = 0

    # --------------------------------------------------
    # 1. 工具异常：dispatch 抛出异常时 Agent 应保留轨迹
    # --------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="hw2-exception-") as temp:
        workspace, name, _, _ = prepare_test_workspace(temp)
        original_bytes = (workspace / name).read_bytes()

        with patch.object(tools_module, "WORKSPACE", workspace):
            case = {
                "request": "读取测试图",
                "messages": [
                    make_message(
                        make_call("read_diagram", {"name": name})
                    ),
                    {
                        "content": "工具异常测试结束。",
                        "tool_calls": [],
                    },
                ],
            }

            model = ReplayModel(case["messages"])

            with patch.object(
                agent_module,
                "dispatch",
                side_effect=RuntimeError("injected tool exception"),
            ):
                result = run_agent(case["request"], model=model)

            tool_events = [
                event for event in result["events"]
                if event.get("type") == "tool"
            ]

            assert model.calls == 2, (
                f"工具异常：模型调用次数错误：{model.calls}"
            )
            assert result["stop_reason"] == "tool_error"
            assert len(tool_events) == 1
            assert tool_events[0]["result"]["ok"] is False
            assert (
                tool_events[0]["result"]["error"]["code"]
                == "tool_exception"
            )
            assert (workspace / name).read_bytes() == original_bytes

            print("[通过] tool_exception")
            print(json.dumps(tool_events, ensure_ascii=False, indent=2))
            passed += 1

    # --------------------------------------------------
    # 2. 重复写入：同一批次对同一节点执行相同改名
    # --------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="hw2-duplicate-") as temp:
        workspace, name, page_id, cell_id = prepare_test_workspace(temp)

        with patch.object(tools_module, "WORKSPACE", workspace):
            before = tools_module.read_diagram(workspace, name)
            old_label = next(
                cell["value"]
                for cell in before["pages"][0]["cells"]
                if cell["id"] == cell_id
            )

            operation = {
                "op": "rename_node",
                "page_id": page_id,
                "cell_id": cell_id,
                "label": "重复写入测试",
            }

            case = {
                "request": "重复执行相同改名并检查结果",
                "messages": [
                    make_message(
                        make_call(
                            "apply_changes",
                            {
                                "name": name,
                                "expected_version": before["version"],
                                "operations": [
                                    operation,
                                    operation.copy(),
                                ],
                            },
                        )
                    ),
                    make_message(
                        make_call(
                            "inspect_diagram",
                            {"name": name},
                        )
                    ),
                    {
                        "content": "重复写入测试完成。",
                        "tool_calls": [],
                    },
                ],
            }

            output = run_case(case)
            result = output["result"]

            tool_events = [
                event for event in result["events"]
                if event.get("type") == "tool"
            ]

            after = tools_module.read_diagram(workspace, name)
            final_node = next(
                cell for cell in after["pages"][0]["cells"]
                if cell["id"] == cell_id
            )

            assert output["model_calls"] == 3
            assert result["stop_reason"] == "answered"
            assert len(tool_events) == 2
            assert all(event["result"]["ok"] for event in tool_events)
            assert tool_events[0]["result"]["data"]["operation_count"] == 2
            assert final_node["value"] == "重复写入测试"
            assert after["version"] != before["version"]

            print("[通过] duplicate_write")
            print(
                f"节点名称：{old_label!r} -> "
                f"{final_node['value']!r}"
            )
            passed += 1

    # --------------------------------------------------
    # 3. 版本冲突：用旧版本提交写入，不能覆盖新文件
    # --------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="hw2-conflict-") as temp:
        workspace, name, page_id, cell_id = prepare_test_workspace(temp)

        with patch.object(tools_module, "WORKSPACE", workspace):
            old_snapshot = tools_module.read_diagram(workspace, name)
            stale_version = old_snapshot["version"]

            # 先直接完成一次合法写入，制造新版本。
            first_write = tools_module.apply_tool(
                name,
                stale_version,
                [{
                    "op": "rename_node",
                    "page_id": page_id,
                    "cell_id": cell_id,
                    "label": "版本 B",
                }],
            )

            assert first_write["ok"] is True

            version_b = first_write["data"]["version"]
            bytes_b = (workspace / name).read_bytes()

            # Agent 故意使用过期的版本 A。
            case = {
                "request": "使用旧版本修改图表",
                "messages": [
                    make_message(
                        make_call(
                            "apply_changes",
                            {
                                "name": name,
                                "expected_version": stale_version,
                                "operations": [{
                                    "op": "rename_node",
                                    "page_id": page_id,
                                    "cell_id": cell_id,
                                    "label": "不应写入",
                                }],
                            },
                        )
                    ),
                    {
                        "content": "版本冲突测试结束。",
                        "tool_calls": [],
                    },
                ],
            }

            output = run_case(case)
            result = output["result"]

            tool_events = [
                event for event in result["events"]
                if event.get("type") == "tool"
            ]

            after_bytes = (workspace / name).read_bytes()
            after = tools_module.read_diagram(workspace, name)

            assert output["model_calls"] == 2
            assert result["stop_reason"] == "tool_error"
            assert len(tool_events) == 1
            assert tool_events[0]["result"]["ok"] is False
            assert (
                tool_events[0]["result"]["error"]["code"]
                == "version_conflict"
            )
            assert after_bytes == bytes_b
            assert after["version"] == version_b

            final_node = next(
                cell for cell in after["pages"][0]["cells"]
                if cell["id"] == cell_id
            )
            assert final_node["value"] == "版本 B"

            print("[通过] version_conflict")
            print(json.dumps(tool_events, ensure_ascii=False, indent=2))
            passed += 1

    print(f"\n注入测试完成：{passed}/3 项全部通过。")

def self_test():
    """测试 Agent 的基本控制流程和限制。"""

    cases = {
        "normal_answer": {
            "request": "回答测试",
            "messages": [
                {"content": "模拟回答成功", "tool_calls": []}
            ],
        },
        "unknown_tool": {
            "request": "测试未知工具",
            "messages": [
                {
                    "content": "",
                    "tool_calls": [{
                        "function": {
                            "name": "unknown_tool",
                            "arguments": {},
                        }
                    }],
                },
                {"content": "未知工具测试结束", "tool_calls": []},
            ],
        },
        "invalid_arguments": {
            "request": "测试无效参数",
            "messages": [
                {
                    "content": "",
                    "tool_calls": [{
                        "function": {
                            "name": "read_diagram",
                            "arguments": {},
                        }
                    }],
                },
                {"content": "无效参数测试结束", "tool_calls": []},
            ],
        },
        "service_error": {
            "request": "测试服务不可用",
            "messages": [
                {"raise": "模拟模型服务不可用"}
            ],
        },
        "loop_limit": {
            "request": "测试循环上限",
            "messages": [
                {
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "unknown_tool",
                                "arguments": {},
                            }
                        }
                    ],
                }
                for _ in range(10)
            ],
        },
        "multiple_tools": {
            "request": "同一轮执行读取和检查",
            "messages": [
                {
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "read_diagram",
                                "arguments": {"name": "practice.drawio"},
                            }
                        },
                        {
                            "function": {
                                "name": "inspect_diagram",
                                "arguments": {"name": "practice.drawio"},
                            }
                        },
                    ],
                },
                {
                    "content": "读取和检查均已完成。",
                    "tool_calls": [],
                },
            ],
        },
        "tool_call_limit": {
            "request": "测试第13次工具调用是否被拒绝",
            "messages": [
                {
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "unknown_tool",
                                "arguments": {},
                            }
                        }
                        for _ in range(13)
                    ],
                }
            ],
        },
    }

    expected = {
        "normal_answer": ("answered", 1),
        "unknown_tool": ("answered", 2),
        "invalid_arguments": ("answered", 2),
        "service_error": ("model_error", 1),
        "loop_limit": ("limit", 8),
        "multiple_tools": ("answered", 2),
        "tool_call_limit": ("limit", 1),
    }

    passed = 0

    for name, case in cases.items():
        output = run_case(case)
        result = output["result"]
        actual = (result["stop_reason"], output["model_calls"])

        assert actual == expected[name], (
            f"{name}: 预期 {expected[name]}，实际 {actual}"
        )

        tool_events = [
            event for event in result["events"]
            if event.get("type") == "tool"
        ]

        if name == "multiple_tools":
            assert len(tool_events) == 2
            assert all(event["result"].get("ok") for event in tool_events)

        if name == "tool_call_limit":
            assert len(tool_events) == 12

        passed += 1
        print(f"[通过] {name}")
    print(f"\n基础测试完成：{passed}/{len(cases)} 项全部通过。")
    run_injection_tests()

def main():
    parser = argparse.ArgumentParser(
        description="使用预设模型消息测试 Agent 控制流程。"
    )
    parser.add_argument(
        "scenario",
        nargs="?",
        type=Path,
        help="包含 request 和 messages 的 JSON 案例文件",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行内置控制流程测试",
    )
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.scenario is None:
        parser.error("请提供案例 JSON 文件，或使用 --self-test")

    case = json.loads(args.scenario.read_text(encoding="utf-8"))
    print(json.dumps(
        run_case(case),
        ensure_ascii=False,
        indent=2,
        default=str,
    ))


if __name__ == "__main__":
    main()