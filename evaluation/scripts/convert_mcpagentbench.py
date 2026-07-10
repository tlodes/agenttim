"""
MCPAgentBench -> JUNE Evaluation Format Converter.
Reads MCPAgentBench test data and MCP server tool definitions,
converts to JUNE evaluation format (JSON files loadable by mcpagentbench_loader).
MCPAgentBench provides:
    - content: user input (natural language task)
    - tools: expected tool names per step [[step1_tools], [step2_tools]]
    - inputs: expected arguments per tool per step [[step1_args], [step2_args]]
Execution pattern is encoded in the structure:
    [["tool_a", "tool_b"]]        -> parallel (one step, two tools)
    [["tool_a"], ["tool_b"]]      -> sequential (two steps, one tool each)
    [["tool_a", "tool_b"], ["c"]] -> mixed (parallel step, then sequential)
Data splits:
    daytasks_single.json              (30)  -> STurn-1T
    daytasks_with_2_parallel_tools    (20)  -> STurn-MT parallel
    daytasks_with_2_sequential_tools  (20)  -> STurn-MT sequential
    daytasks_with_3_tools             (20)  -> STurn-MT sequential
    protasks_single.json              (30)  -> STurn-1T
    protasks_with_2_parallel_tools    (20)  -> STurn-MT parallel
    protasks_with_2_sequential_tools  (20)  -> STurn-MT sequential
    protasks_with_3_tools             (18)  -> STurn-MT sequential
Usage:
    cd agenttim/evaluation
    python scripts/convert_mcpagentbench.py \\
        --bench-path "C:/Users/.../MCPAgentBench-5C16"
    python scripts/convert_mcpagentbench.py \\
        --bench-path "..." --categories daytasks_single,protasks_single
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any
DATA_FILES: dict[str, str] = {

    "daytasks_single": "daytasks_single.json",

    "daytasks_2_parallel": "daytasks_with_2_parallel_tools.json",

    "daytasks_2_sequential": "daytasks_with_2_sequential_tools.json",

    "daytasks_3_tools": "daytasks_with_3_tools.json",

    "protasks_single": "protasks_single.json",

    "protasks_2_parallel": "protasks_with_2_parallel_tools.json",

    "protasks_2_sequential": "protasks_with_2_sequential_tools.json",

    "protasks_3_tools": "protasks_with_3_tools.json",
}
DIMENSION_MAP: dict[str, str] = {

    "daytasks_single": "STurn-1T",

    "daytasks_2_parallel": "STurn-MT",

    "daytasks_2_sequential": "STurn-MT",

    "daytasks_3_tools": "STurn-MT",

    "protasks_single": "STurn-1T",

    "protasks_2_parallel": "STurn-MT",

    "protasks_2_sequential": "STurn-MT",

    "protasks_3_tools": "STurn-MT",
}
EXECUTION_TYPE_MAP: dict[str, str] = {

    "daytasks_single": "single",

    "daytasks_2_parallel": "parallel",

    "daytasks_2_sequential": "sequential",

    "daytasks_3_tools": "sequential",

    "protasks_single": "single",

    "protasks_2_parallel": "parallel",

    "protasks_2_sequential": "sequential",

    "protasks_3_tools": "sequential",
}
OUTPUT_FILES: dict[str, str] = {

    "daytasks_single": "sturn_1t_daytasks.json",

    "daytasks_2_parallel": "sturn_mt_daytasks_parallel.json",

    "daytasks_2_sequential": "sturn_mt_daytasks_sequential.json",

    "daytasks_3_tools": "sturn_mt_daytasks_3tools.json",

    "protasks_single": "sturn_1t_protasks.json",

    "protasks_2_parallel": "sturn_mt_protasks_parallel.json",

    "protasks_2_sequential": "sturn_mt_protasks_sequential.json",

    "protasks_3_tools": "sturn_mt_protasks_3tools.json",
}
DEFAULT_CATEGORIES = list(DATA_FILES.keys())
def extract_tool_schema(server_path: Path) -> dict[str, Any] | None:

    """Extract tool name, description, and parameters from an MCP server .py file.

    Parses the @mcp.tool() decorated function, its signature, type annotations,
    and docstring to produce a JSON-schema-like tool definition.
    """

    try:

        source = server_path.read_text(encoding="utf-8")

    except Exception:

        return None

    try:

        tree = ast.parse(source)

    except SyntaxError:

        return None

    for node in ast.walk(tree):

        if not isinstance(node, ast.FunctionDef):

            continue

        if not _has_mcp_tool_decorator(node):

            continue

        func_name = node.name

        raw_doc = ast.get_docstring(node) or ""

        raw_doc = raw_doc.strip().strip('"').strip()

        description, param_descs = _parse_docstring(raw_doc)

        parameters, required = _extract_params(node, param_descs)

        return {

            "name": func_name,

            "description": description,

            "parameters": {

                "type": "dict",

                "properties": parameters,

                "required": required,

            },

        }

    return None
def _has_mcp_tool_decorator(node: ast.FunctionDef) -> bool:

    for dec in node.decorator_list:

        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):

            if dec.func.attr == "tool":

                return True

        if isinstance(dec, ast.Attribute) and dec.attr == "tool":

            return True

    return False
def _parse_docstring(raw_doc: str) -> tuple[str, dict[str, dict]]:

    """Split docstring into description and per-parameter info."""

    parts = re.split(r"\n\s*Args:", raw_doc, maxsplit=1)

    description = parts[0].strip()

    param_descs: dict[str, dict] = {}

    if len(parts) > 1:

        args_section = parts[1]

        for m in re.finditer(

            r"(\w+)\s*\(([^)]+)\)\s*:\s*(.+?)(?=\n\s*\w+\s*\(|\n\s*Returns:|\Z)",

            args_section,

            re.DOTALL,

        ):

            pname = m.group(1)

            ptype = m.group(2).strip()

            pdesc = " ".join(m.group(3).strip().split())

            param_descs[pname] = {"type": ptype, "description": pdesc}

    return description, param_descs
def _extract_params(

    node: ast.FunctionDef, param_descs: dict[str, dict]
) -> tuple[dict[str, Any], list[str]]:

    """Extract parameters and required list from function signature."""

    parameters: dict[str, Any] = {}

    required: list[str] = []

    args = node.args

    defaults_offset = len(args.args) - len(args.defaults)

    for i, arg in enumerate(args.args):

        if arg.arg == "self":

            continue

        ptype = "string"

        if arg.annotation and isinstance(arg.annotation, ast.Name):

            ptype = arg.annotation.id

        elif arg.arg in param_descs:

            ptype = param_descs[arg.arg]["type"]

        param: dict[str, Any] = {"type": ptype}

        if arg.arg in param_descs:

            param["description"] = param_descs[arg.arg]["description"]

        default_idx = i - defaults_offset

        if 0 <= default_idx < len(args.defaults):

            try:

                param["default"] = ast.literal_eval(args.defaults[default_idx])

            except Exception:

                pass

        else:

            required.append(arg.arg)

        parameters[arg.arg] = param

    return parameters, required
def load_all_tool_schemas(servers_dir: Path) -> dict[str, dict[str, Any]]:

    """Load tool schemas from all MCP server files. Returns {tool_name: schema}."""

    schemas: dict[str, dict[str, Any]] = {}

    if not servers_dir.exists():

        return schemas

    for server_file in sorted(servers_dir.glob("*.py")):

        if server_file.name == "__init__.py":

            continue

        schema = extract_tool_schema(server_file)

        if schema:

            schemas[schema["name"]] = schema

    return schemas
def convert_task(

    task: dict[str, Any],

    category: str,

    tool_schemas: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    """Convert a single MCPAgentBench task to JUNE format."""

    source_id = task["id"]

    dimension = DIMENSION_MAP[category]

    execution_type = EXECUTION_TYPE_MAP[category]

    expected_tool_calls: list[dict[str, Any]] = []

    for step_tools, step_inputs in zip(task["tools"], task["inputs"]):

        for tool_name, tool_args in zip(step_tools, step_inputs):

            expected_tool_calls.append({

                "name": tool_name,

                "arguments": tool_args,

            })

    expected_execution: list[list[str]] = [

        list(step_tools) for step_tools in task["tools"]

    ]

    all_tool_names: set[str] = set()

    for step_tools in task["tools"]:

        all_tool_names.update(step_tools)

    available_functions = [

        tool_schemas[name]

        for name in sorted(all_tool_names)

        if name in tool_schemas

    ]

    result: dict[str, Any] = {

        "id": f"MCPAB-{source_id}",

        "source_id": source_id,

        "source_category": category,

        "dimension": dimension,

        "dataset": "MCPAgentBench",

        "category": execution_type,

        "input": task["content"],

        "expected_tool_calls": expected_tool_calls,

        "expected_execution": expected_execution,

        "available_functions": available_functions,

    }

    return result
def convert_category(

    data_dir: Path,

    output_dir: Path,

    category: str,

    tool_schemas: dict[str, dict[str, Any]],

    limit: int | None = None,
) -> int:

    """Convert one MCPAgentBench category. Returns number of cases converted."""

    data_file = data_dir / DATA_FILES[category]

    if not data_file.exists():

        print(f"  SKIP: {data_file.name} not found")

        return 0

    with open(data_file, encoding="utf-8") as f:

        tasks = json.load(f)

    if limit:

        tasks = tasks[:limit]

    converted = [convert_task(t, category, tool_schemas) for t in tasks]

    output_file = output_dir / OUTPUT_FILES[category]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(converted, f, indent=2, ensure_ascii=False)

    print(f"  {len(converted)} cases -> {output_file.name}")

    return len(converted)
def main() -> None:

    parser = argparse.ArgumentParser(

        description="Convert MCPAgentBench test cases to JUNE evaluation format"

    )

    parser.add_argument(

        "--bench-path",

        type=Path,

        required=True,

        help="Path to MCPAgentBench root directory",

    )

    parser.add_argument(

        "--output-path",

        type=Path,

        default=None,

        help="Output directory (default: test_cases/mcpagentbench_data/)",

    )

    parser.add_argument(

        "--categories",

        type=str,

        default=None,

        help=f"Comma-separated categories (default: all). "

             f"Available: {', '.join(DEFAULT_CATEGORIES)}",

    )

    parser.add_argument(

        "--limit",

        type=int,

        default=None,

        help="Max cases per category (default: all)",

    )

    args = parser.parse_args()

    bench_path = args.bench_path

    if not bench_path.exists():

        print(f"ERROR: MCPAgentBench dir not found: {bench_path}")

        sys.exit(1)

    data_dir = bench_path / "data"

    servers_dir = bench_path / "servers"

    if args.output_path:

        output_dir = args.output_path

    else:

        output_dir = (

            Path(__file__).resolve().parent.parent

            / "test_cases"

            / "mcpagentbench_data"

        )

    categories = (

        args.categories.split(",") if args.categories else DEFAULT_CATEGORIES

    )

    invalid = [c for c in categories if c not in DATA_FILES]

    if invalid:

        print(f"ERROR: Unknown categories: {invalid}")

        print(f"Available: {', '.join(DEFAULT_CATEGORIES)}")

        sys.exit(1)

    print(f"Extracting tool schemas from {servers_dir}/...")

    tool_schemas = load_all_tool_schemas(servers_dir)

    print(f"Extracted {len(tool_schemas)} tool definitions.\n")

    schemas_output = output_dir / "tool_schemas.json"

    schemas_output.parent.mkdir(parents=True, exist_ok=True)

    with open(schemas_output, "w", encoding="utf-8") as f:

        json.dump(tool_schemas, f, indent=2, ensure_ascii=False)

    print(f"Tool schemas saved to {schemas_output.name}")

    print(f"Converting {len(categories)} categories -> {output_dir}/\n")

    total = 0

    for category in categories:

        dimension = DIMENSION_MAP[category]

        exec_type = EXECUTION_TYPE_MAP[category]

        print(f"[{dimension}] {category} ({exec_type}):")

        count = convert_category(data_dir, output_dir, category, tool_schemas, args.limit)

        total += count

    print(f"\nDone. {total} total cases converted.")

    print(f"Output: {output_dir}/")
if __name__ == "__main__":

    main()

