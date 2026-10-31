"""实现 HW2 的四种工具；文件解析与写入可调用 shared 中的适配器。"""
import sys
from pathlib import Path
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.diagram_io import apply_operations, read_diagram


WORKSPACE = Path(__file__).resolve().parents[2] / ".runtime/hw02/workspace"

# 每次运行独立保存快照
SNAPSHOTS: dict[str, dict] = {}


def success(data):
    return {"ok": True, "data": data, "error": None}


def failure(code, message):
    return {"ok": False, "data": None, "error": {
        "code": code, "message": str(message)
    }}


def save_snapshot(snapshot):
    snapshot_id = uuid.uuid4().hex[:8]
    SNAPSHOTS[snapshot_id] = snapshot
    return snapshot_id


def valid_name(name):
    if not isinstance(name, str) or not name.endswith(".drawio"):
        raise ValueError("name 必须是 .drawio 文件名")
    if Path(name).name != name:
        raise ValueError("name 不能包含目录")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_diagram",
            "description": "读取工作区中的 Draw.io 图表，返回页面、图元摘要、文件版本和快照标识。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_diagram",
            "description": "检查图表各页面中的空节点名称和连接端点错误。",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_changes",
            "description": (
                "修改 Draw.io 图表。operations 中每项必须严格使用以下字段："
                "rename_node: {op:'rename_node', page_id, cell_id, label}；"
                "add_edge: {op:'add_edge', page_id, cell_id, source, target}；"
                "set_endpoints: {op:'set_endpoints', page_id, cell_id, source, target}。"
                "禁止使用 node_id、new_value 等其他字段。必须先读取图表并使用最新 version。"
),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "expected_version": {"type": "string"},
                    "operations": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 20,
                        "items": {
                            "type": "object",
                            "properties": {
                                "op": {
                                    "type": "string",
                                    "enum": ["rename_node", "add_edge", "set_endpoints"]
                                },
                                "page_id": {"type": "string"},
                                "cell_id": {"type": "string"},
                                "label": {"type": "string"},
                                "source": {"type": "string"},
                                "target": {"type": "string"}
                            },
                            "required": ["op", "page_id", "cell_id"],
                            "additionalProperties": False
                        }
                    },

                },
                "required": ["name", "expected_version", "operations"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_changes",
            "description": "比较两次读取或修改产生的快照，查看页面和图元的变化。",
            "parameters": {
                "type": "object",
                "properties": {
                    "before": {"type": "string"},
                    "after": {"type": "string"},
                },
                "required": ["before", "after"],
            },
        },
    },
]


def read_tool(name: str) -> dict:
    try:
        valid_name(name)
        snapshot = read_diagram(WORKSPACE, name)
        snapshot_id = save_snapshot(snapshot)
        return success({
            "snapshot_id": snapshot_id,
            "version": snapshot["version"],
            "pages": snapshot["pages"],
        })
    except Exception as exc:
        return failure("read_error", exc)


def inspect_tool(name: str) -> dict:
    try:
        valid_name(name)
        snapshot = read_diagram(WORKSPACE, name)
        snapshot_id = save_snapshot(snapshot)
        issues = []

        for page in snapshot["pages"]:
            cells = page["cells"]
            nodes = {
                cell["id"]: cell for cell in cells
                if cell.get("vertex") == "1"
            }

            for cell in cells:
                if cell.get("vertex") == "1":
                    if not cell.get("value", "").strip():
                        issues.append({
                            "type": "empty_name",
                            "page_id": page["id"],
                            "cell_id": cell["id"],
                        })

                if cell.get("edge") == "1":
                    for endpoint in ("source", "target"):
                        value = cell.get(endpoint)
                        if not value:
                            issues.append({
                                "type": "missing_endpoint",
                                "page_id": page["id"],
                                "cell_id": cell["id"],
                                "endpoint": endpoint,
                            })
                        elif value not in nodes:
                            issues.append({
                                "type": "invalid_endpoint",
                                "page_id": page["id"],
                                "cell_id": cell["id"],
                                "endpoint": endpoint,
                                "value": value,
                            })

        return success({
            "snapshot_id": snapshot_id,
            "version": snapshot["version"],
            "issues": issues,
            "issue_count": len(issues),
        })
    except Exception as exc:
        return failure("inspect_error", exc)


def apply_tool(name: str, expected_version: str, operations: list[dict]) -> dict:
    try:
        valid_name(name)

        if not isinstance(expected_version, str) or not expected_version:
            return failure("invalid_arguments", "expected_version 必须是非空字符串")

        if not isinstance(operations, list) or not 1 <= len(operations) <= 20:
            return failure("invalid_arguments", "operations 必须包含 1–20 项操作")

        allowed_fields = {
            "rename_node": {"op", "page_id", "cell_id", "label"},
            "add_edge": {"op", "page_id", "cell_id", "source", "target"},
            "set_endpoints": {"op", "page_id", "cell_id", "source", "target"},
        }

        for operation in operations:
            if not isinstance(operation, dict):
                return failure("invalid_arguments", "每项操作必须是对象")

            kind = operation.get("op")
            if kind not in allowed_fields:
                return failure("invalid_arguments", f"未知操作类型：{kind}")

            if set(operation) != allowed_fields[kind]:
                return failure("invalid_arguments", f"{kind} 参数缺失或包含未知字段")

            for key in ("page_id", "cell_id"):
                if not isinstance(operation[key], str) or not operation[key]:
                    return failure("invalid_arguments", f"{key} 必须是非空字符串")

            if kind == "rename_node":
                if not isinstance(operation["label"], str):
                    return failure("invalid_arguments", "label 必须是字符串")
            else:
                for key in ("source", "target"):
                    if not isinstance(operation[key], str) or not operation[key]:
                        return failure("invalid_arguments", f"{key} 必须是非空字符串")

        # 先执行完整批次；底层适配器保证失败时不写入
        updated = apply_operations(
            WORKSPACE, name, expected_version, operations
        )
        snapshot_id = save_snapshot(updated)

        return success({
            "snapshot_id": snapshot_id,
            "version": updated["version"],
            "pages": updated["pages"],
            "operation_count": len(operations),
        })
    except Exception as exc:
        message = str(exc)
        code = "version_conflict" if "version_conflict" in message else "apply_error"
        return failure(code, message)


def compare_tool(before: dict, after: dict) -> dict:
    try:
        changes = []

        old_pages = {p["id"]: p for p in before["pages"]}
        new_pages = {p["id"]: p for p in after["pages"]}

        for page_id in old_pages.keys() | new_pages.keys():
            if page_id not in old_pages:
                changes.append({"type": "page_added", "page_id": page_id})
                continue
            if page_id not in new_pages:
                changes.append({"type": "page_removed", "page_id": page_id})
                continue

            old_cells = {c["id"]: c for c in old_pages[page_id]["cells"]}
            new_cells = {c["id"]: c for c in new_pages[page_id]["cells"]}

            for cell_id in old_cells.keys() | new_cells.keys():
                if cell_id not in old_cells:
                    changes.append({
                        "type": "cell_added",
                        "page_id": page_id,
                        "cell_id": cell_id,
                    })
                elif cell_id not in new_cells:
                    changes.append({
                        "type": "cell_removed",
                        "page_id": page_id,
                        "cell_id": cell_id,
                    })
                else:
                    old = old_cells[cell_id]
                    new = new_cells[cell_id]
                    fields = {}
                    for key in old.keys() | new.keys():
                        if old.get(key) != new.get(key):
                            fields[key] = {
                                "before": old.get(key),
                                "after": new.get(key),
                            }
                    if fields:
                        changes.append({
                            "type": "cell_changed",
                            "page_id": page_id,
                            "cell_id": cell_id,
                            "fields": fields,
                        })

        return success({
            "before_version": before["version"],
            "after_version": after["version"],
            "changes": changes,
            "change_count": len(changes),
        })
    except Exception as exc:
        return failure("compare_error", exc)


def dispatch(name: str, arguments: dict) -> dict:
    if not isinstance(arguments, dict):
        return failure("invalid_arguments", "工具参数必须是 JSON 对象")

    handlers = {
        "read_diagram": (read_tool, {"name"}),
        "inspect_diagram": (inspect_tool, {"name"}),
        "apply_changes": (
            apply_tool, {"name", "expected_version", "operations"}
        ),
        "compare_changes": (
            None, {"before", "after"}
        ),
    }

    if name not in handlers:
        return failure("unknown_tool", f"未知工具：{name}")

    handler, required = handlers[name]

    if set(arguments) != required:
        return failure(
            "invalid_arguments",
            f"参数必须恰好为：{', '.join(sorted(required))}",
        )

    if name == "compare_changes":
        before_id = arguments["before"]
        after_id = arguments["after"]
        if before_id not in SNAPSHOTS or after_id not in SNAPSHOTS:
            return failure("invalid_snapshot", "找不到指定的快照标识")
        return compare_tool(SNAPSHOTS[before_id], SNAPSHOTS[after_id])

    return handler(**arguments)