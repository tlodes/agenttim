"""Save evaluation results as JSON for the Streamlit dashboard."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from .constants import MODEL_PRICING, is_orchestrator_tool
from .efficiency import calculate_efficiency
from .utils import sanitize_args
RESULTS_DIR = Path(__file__).parent.parent / "results"
def save_results(

    test_case_defs: List[Dict[str, Any]],

    eval_result: Any,

    token_trackers: List[Any],

    tool_trackers: List[Any],

    latencies: List[float],

    model_name: str,

    extra_data: Dict[str, Any] | None = None,
) -> Path:

    """Save evaluation results as JSON for the Streamlit dashboard.

    Uses the EvaluationResult returned by deepeval.evaluate() to capture
    the actual metric scores, reasons, verbose_logs, and errors.
    """

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    pricing = MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})

    results_by_id: Dict[str, Any] = {

        tr.name: tr for tr in eval_result.test_results

    }

    per_case_results = []

    for i, (tc_def, tt, trt, lat) in enumerate(

        zip(test_case_defs, token_trackers, tool_trackers, latencies)

    ):

        tc_id = tc_def["id"]

        test_result = results_by_id[tc_id]

        mcp_calls = [c for c in trt.calls if not is_orchestrator_tool(c["name"])]

        expected_tools_raw = tc_def.get("expected_tools", [])

        expected_tool_calls_raw = tc_def.get("expected_tool_calls", [])

        if expected_tools_raw and hasattr(expected_tools_raw[0], "name"):

            expected_tool_names = [t.name for t in expected_tools_raw]

            expected_params = [

                {"name": t.name, "input_parameters": t.input_parameters}

                for t in expected_tools_raw

            ]

        elif expected_tool_calls_raw:

            expected_tool_names = [t["name"] for t in expected_tool_calls_raw]

            expected_params = [

                {"name": t["name"], "input_parameters": t.get("arguments", {})}

                for t in expected_tool_calls_raw

            ]

        else:

            expected_tool_names = []

            expected_params = []

        called_tool_names = [c["name"] for c in mcp_calls]

        actual_params = [

            {"name": c["name"], "input_parameters": sanitize_args(c["args"])}

            for c in mcp_calls

        ]

        metric_comparisons = {

            "Tool Correctness": {

                "expected": expected_tool_names,

                "actual": called_tool_names,

            },

            "Argument Correctness [Reference]": {

                "expected": expected_params,

                "actual": actual_params,

            },

            "Argument Correctness": {

                "expected": expected_params,

                "actual": actual_params,

            },

            "Correctness": {

                "expected": tc_def.get("expected_output", ""),

                "actual": test_result.actual_output[:500] if test_result.actual_output else "",

            },

            "Correctness [GEval]": {

                "expected": tc_def.get("expected_output", ""),

                "actual": test_result.actual_output[:500] if test_result.actual_output else "",

            },

        }

        metrics = {}

        for md in (test_result.metrics_data or []):

            comparison = metric_comparisons.get(md.name, {})

            metrics[md.name] = {

                "score": md.score,

                "threshold": md.threshold,

                "success": md.success,

                "reason": md.reason,

                "error": md.error,

                "strict_mode": md.strict_mode,

                "evaluation_model": md.evaluation_model,

                "evaluation_cost": md.evaluation_cost,

                "verbose_logs": md.verbose_logs,

                "comparison": comparison,

            }

        expected_execution = tc_def.get("expected_execution")

        if expected_execution:

            all_tool_calls = [

                {"name": c["name"], "start_time": c.get("start_time", 0), "latency": c.get("latency", 0)}

                for c in trt.calls if not is_orchestrator_tool(c["name"])

            ]

            efficiency = calculate_efficiency(expected_execution, all_tool_calls)

            metrics["Execution Efficiency"] = {

                "score": efficiency["score"],

                "threshold": efficiency["threshold"],

                "success": efficiency["success"],

                "reason": efficiency["reason"],

                "error": None,

                "strict_mode": False,

                "evaluation_model": None,

                "evaluation_cost": None,

                "verbose_logs": None,

                "comparison": {

                    "expected_steps": expected_execution,

                    "checks": efficiency["checks"],

                    "expected_tools": efficiency.get("expected_tools", []),

                    "found_tools": efficiency.get("found_tools", []),

                    "missing_tools": efficiency.get("missing_tools", []),

                    "actual_tools_called": [c["name"] for c in all_tool_calls],

                },

            }

        per_case_results.append({

            "id": tc_id,

            "dimension": tc_def.get("dimension", ""),

            "category": tc_def.get("category", ""),

            "description": tc_def.get("description", ""),

            "input": tc_def["input"],

            "expected_output": tc_def.get("expected_output", ""),

            "actual_output": test_result.actual_output[:500] if test_result.actual_output else "",

            "expected_tools": expected_params,

            "tools_called": [

                {"name": c["name"], "input_parameters": sanitize_args(c["args"]), "start_time": c.get("start_time", 0), "latency": round(c["latency"], 3)}

                for c in mcp_calls

            ],

            "metrics": metrics,

            "tokens": {

                "prompt_tokens": tt.prompt_tokens,

                "completion_tokens": tt.completion_tokens,

                "total_tokens": tt.total_tokens,

                "llm_calls": tt.llm_calls,

                "cost": round(tt.get_cost(model_name), 6),

            },

            "latency": {

                "total": round(lat, 3),

                "llm_latencies": [round(l, 3) for l in tt.llm_latencies],

            },

        })

    total_prompt = sum(t.prompt_tokens for t in token_trackers)

    total_completion = sum(t.completion_tokens for t in token_trackers)

    total_cost = (total_prompt / 1_000_000) * pricing["input"] + (total_completion / 1_000_000) * pricing["output"]

    run_metadata = {}

    if extra_data:

        for key in ("agent_type", "mode", "category", "architecture"):

            if key in extra_data:

                run_metadata[key] = extra_data[key]

    test_case_errors: List[Dict[str, Any]] = (

        extra_data.get("test_case_errors", []) if extra_data else []

    )

    errors_by_id = {e["test_case_id"]: e for e in test_case_errors}

    for case_result in per_case_results:

        error_info = errors_by_id.get(case_result["id"])

        if error_info:

            case_result["error"] = {

                "type": error_info["error_type"],

                "message": error_info["error_message"],

                "traceback": error_info["traceback"],

            }

    errors_by_type: Dict[str, int] = {}

    for err in test_case_errors:

        errors_by_type[err["error_type"]] = errors_by_type.get(err["error_type"], 0) + 1

    errors_summary = {

        "total_errors": len(test_case_errors),

        "total_test_cases": len(test_case_defs),

        "error_rate": round(len(test_case_errors) / len(test_case_defs), 4) if test_case_defs else 0,

        "errors_by_type": errors_by_type,

        "failed_test_case_ids": [e["test_case_id"] for e in test_case_errors],

    }

    result = {

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "model": model_name,

        "num_test_cases": len(test_case_defs),

        **run_metadata,

        "errors_summary": errors_summary,

        "aggregate": {

            "total_prompt_tokens": total_prompt,

            "total_completion_tokens": total_completion,

            "total_tokens": sum(t.total_tokens for t in token_trackers),

            "total_llm_calls": sum(t.llm_calls for t in token_trackers),

            "total_cost": round(total_cost, 6),

            "total_latency": round(sum(latencies), 3),

            "avg_latency": round(sum(latencies) / len(latencies), 3),

        },

        "test_cases": per_case_results,

    }

    if extra_data:

        ma_metrics = extra_data.get("multi_agent_metrics")

        if ma_metrics and len(ma_metrics) == len(per_case_results):

            for case_result, ma_result in zip(per_case_results, ma_metrics):

                if ma_result:

                    for metric_name, metric_data in ma_result.items():

                        case_result["metrics"][metric_name] = {

                            "score": metric_data.get("score", 0),

                            "threshold": metric_data.get("threshold", 0),

                            "success": metric_data.get("success", False),

                            "reason": metric_data.get("reason", ""),

                            "error": None,

                            "strict_mode": False,

                            "evaluation_model": None,

                            "evaluation_cost": None,

                            "verbose_logs": None,

                            "comparison": metric_data.get("details", {}),

                        }

        for key in ("clarification_data", "efficiency_results"):

            if key in extra_data and extra_data[key] is not None:

                result[key] = extra_data[key]

    agent_type = extra_data.get("agent_type", "") if extra_data else ""

    mode = extra_data.get("mode", "") if extra_data else ""

    name_parts = [timestamp] + [p for p in [agent_type, mode] if p]

    benchmark = extra_data.get("benchmark") if extra_data else None

    output_dir = RESULTS_DIR / benchmark if benchmark else RESULTS_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / f"{'_'.join(name_parts)}.json"

    filepath.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nResults saved to: {filepath}")

    if test_case_errors:

        errors_filepath = output_dir / f"{'_'.join(name_parts)}_errors.json"

        errors_filepath.write_text(

            json.dumps(test_case_errors, indent=2, ensure_ascii=False),

            encoding="utf-8",

        )

        print(f"Errors saved to: {errors_filepath}")

    return filepath

