"""HW1 实验程序：按 assignments/HW1.md 实现模型调用、评估和批量记录。"""
import argparse
import json
from pathlib import Path
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from ollama import Client
import uuid

ROOT = Path(__file__).resolve().parents[2]


# def generate(case: dict, mode: str, schema: dict) -> str:
#     # TODO: 调用 Ollama，三种生成方式使用相同的模型和生成设置。
#     # 生成方式为 brief、contract、schema；返回模型的原始内容。
#     raise NotImplementedError("请先实现模型调用和三种提示方式")

def generate(case: dict, mode: str, schema: dict) -> str:
    load_dotenv(ROOT / ".env")

    client = Client(
        host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    )
    model = os.getenv("OLLAMA_MODEL", "qwen3:4b-q4_K_M")

    case_text = json.dumps(case, ensure_ascii=False, indent=2)

    base_instruction = (
        "将给定需求转换为流程图规格。"
        "只输出 JSON 对象，包含 nodes、edges、questions 三个字段。"
        "nodes 中每项包含 id 和 label；"
        "edges 中每项包含 source、target 和 label；"
        "questions 是字符串数组。"
        "不要输出 Markdown 代码围栏。"
    )

    if mode == "brief":
        prompt = (
            "请根据以下案例生成流程图 JSON。"
            "只输出一个合法的 JSON 对象，必须包含 nodes、edges、questions 三个字段。"
            "nodes 中每项必须包含 id 和 label；"
            "edges 中每项必须包含 source、target 和 label；"
            "questions 必须是字符串数组。"
            "不要使用其他字段名，不要输出 Markdown 代码围栏。\n"
            f"案例：\n{case_text}"
        )
        response = client.generate(
            model=model,
            prompt=prompt,
            options={"temperature": 0}
        )

    elif mode == "contract":
        prompt = (
            f"{base_instruction}\n"
            f"案例：\n{case_text}"
        )
        response = client.generate(
            model=model,
            prompt=prompt,
            options={"temperature": 0}
        )

    elif mode == "schema":
        prompt = (
                base_instruction
                + "\n严格遵守提供的 JSON Schema。"
                + "\nJSON Schema 如下：\n"
                + json.dumps(schema, ensure_ascii=False, indent=2)
                + "\n只输出符合该 Schema 的 JSON，不要输出 Markdown 代码围栏。"
        )
        response = client.generate(
            model=model,
            prompt=prompt,
            format=schema if mode == "schema" else "",
            options={"temperature": 0}
        )

    else:
        raise ValueError(f"未知生成模式：{mode}")

    return response.response


# def evaluate(case: dict, content: str) -> dict:
#     # TODO: 分别记录 JSON/Schema 检查、图关系检查及需要人工判断的含义。
#     raise NotImplementedError("请先实现解析和评估记录")

def evaluate(case: dict, content: str) -> dict:
    from jsonschema import validate
    from jsonschema.exceptions import ValidationError

    schema_path = Path(__file__).with_name("spec.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    result = {
        "case_id": case.get("id"),
        "json_valid": False,
        "schema_valid": False,
        "graph_valid": False,
        "errors": [],
        "manual_review": [
            "请人工检查流程含义是否符合需求。",
            "请检查是否保留了未确定的信息，并将疑问写入 questions。"
        ]
    }

    # 1. 检查 JSON 格式
    try:

        cleaned = content.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        data = json.loads(cleaned)

        result["json_valid"] = True
    except json.JSONDecodeError as e:
        result["errors"].append(f"JSON 解析失败：{e}")
        return result

    # 2. 检查 JSON Schema
    try:
        validate(instance=data, schema=schema)
        result["schema_valid"] = True
    except ValidationError as e:
        result["errors"].append(f"Schema 检查失败：{e.message}")

    if not isinstance(data, dict):
        result["errors"].append("JSON 顶层必须是对象")
        return result

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not isinstance(nodes, list) or not isinstance(edges, list):
        result["errors"].append("nodes 和 edges 必须是数组")
        return result

    # 3. 检查图关系：节点 ID 唯一、连接端点存在、避免保留 ID
    node_ids = [
        node.get("id")
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    ]

    if len(node_ids) != len(set(node_ids)):
        result["errors"].append("存在重复的节点 ID")

    reserved_ids = {"0", "1"}
    if reserved_ids.intersection(node_ids):
        result["errors"].append("节点 ID 不能使用保留值 '0' 或 '1'")

    known_ids = set(node_ids)

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            result["errors"].append(f"第 {index + 1} 条连接不是对象")
            continue

        source = edge.get("source")
        target = edge.get("target")

        if source not in known_ids:
            result["errors"].append(
                f"第 {index + 1} 条连接的 source 不存在：{source}"
            )

        if target not in known_ids:
            result["errors"].append(
                f"第 {index + 1} 条连接的 target 不存在：{target}"
            )

    result["graph_valid"] = not any(
        "重复的节点 ID" in error
        or "保留值" in error
        or "连接的 source 不存在" in error
        or "连接的 target 不存在" in error
        or "连接不是对象" in error
        for error in result["errors"]
    )

    result["parsed"] = data
    return result



# def run(split: str) -> None:
#     cases = json.loads((ROOT / "materials/cases/prompt-cases.json").read_text(encoding="utf-8"))
#     schema = json.loads(Path(__file__).with_name("spec.schema.json").read_text(encoding="utf-8"))
#     # TODO: 按 split 选取案例，遍历三种生成方式，每种重复两次。
#     # 保存原始输出、耗时、模型配置和错误。
#     # 将输出写入 .runtime/hw01，每次运行使用独立 run_id。
#     raise NotImplementedError(f"请先实现 {split} 的批量实验；已读取 {len(cases)} 个案例")


def run(split: str) -> None:
    load_dotenv(ROOT / ".env")
    cases = json.loads(
        (ROOT / "materials/cases/prompt-cases.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        Path(__file__).with_name("spec.schema.json").read_text(encoding="utf-8")
    )

    selected_cases = [case for case in cases if case.get("split") == split]
    if not selected_cases:
        raise ValueError(f"没有找到 split={split} 的案例")

    model = os.getenv("OLLAMA_MODEL", "qwen3:4b-q4_K_M")
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    temperature = 0
    modes = ["brief", "contract", "schema"]
    run_id = f"{split}_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    output_dir = ROOT / ".runtime" / "hw01" / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []

    for case in selected_cases:
        for mode in modes:
            for repeat in range(1, 3):
                print(
                    f"运行案例 {case['id']} | 模式 {mode} | "
                    f"第 {repeat} 次"
                )

                started = time.perf_counter()
                try:
                    content = generate(case, mode, schema)
                    elapsed = time.perf_counter() - started
                    evaluation = evaluate(case, content)

                    record = {
                        "run_id": run_id,
                        "split": split,
                        "prompt_version": "v3",
                        "case_id": case["id"],
                        "mode": mode,
                        "repeat": repeat,
                        "model": model,
                        "config": {
                            "host": host,
                            "temperature": temperature
                        },
                        "elapsed_seconds": round(elapsed, 3),
                        "raw_output": content,
                        "evaluation": evaluation,
                        "error": None,
                    }

                except Exception as exc:
                    elapsed = time.perf_counter() - started
                    record = {
                        "run_id": run_id,
                        "split": split,
                        "prompt_version": "v3",
                        "case_id": case["id"],
                        "mode": mode,
                        "repeat": repeat,
                        "model": model,
                        "config": {
                            "host": host,
                            "temperature": temperature
                        },
                        "elapsed_seconds": round(elapsed, 3),
                        "raw_output": None,
                        "evaluation": None,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                    print(f"本次运行失败：{record['error']}")

                records.append(record)

                output_file = (
                    output_dir
                    / f"{case['id']}_{mode}_repeat{repeat}.json"
                )
                output_file.write_text(
                    json.dumps(record, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

    summary = {
        "run_id": run_id,
        "split": split,
        "model": model,
        "case_count": len(selected_cases),
        "mode_count": len(modes),
        "repeats_per_mode": 2,
        "total_runs": len(records),
        "successful_generations": sum(
            record["raw_output"] is not None for record in records
        ),
        "records": records,
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n实验结束，结果保存在：{output_dir}")
    print(f"总调用次数：{len(records)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "eval"], required=True)
    args = parser.parse_args()
    run(args.split)
