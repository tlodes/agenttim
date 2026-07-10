"""
BFCL v4 → JUNE Evaluation Format Converter.
Reads Berkeley Function Calling Leaderboard test data + ground truth
and converts to JUNE evaluation format (JSON files loadable by bfcl_loader).
Supported BFCL categories:
    Single-Turn:
        simple_python (399)  → STurn-1T   simple
        simple_java (99)     → STurn-1T   simple_java
        simple_javascript (49) → STurn-1T simple_js
        multiple (199)       → STurn-1T   multiple (tool selection)
        parallel (199)       → STurn-MT   parallel
        parallel_multiple (199) → STurn-MT parallel_multiple

    Multi-Turn:
        multi_turn_base (200)       → MTurn-MT  base
        multi_turn_miss_param (200) → MTurn-MT  missing_params
        multi_turn_miss_func (200)  → MTurn-MT  missing_func
Usage:
    cd agenttim/evaluation
    python scripts/convert_bfcl.py --bfcl-path "C:/Users/.../bfcl/gorilla-main/berkeley-function-call-leaderboard/bfcl_eval/data"
    python scripts/convert_bfcl.py --bfcl-path "..." --categories simple_python,parallel
    python scripts/convert_bfcl.py --bfcl-path "..." --limit 50
"""
import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any
BFCL_FILE_MAP: dict[str, str] = {

    "simple_python": "BFCL_v4_simple_python.json",

    "simple_java": "BFCL_v4_simple_java.json",

    "simple_javascript": "BFCL_v4_simple_javascript.json",

    "multiple": "BFCL_v4_multiple.json",

    "parallel": "BFCL_v4_parallel.json",

    "parallel_multiple": "BFCL_v4_parallel_multiple.json",

    "multi_turn_base": "BFCL_v4_multi_turn_base.json",

    "multi_turn_miss_param": "BFCL_v4_multi_turn_miss_param.json",

    "multi_turn_miss_func": "BFCL_v4_multi_turn_miss_func.json",

    "multi_turn_long_context": "BFCL_v4_multi_turn_long_context.json",
}
GROUND_TRUTH_DIR = "possible_answer"
FUNC_DOC_DIR = "multi_turn_func_doc"
DIMENSION_MAP: dict[str, str] = {

    "simple_python": "STurn-1T",

    "simple_java": "STurn-1T",

    "simple_javascript": "STurn-1T",

    "multiple": "STurn-1T",

    "parallel": "STurn-MT",

    "parallel_multiple": "STurn-MT",

    "multi_turn_base": "MTurn-MT",

    "multi_turn_miss_param": "MTurn-MT",

    "multi_turn_miss_func": "MTurn-MT",

    "multi_turn_long_context": "MTurn-MT",
}
MT_CATEGORY_MAP: dict[str, str] = {

    "multi_turn_base": "base",

    "multi_turn_miss_param": "missing_params",

    "multi_turn_miss_func": "missing_func",

    "multi_turn_long_context": "long_context",
}
OUTPUT_FILE_MAP: dict[str, str] = {

    "simple_python": "sturn_1t_simple.json",

    "simple_java": "sturn_1t_simple_java.json",

    "simple_javascript": "sturn_1t_simple_js.json",

    "multiple": "sturn_1t_multiple.json",

    "parallel": "sturn_mt_parallel.json",

    "parallel_multiple": "sturn_mt_parallel_multiple.json",

    "multi_turn_base": "mturn_mt_base.json",

    "multi_turn_miss_param": "mturn_mt_missing_params.json",

    "multi_turn_miss_func": "mturn_mt_missing_func.json",

    "multi_turn_long_context": "mturn_mt_long_context.json",
}
SINGLE_TURN_CATEGORIES = {

    "simple_python", "simple_java", "simple_javascript",

    "multiple", "parallel", "parallel_multiple",
}
MULTI_TURN_CATEGORIES = {

    "multi_turn_base", "multi_turn_miss_param", "multi_turn_miss_func",

    "multi_turn_long_context",
}
DEFAULT_CATEGORIES = list(BFCL_FILE_MAP.keys())
def load_jsonl(path: Path) -> list[dict[str, Any]]:

    """Load a JSONL file (one JSON object per line)."""

    results: list[dict[str, Any]] = []

    with open(path, encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:

                results.append(json.loads(line))

    return results
def load_all_func_docs(func_doc_dir: Path) -> dict[str, dict[str, Any]]:

    """Load all multi-turn function doc files into a lookup by function name."""

    func_docs: dict[str, dict[str, Any]] = {}

    if not func_doc_dir.exists():

        return func_docs

    for doc_file in func_doc_dir.glob("*.json"):

        for func_def in load_jsonl(doc_file):

            name = func_def.get("name", "")

            if name:

                func_docs[name] = func_def

    return func_docs
def parse_function_call_string(

    call_str: str,

    func_docs: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    """Parse a BFCL function call string into structured format.

    Examples:
        "cd(folder='document')"
            → {"name": "cd", "arguments": {"folder": "document"}}
        "sort('final_report.pdf')"
            → {"name": "sort", "arguments": {"file_name": "final_report.pdf"}}
        "wc(file_name='summary.txt',mode='w')"
            → {"name": "wc", "arguments": {"file_name": "summary.txt", "mode": "w"}}
    """

    try:

        tree = ast.parse(call_str, mode="eval")

        call_node = tree.body

        if not isinstance(call_node, ast.Call):

            return {"name": call_str, "arguments": {}, "_parse_error": "not a Call node"}

        func_name = _extract_func_name(call_node.func)

        arguments: dict[str, Any] = {}

        for kw in call_node.keywords:

            arguments[kw.arg] = ast.literal_eval(kw.value)

        if call_node.args:

            _resolve_positional_args(call_node.args, func_name, func_docs, arguments)

        return {"name": func_name, "arguments": arguments}

    except Exception as e:

        return {"name": call_str, "arguments": {}, "_parse_error": str(e)}
def _extract_func_name(node: ast.expr) -> str:

    """Extract function name from AST node (handles dotted names)."""

    if isinstance(node, ast.Name):

        return node.id

    if isinstance(node, ast.Attribute):

        parts: list[str] = []

        current = node

        while isinstance(current, ast.Attribute):

            parts.append(current.attr)

            current = current.value

        if isinstance(current, ast.Name):

            parts.append(current.id)

        return ".".join(reversed(parts))

    return ast.dump(node)
def _resolve_positional_args(

    args: list[ast.expr],

    func_name: str,

    func_docs: dict[str, dict[str, Any]],

    arguments: dict[str, Any],
) -> None:

    """Resolve positional args to parameter names using func_doc."""

    func_doc = func_docs.get(func_name)

    if func_doc:

        param_names = list(

            func_doc.get("parameters", {}).get("properties", {}).keys()

        )

    else:

        param_names = []

    for i, arg_node in enumerate(args):

        value = ast.literal_eval(arg_node)

        if i < len(param_names):

            arguments[param_names[i]] = value

        else:

            arguments[f"_positional_{i}"] = value
def _extract_input(question: list) -> str:

    """Extract user input from BFCL question format [[{"role":"user","content":"..."}]]."""

    if question and question[0]:

        first_turn = question[0]

        if isinstance(first_turn, list) and first_turn:

            msg = first_turn[0]

            if isinstance(msg, dict):

                return msg.get("content", "")

    return ""
def _convert_ground_truth_entry(gt_entry: dict[str, Any]) -> dict[str, Any]:

    """Convert a single BFCL ground_truth dict to expected_tool_call format.

    BFCL format:  {"func_name": {"param": [accepted_values]}}
    Output format: {"name": "func_name", "arguments": {"param": [accepted_values]}}
    """

    func_name = list(gt_entry.keys())[0]

    params = gt_entry[func_name]

    return {"name": func_name, "arguments": params}
def convert_single_turn_case(

    data_entry: dict[str, Any],

    gt_entry: dict[str, Any],

    category: str,
) -> dict[str, Any]:

    """Convert a single-turn BFCL case to JUNE format."""

    source_id = data_entry["id"]

    dimension = DIMENSION_MAP[category]

    user_input = _extract_input(data_entry.get("question", []))

    ground_truth: list[dict[str, Any]] = gt_entry.get("ground_truth", [])

    expected_tool_calls = [_convert_ground_truth_entry(gt) for gt in ground_truth]

    result: dict[str, Any] = {

        "id": f"BFCL-{source_id}",

        "source_id": source_id,

        "source_category": category,

        "dimension": dimension,

        "dataset": "BFCL",

        "input": user_input,

        "available_functions": data_entry.get("function", []),

        "expected_tool_calls": expected_tool_calls,

    }

    if category in ("parallel", "parallel_multiple"):

        tool_names = [tc["name"] for tc in expected_tool_calls]

        result["expected_execution"] = [tool_names]

    return result
def convert_multi_turn_case(

    data_entry: dict[str, Any],

    gt_entry: dict[str, Any],

    category: str,

    func_docs: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    """Convert a multi-turn BFCL case to JUNE format."""

    source_id = data_entry["id"]

    mt_category = MT_CATEGORY_MAP[category]

    questions: list[list[dict]] = data_entry.get("question", [])

    ground_truth: list[list[str]] = gt_entry.get("ground_truth", [])

    turns: list[dict[str, Any]] = []

    for turn_idx, turn_messages in enumerate(questions):

        user_input = ""

        if turn_messages and isinstance(turn_messages, list):

            for msg in turn_messages:

                if isinstance(msg, dict) and msg.get("role") == "user":

                    user_input = msg.get("content", "")

                    break

        if turn_idx < len(ground_truth):

            gt_calls: list[str] = ground_truth[turn_idx]

        else:

            gt_calls = []

        expected_tool_calls = [

            parse_function_call_string(call_str, func_docs)

            for call_str in gt_calls

        ]

        is_clarification = len(gt_calls) == 0

        turn: dict[str, Any] = {

            "input": user_input,

            "expected_tool_calls": expected_tool_calls,

        }

        if is_clarification:

            turn["expects_clarification"] = True

        turns.append(turn)

    involved_classes = data_entry.get("involved_classes", [])

    path_functions = data_entry.get("path", [])

    available_functions = _collect_available_functions(

        involved_classes, path_functions, func_docs,

        excluded=data_entry.get("excluded_function", []),

    )

    result: dict[str, Any] = {

        "id": f"BFCL-{source_id}",

        "source_id": source_id,

        "source_category": category,

        "dimension": "MTurn-MT",

        "dataset": "BFCL",

        "category": mt_category,

        "turns": turns,

        "available_functions": available_functions,

    }

    if "initial_config" in data_entry:

        result["initial_config"] = data_entry["initial_config"]

    if category == "multi_turn_miss_func" and "missed_function" in data_entry:

        result["missed_functions"] = data_entry["missed_function"]

    if category == "multi_turn_long_context":

        result["long_context"] = True

    return result
def _collect_available_functions(

    involved_classes: list[str],

    path_functions: list[str],

    func_docs: dict[str, dict[str, Any]],

    excluded: list[str] | None = None,
) -> list[dict[str, Any]]:

    """Collect function definitions for a multi-turn case.

    Uses the path field (e.g. "GorillaFileSystem.grep") to find function names,
    then looks them up in func_docs.
    """

    excluded_set = set(excluded) if excluded else set()

    seen: set[str] = set()

    functions: list[dict[str, Any]] = []

    for qualified_name in path_functions:

        short_name = qualified_name.split(".")[-1] if "." in qualified_name else qualified_name

        if short_name in excluded_set or short_name in seen:

            continue

        seen.add(short_name)

        func_def = func_docs.get(short_name)

        if func_def:

            functions.append(func_def)

    return functions
def convert_category(

    bfcl_data_dir: Path,

    output_dir: Path,

    category: str,

    func_docs: dict[str, dict[str, Any]],

    limit: int | None = None,
) -> int:

    """Convert one BFCL category. Returns number of cases converted."""

    data_file = bfcl_data_dir / BFCL_FILE_MAP[category]

    gt_file = bfcl_data_dir / GROUND_TRUTH_DIR / BFCL_FILE_MAP[category]

    if not data_file.exists():

        print(f"  SKIP: {data_file.name} not found")

        return 0

    if not gt_file.exists():

        print(f"  SKIP: ground truth not found for {category}")

        return 0

    data_entries = load_jsonl(data_file)

    gt_entries = load_jsonl(gt_file)

    gt_lookup = {entry["id"]: entry for entry in gt_entries}

    if limit:

        data_entries = data_entries[:limit]

    converted: list[dict[str, Any]] = []

    errors = 0

    for entry in data_entries:

        entry_id = entry["id"]

        gt = gt_lookup.get(entry_id)

        if not gt:

            errors += 1

            continue

        try:

            if category in SINGLE_TURN_CATEGORIES:

                result = convert_single_turn_case(entry, gt, category)

            else:

                result = convert_multi_turn_case(entry, gt, category, func_docs)

            converted.append(result)

        except Exception as e:

            print(f"  ERROR converting {entry_id}: {e}")

            errors += 1

    output_file = output_dir / OUTPUT_FILE_MAP[category]

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(converted, f, indent=2, ensure_ascii=False)

    if errors:

        print(f"  {len(converted)} converted, {errors} errors -> {output_file.name}")

    else:

        print(f"  {len(converted)} cases -> {output_file.name}")

    return len(converted)
def main() -> None:

    parser = argparse.ArgumentParser(

        description="Convert BFCL v4 test cases to JUNE evaluation format"

    )

    parser.add_argument(

        "--bfcl-path",

        type=Path,

        required=True,

        help="Path to BFCL bfcl_eval/data/ directory",

    )

    parser.add_argument(

        "--output-path",

        type=Path,

        default=None,

        help="Output directory (default: test_cases/bfcl_data/)",

    )

    parser.add_argument(

        "--categories",

        type=str,

        default=None,

        help=f"Comma-separated categories to convert (default: all). "

             f"Available: {', '.join(DEFAULT_CATEGORIES)}",

    )

    parser.add_argument(

        "--limit",

        type=int,

        default=None,

        help="Max cases per category (default: all)",

    )

    args = parser.parse_args()

    bfcl_data_dir = args.bfcl_path

    if not bfcl_data_dir.exists():

        print(f"ERROR: BFCL data dir not found: {bfcl_data_dir}")

        sys.exit(1)

    if args.output_path:

        output_dir = args.output_path

    else:

        output_dir = Path(__file__).resolve().parent.parent / "test_cases" / "bfcl_data"

    categories = (

        args.categories.split(",") if args.categories else DEFAULT_CATEGORIES

    )

    invalid = [c for c in categories if c not in BFCL_FILE_MAP]

    if invalid:

        print(f"ERROR: Unknown categories: {invalid}")

        print(f"Available: {', '.join(DEFAULT_CATEGORIES)}")

        sys.exit(1)

    func_doc_dir = bfcl_data_dir / FUNC_DOC_DIR

    func_docs = load_all_func_docs(func_doc_dir)

    print(f"Loaded {len(func_docs)} function definitions from {FUNC_DOC_DIR}/")

    print(f"\nConverting {len(categories)} categories -> {output_dir}/\n")

    total = 0

    for category in categories:

        dimension = DIMENSION_MAP[category]

        print(f"[{dimension}] {category}:")

        count = convert_category(bfcl_data_dir, output_dir, category, func_docs, args.limit)

        total += count

    print(f"\nDone. {total} total cases converted.")

    print(f"Output: {output_dir}/")
if __name__ == "__main__":

    main()

