"""Execution Efficiency metric — deterministic, no LLM needed.
Compares expected execution steps (parallel/sequential) against actual
tool call timeline to score how efficiently the agent used parallelism
and respected dependencies.
"""
from typing import Any, Dict, List, Optional
_OVERLAP_THRESHOLD = 0.3
def _tools_overlap(tool_a: Dict[str, Any], tool_b: Dict[str, Any]) -> bool:

    """Check if two tool calls overlapped in time."""

    a_start = tool_a.get("start_time", 0)

    a_end = a_start + tool_a.get("latency", 0)

    b_start = tool_b.get("start_time", 0)

    b_end = b_start + tool_b.get("latency", 0)

    overlap_start = max(a_start, b_start)

    overlap_end = min(a_end, b_end)

    overlap = max(0, overlap_end - overlap_start)

    min_duration = min(a_end - a_start, b_end - b_start)

    if min_duration <= 0:

        return False

    return (overlap / min_duration) >= _OVERLAP_THRESHOLD
def _find_tool_in_timeline(

    tool_name: str, timeline: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    """Find the first matching tool call in the timeline."""

    for t in timeline:

        if t["name"] == tool_name:

            return t

    return None
def calculate_efficiency(

    expected_execution: List[List[str]],

    actual_timeline: List[Dict[str, Any]],
) -> Dict[str, Any]:

    """Calculate execution efficiency score.

    Args:
        expected_execution: List of steps, each step is a list of tool names.
            Tools in the same step can run in parallel.
            Steps must run sequentially.
        actual_timeline: List of tool calls with start_time and latency.

    Returns:
        Dict with score (0-1), success, reason, and detailed checks.
    """

    checks = []

    total = 0

    passed = 0

    all_expected_tools = [t for step in expected_execution for t in step]

    actual_tool_names = {t["name"] for t in actual_timeline}

    found_expected = [t for t in all_expected_tools if t in actual_tool_names]

    missing_expected = [t for t in all_expected_tools if t not in actual_tool_names]

    for step_idx, step_tools in enumerate(expected_execution):

        if len(step_tools) > 1:

            actual_tools = []

            for name in step_tools:

                tool = _find_tool_in_timeline(name, actual_timeline)

                if tool:

                    actual_tools.append((name, tool))

            if len(actual_tools) >= 2:

                all_parallel = True

                for i in range(len(actual_tools)):

                    for j in range(i + 1, len(actual_tools)):

                        name_a, tool_a = actual_tools[i]

                        name_b, tool_b = actual_tools[j]

                        is_parallel = _tools_overlap(tool_a, tool_b)

                        total += 1

                        if is_parallel:

                            passed += 1

                            checks.append({

                                "type": "parallel",

                                "step": step_idx + 1,

                                "tools": [name_a, name_b],

                                "result": "pass",

                                "detail": "Tools ran in parallel",

                            })

                        else:

                            all_parallel = False

                            checks.append({

                                "type": "parallel",

                                "step": step_idx + 1,

                                "tools": [name_a, name_b],

                                "result": "fail",

                                "detail": "Tools ran sequentially (missed parallelization)",

                            })

        if step_idx < len(expected_execution) - 1:

            next_step_tools = expected_execution[step_idx + 1]

            for curr_name in step_tools:

                curr_tool = _find_tool_in_timeline(curr_name, actual_timeline)

                if not curr_tool:

                    continue

                curr_end = curr_tool.get("start_time", 0) + curr_tool.get("latency", 0)

                for next_name in next_step_tools:

                    next_tool = _find_tool_in_timeline(next_name, actual_timeline)

                    if not next_tool:

                        continue

                    next_start = next_tool.get("start_time", 0)

                    total += 1

                    if next_start >= curr_end - 0.1:

                        passed += 1

                        checks.append({

                            "type": "sequential",

                            "step": step_idx + 1,

                            "tools": [curr_name, next_name],

                            "result": "pass",

                            "detail": f"{next_name} waited for {curr_name} to complete",

                        })

                    else:

                        checks.append({

                            "type": "sequential",

                            "step": step_idx + 1,

                            "tools": [curr_name, next_name],

                            "result": "fail",

                            "detail": f"{next_name} started before {curr_name} finished (dependency violated)",

                        })

    score = (passed / total) if total > 0 else None

    if score is None:

        if missing_expected:

            reason = (

                f"N/A — cannot evaluate efficiency: {len(found_expected)}/{len(all_expected_tools)} "

                f"expected tools called. Missing: {missing_expected}"

            )

        elif len(all_expected_tools) <= 1:

            reason = "N/A — single expected tool, no execution pattern to evaluate"

        else:

            reason = "N/A — no execution pattern checks could be performed"

    elif score == 1.0:

        reason = "All parallel opportunities used and all dependencies respected"

    else:

        fails = [c for c in checks if c["result"] == "fail"]

        fail_details = "; ".join(c["detail"] for c in fails)

        reason = f"{passed}/{total} checks passed. Issues: {fail_details}"

    return {

        "score": score,

        "threshold": 0.7,

        "success": score is not None and score >= 0.7,

        "reason": reason,

        "checks": checks,

        "expected_tools": all_expected_tools,

        "found_tools": found_expected,

        "missing_tools": missing_expected,

    }

