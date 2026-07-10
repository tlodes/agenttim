"""
Export MCPAgentBench evaluation results to Excel.
Reads all result JSON files and produces a multi-sheet workbook:
  1. Overview        — Agent × Mode matrix with key metrics
  2. Agent Summary   — Aggregated per agent type
  3. Mode Summary    — Aggregated per benchmark mode
  4. Test Cases      — Every test case with all metrics
  5. Errors          — All errors across runs
  6. Cost & Latency  — Token usage, cost, latency breakdown
Usage:
    cd agenttim/evaluation
    python scripts/export_results_to_excel.py [--benchmark mcpagentbench] [--out results.xlsx]
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
METRIC_KEYS = [

    "Tool Correctness",

    "Argument Correctness [Reference]",

    "Execution Efficiency",

    "Final State (Derived)",

    "State Match",

    "Coordination Token Overhead",
]
def load_results(benchmark: str) -> list[dict[str, Any]]:

    """Load all non-error JSON result files for a benchmark, newest first."""

    result_dir = RESULTS_DIR / benchmark

    if not result_dir.exists():

        raise FileNotFoundError(f"No results directory: {result_dir}")

    files = sorted(

        (f for f in result_dir.glob("*.json") if not f.name.endswith("_errors.json")),

        reverse=True,

    )

    results = []

    for f in files:

        if f.parent != result_dir:

            continue

        try:

            data = json.loads(f.read_text(encoding="utf-8"))

            if isinstance(data, dict) and "test_cases" in data:

                data["_filename"] = f.name

                results.append(data)

        except (json.JSONDecodeError, KeyError):

            continue

    return results
def get_latest_per_agent_mode(results: list[dict]) -> list[dict]:

    """Keep only the newest run per (agent_type, mode) pair."""

    seen: set[str] = set()

    latest = []

    for r in results:

        key = f"{r.get('agent_type', '')}_{r.get('mode', '')}"

        if key not in seen:

            seen.add(key)

            latest.append(r)

    return latest
def extract_metric(tc: dict, metric_name: str) -> float | None:

    """Extract a metric score from a test case dict."""

    m = tc.get("metrics", {}).get(metric_name, {})

    return m.get("score")
def extract_metric_success(tc: dict, metric_name: str) -> bool | None:

    m = tc.get("metrics", {}).get(metric_name)

    if m is None:

        return None

    return m.get("success", False)
def build_overview_df(runs: list[dict]) -> pd.DataFrame:

    """Agent × Mode matrix with key metrics."""

    rows = []

    for run in runs:

        agent = run.get("agent_type", "?")

        mode = run.get("mode", "?")

        tcs = run.get("test_cases", [])

        n = len(tcs)

        agg = run.get("aggregate", {})

        errors = run.get("errors_summary", {})

        def avg_metric(name: str) -> float | None:

            scores = [extract_metric(tc, name) for tc in tcs]

            valid = [s for s in scores if s is not None]

            return round(sum(valid) / len(valid), 4) if valid else None

        def pass_count(name: str) -> int:

            return sum(1 for tc in tcs if extract_metric_success(tc, name))

        rows.append({

            "Agent": agent,

            "Mode": mode,

            "Cases": n,

            "Errors": errors.get("total_errors", 0),

            "Tool Corr. (avg)": avg_metric("Tool Correctness"),

            "Tool Corr. (pass)": f"{pass_count('Tool Correctness')}/{n}",

            "Arg Corr. (avg)": avg_metric("Argument Correctness [Reference]"),

            "Arg Corr. (pass)": f"{pass_count('Argument Correctness [Reference]')}/{n}",

            "Exec Eff. (avg)": avg_metric("Execution Efficiency"),

            "Final State (avg)": avg_metric("Final State (Derived)"),

            "Final State (pass)": f"{pass_count('Final State (Derived)')}/{n}",

            "Avg Latency (s)": agg.get("avg_latency"),

            "Total Tokens": agg.get("total_tokens"),

            "Total LLM Calls": agg.get("total_llm_calls"),

            "Total Cost ($)": agg.get("total_cost"),

        })

    df = pd.DataFrame(rows)

    df.sort_values(["Agent", "Mode"], inplace=True)

    return df
def build_agent_summary_df(runs: list[dict]) -> pd.DataFrame:

    """Aggregated metrics per agent type across all modes."""

    agent_data: dict[str, dict] = {}

    for run in runs:

        agent = run.get("agent_type", "?")

        tcs = run.get("test_cases", [])

        agg = run.get("aggregate", {})

        errors = run.get("errors_summary", {})

        if agent not in agent_data:

            agent_data[agent] = {

                "cases": 0, "errors": 0, "modes": 0,

                "tool_scores": [], "arg_scores": [], "eff_scores": [],

                "final_scores": [], "latencies": [],

                "tokens": 0, "llm_calls": 0, "cost": 0.0,

            }

        d = agent_data[agent]

        d["cases"] += len(tcs)

        d["errors"] += errors.get("total_errors", 0)

        d["modes"] += 1

        d["tokens"] += agg.get("total_tokens", 0)

        d["llm_calls"] += agg.get("total_llm_calls", 0)

        d["cost"] += agg.get("total_cost", 0)

        for tc in tcs:

            lat = tc.get("latency", {}).get("total")

            if lat is not None:

                d["latencies"].append(lat)

            for key, bucket in [

                ("Tool Correctness", "tool_scores"),

                ("Argument Correctness [Reference]", "arg_scores"),

                ("Execution Efficiency", "eff_scores"),

                ("Final State (Derived)", "final_scores"),

            ]:

                s = extract_metric(tc, key)

                if s is not None:

                    d[bucket].append(s)

    def safe_avg(lst: list) -> float | None:

        return round(sum(lst) / len(lst), 4) if lst else None

    rows = []

    for agent, d in sorted(agent_data.items()):

        n = d["cases"]

        rows.append({

            "Agent": agent,

            "Modes": d["modes"],

            "Total Cases": n,

            "Errors": d["errors"],

            "Error Rate": f"{d['errors'] / n * 100:.1f}%" if n else "0%",

            "Tool Corr. (avg)": safe_avg(d["tool_scores"]),

            "Arg Corr. (avg)": safe_avg(d["arg_scores"]),

            "Exec Eff. (avg)": safe_avg(d["eff_scores"]),

            "Final State (avg)": safe_avg(d["final_scores"]),

            "Avg Latency (s)": safe_avg(d["latencies"]),

            "Total Tokens": d["tokens"],

            "Tokens/Case": round(d["tokens"] / n) if n else 0,

            "LLM Calls": d["llm_calls"],

            "LLM Calls/Case": round(d["llm_calls"] / n, 1) if n else 0,

            "Total Cost ($)": round(d["cost"], 4),

            "Cost/Case ($)": round(d["cost"] / n, 6) if n else 0,

        })

    return pd.DataFrame(rows)
def build_mode_summary_df(runs: list[dict]) -> pd.DataFrame:

    """Aggregated metrics per mode across all agents."""

    mode_data: dict[str, dict] = {}

    for run in runs:

        mode = run.get("mode", "?")

        tcs = run.get("test_cases", [])

        if mode not in mode_data:

            mode_data[mode] = {

                "agents": set(), "cases": 0,

                "tool_scores": [], "arg_scores": [],

                "final_scores": [],

            }

        d = mode_data[mode]

        d["agents"].add(run.get("agent_type", "?"))

        d["cases"] += len(tcs)

        for tc in tcs:

            for key, bucket in [

                ("Tool Correctness", "tool_scores"),

                ("Argument Correctness [Reference]", "arg_scores"),

                ("Final State (Derived)", "final_scores"),

            ]:

                s = extract_metric(tc, key)

                if s is not None:

                    d[bucket].append(s)

    def safe_avg(lst: list) -> float | None:

        return round(sum(lst) / len(lst), 4) if lst else None

    rows = []

    for mode, d in sorted(mode_data.items()):

        rows.append({

            "Mode": mode,

            "Agents Tested": len(d["agents"]),

            "Total Cases": d["cases"],

            "Tool Corr. (avg)": safe_avg(d["tool_scores"]),

            "Arg Corr. (avg)": safe_avg(d["arg_scores"]),

            "Final State (avg)": safe_avg(d["final_scores"]),

        })

    return pd.DataFrame(rows)
def build_test_cases_df(runs: list[dict]) -> pd.DataFrame:

    """Every test case with full metric breakdown."""

    rows = []

    for run in runs:

        agent = run.get("agent_type", "?")

        mode = run.get("mode", "?")

        for tc in run.get("test_cases", []):

            tokens = tc.get("tokens", {})

            latency = tc.get("latency", {})

            expected = tc.get("expected_tools", [])

            called = tc.get("tools_called", [])

            expected_names = ", ".join(

                t.get("name", t) if isinstance(t, dict) else str(t)

                for t in expected

            )

            called_names = ", ".join(

                t.get("name", t) if isinstance(t, dict) else str(t)

                for t in called

            )

            expected_args = "; ".join(

                f"{t['name']}({t.get('arguments', t.get('input_parameters', {}))})"

                for t in expected if isinstance(t, dict) and t.get("name")

            )

            called_args = "; ".join(

                f"{t['name']}({t.get('args', t.get('input_parameters', {}))})"

                for t in called if isinstance(t, dict) and t.get("name")

            )

            row = {

                "Agent": agent,

                "Mode": mode,

                "Test Case ID": tc.get("id", ""),

                "Input": tc.get("input", "")[:200],

                "Output": (tc.get("actual_output") or "")[:200],

                "Expected Tools": expected_names,

                "Actual Tools": called_names,

                "Expected Args": expected_args,

                "Actual Args": called_args,

            }

            for metric_name in METRIC_KEYS:

                score = extract_metric(tc, metric_name)

                success = extract_metric_success(tc, metric_name)

                row[metric_name] = score

                row[f"{metric_name} (pass)"] = success

            for key in ["Tool Correctness", "Argument Correctness [Reference]"]:

                m = tc.get("metrics", {}).get(key, {})

                row[f"{key} (reason)"] = (m.get("reason") or "")[:300]

            row.update({

                "Tokens": tokens.get("total_tokens", 0),

                "LLM Calls": tokens.get("llm_calls", 0),

                "Cost ($)": tokens.get("cost", 0),

                "Latency (s)": latency.get("total", 0),

            })

            rows.append(row)

    return pd.DataFrame(rows)
def build_errors_df(runs: list[dict]) -> pd.DataFrame:

    """All test case errors across runs."""

    rows = []

    for run in runs:

        agent = run.get("agent_type", "?")

        mode = run.get("mode", "?")

        for tc in run.get("test_cases", []):

            err = tc.get("error")

            if err:

                rows.append({

                    "Agent": agent,

                    "Mode": mode,

                    "Test Case ID": tc.get("id", ""),

                    "Error Type": err.get("type", ""),

                    "Error Message": (err.get("message") or "")[:500],

                })

    for run in runs:

        agent = run.get("agent_type", "?")

        mode = run.get("mode", "?")

        for err in run.get("test_case_errors", []):

            rows.append({

                "Agent": agent,

                "Mode": mode,

                "Test Case ID": err.get("test_case_id", ""),

                "Error Type": err.get("error_type", ""),

                "Error Message": (err.get("error_message") or "")[:500],

            })

    return pd.DataFrame(rows)
def build_cost_latency_df(runs: list[dict]) -> pd.DataFrame:

    """Per-agent cost and latency breakdown."""

    rows = []

    for run in runs:

        agent = run.get("agent_type", "?")

        mode = run.get("mode", "?")

        agg = run.get("aggregate", {})

        n = run.get("num_test_cases", 0)

        rows.append({

            "Agent": agent,

            "Mode": mode,

            "Cases": n,

            "Total Tokens": agg.get("total_tokens", 0),

            "Prompt Tokens": agg.get("total_prompt_tokens", 0),

            "Completion Tokens": agg.get("total_completion_tokens", 0),

            "Tokens/Case": round(agg.get("total_tokens", 0) / n) if n else 0,

            "LLM Calls": agg.get("total_llm_calls", 0),

            "LLM Calls/Case": round(agg.get("total_llm_calls", 0) / n, 1) if n else 0,

            "Total Cost ($)": agg.get("total_cost", 0),

            "Cost/Case ($)": round(agg.get("total_cost", 0) / n, 6) if n else 0,

            "Total Latency (s)": agg.get("total_latency", 0),

            "Avg Latency (s)": agg.get("avg_latency", 0),

        })

    df = pd.DataFrame(rows)

    df.sort_values(["Agent", "Mode"], inplace=True)

    return df
def export_to_excel(

    benchmark: str,

    output_path: Path,

    latest_only: bool = True,
) -> None:

    results = load_results(benchmark)

    if not results:

        print(f"No results found for benchmark '{benchmark}'")

        return

    if latest_only:

        runs = get_latest_per_agent_mode(results)

    else:

        runs = results

    print(f"Loaded {len(runs)} runs ({len(results)} total) for '{benchmark}'")

    overview_df = build_overview_df(runs)

    agent_df = build_agent_summary_df(runs)

    mode_df = build_mode_summary_df(runs)

    test_cases_df = build_test_cases_df(runs)

    errors_df = build_errors_df(runs)

    cost_df = build_cost_latency_df(runs)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        overview_df.to_excel(writer, sheet_name="Overview", index=False)

        agent_df.to_excel(writer, sheet_name="Agent Summary", index=False)

        mode_df.to_excel(writer, sheet_name="Mode Summary", index=False)

        cost_df.to_excel(writer, sheet_name="Cost & Latency", index=False)

        test_cases_df.to_excel(writer, sheet_name="Test Cases", index=False)

        if not errors_df.empty:

            errors_df.to_excel(writer, sheet_name="Errors", index=False)

    print(f"Exported to: {output_path}")

    print(f"  Sheets: Overview, Agent Summary, Mode Summary, Cost & Latency, Test Cases"

          + (", Errors" if not errors_df.empty else ""))

    print(f"  {len(test_cases_df)} test cases across {len(agent_df)} agents and {len(mode_df)} modes")
def main():

    parser = argparse.ArgumentParser(description="Export evaluation results to Excel")

    parser.add_argument(

        "--benchmark", "-b", default="mcpagentbench",

        help="Benchmark name (subdirectory in results/). Default: mcpagentbench",

    )

    parser.add_argument(

        "--out", "-o", default=None,

        help="Output Excel file path. Default: results/{benchmark}_export.xlsx",

    )

    parser.add_argument(

        "--all-runs", action="store_true",

        help="Include all runs, not just the latest per agent/mode",

    )

    args = parser.parse_args()

    output_path = Path(args.out) if args.out else RESULTS_DIR / f"{args.benchmark}_export.xlsx"

    export_to_excel(

        benchmark=args.benchmark,

        output_path=output_path,

        latest_only=not args.all_runs,

    )
if __name__ == "__main__":

    main()

