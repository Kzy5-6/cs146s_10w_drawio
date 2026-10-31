
"""通过 stdio 连接 MCP 服务器，并比较 MCP 与直接工具调用结果。"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.tool_result import require_success
from tools import dispatch, SNAPSHOTS


def parse_mcp_result(result):
    """将 MCP 的文本内容解析为工具返回的 JSON。"""
    require_success(result)

    for block in result.content:
        if getattr(block, "type", None) == "text":
            return json.loads(block.text)

    raise RuntimeError("MCP 工具没有返回文本结果")


def comparable_data(result):
    """去掉每次调用都会变化的 snapshot_id，比较实际业务数据。"""
    if not result.get("ok"):
        return result

    data = result.get("data")
    if isinstance(data, dict):
        data = dict(data)
        data.pop("snapshot_id", None)

    return {
        "ok": result.get("ok"),
        "data": data,
        "error": result.get("error"),
    }


async def main():
    # 清空直接调用工具的快照表，避免沿用旧状态。
    SNAPSHOTS.clear()

    server = str(Path(__file__).with_name("mcp_server.py"))
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listed = await session.list_tools()
            names = {tool.name for tool in listed.tools}

            required = {"read_diagram", "inspect_diagram"}
            assert required <= names, f"缺少 MCP 工具：{required - names}"

            for name in ("read_diagram", "inspect_diagram"):
                arguments = {"name": "practice.drawio"}

                # 通过 MCP 服务器调用。
                mcp_raw = await session.call_tool(name, arguments)
                mcp_result = parse_mcp_result(mcp_raw)

                # 直接调用 Python 工具。
                direct_result = dispatch(name, arguments)

                print(f"\n========== {name} ==========")
                print("MCP 结果：")
                print(json.dumps(
                    mcp_result, ensure_ascii=False, indent=2
                ))
                print("直接调用结果：")
                print(json.dumps(
                    direct_result, ensure_ascii=False, indent=2
                ))

                # 两种调用方式应返回相同的业务数据。
                assert comparable_data(mcp_result) == comparable_data(
                    direct_result
                ), f"{name}：MCP 与直接调用结果不一致"

                print(f"[通过] {name}：MCP 与直接调用结果一致")

    print("\nMCP 对比测试全部通过。")


if __name__ == "__main__":
    asyncio.run(main())
