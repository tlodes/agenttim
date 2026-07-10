"""
Post-hoc analysis script: Confidence Intervals.
Reads all result JSONs from evaluation/results/ and computes:
- 95% Wilson Confidence Intervals (for pass/fail metrics)
- Standard Error CIs (for score-based metrics)
For post-hoc metric enrichment (Token Overhead, Cost recalculation),
use scripts/enrich_results.py instead.
Usage:
    cd evaluation

    python evaluationscripts/analyze_results.py
    python evaluationscripts/analyze_results.py --benchmark bfcl_multiturn
    python evaluationscripts/analyze_results.py --benchmark mcpagentbench --agent single
    python evaluationscripts/analyze_results.py --latest    # Only most recent run per config
    python evaluationscripts/analyze_results.py --aggregate  # Aggregate across modes
"""
import argparse
import json
import math
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:

    """Wilson score confidence interval for binomial proportion.

    Args:
        k: Number of successes (PASS)
        n: Total number of trials
        z: Z-score (1.96 for 95% CI)

    Returns:
        (lower, upper) bounds as proportions
    """

    if n == 0:

        return 0.0, 0.0

    p = k / n

    denominator = 1 + z**2 / n

    center = (p + z**2 / (2 * n)) / denominator

    margin = (z / denominator) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))

    return max(0.0, center - margin), min(1.0, center + margin)
def score_ci(scores: list[float], z: float = 1.96) -> tuple[float, float, float]:

    """Standard error confidence interval for continuous scores.

    Args:
        scores: List of scores (0.0 - 1.0)
        z: Z-score (1.96 for 95% CI)

    Returns:
        (mean, lower, upper)
    """

    if not scores:

        return 0.0, 0.0, 0.0

    arr = np.array(scores)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0

    return mean, max(0.0, mean - z * se), min(1.0, mean + z * se)
def load_results(

    benchmark: str | None = None,

    agent: str | None = None,

    latest_only: bool = False,
) -> list[dict[str, Any]]:

    """Load all result JSONs, optionally filtered.

    Supports both old flat structure (results/benchmark/*.json)
    and new nested structure (results/model/benchmark/tools/*.json).
    """

    results = []

    for filepath in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in filepath.name:

            continue

        try:

            data = json.loads(filepath.read_text(encoding="utf-8"))

            data["_filepath"] = str(filepath)

            data["_benchmark"] = data.get("benchmark", filepath.parent.name)

            if benchmark and data["_benchmark"] != benchmark:

                continue

            if agent and data.get("agent_type") != agent:

                continue

            results.append(data)

        except (json.JSONDecodeError, OSError):

            continue

    if latest_only:

        results = _keep_latest(results)

    return results
def _keep_latest(results: list[dict]) -> list[dict]:

    """Keep only the most recent result per (benchmark, agent_type, mode, num_tools)."""

    latest = {}

    for r in results:

        key = (

            r.get("_benchmark", ""),

            r.get("agent_type", ""),

            r.get("mode", ""),

            r.get("num_tools"),

        )

        existing = latest.get(key)

        if not existing or r.get("timestamp", "") > existing.get("timestamp", ""):

            latest[key] = r

    return list(latest.values())
def analyze_run(data: dict) -> list[dict]:

    """Analyze one result file: compute CIs per metric."""

    test_cases = data.get("test_cases", [])

    if not test_cases:

        return []

    metric_names = set()

    for tc in test_cases:

        metric_names.update(tc.get("metrics", {}).keys())

    rows = []

    for metric_name in sorted(metric_names):

        scores = []

        successes = 0

        total = 0

        for tc in test_cases:

            m = tc.get("metrics", {}).get(metric_name)

            if m is None:

                continue

            s = m.get("score")

            if s is not None:

                scores.append(float(s))

            if m.get("success") is not None:

                total += 1

                if m["success"]:

                    successes += 1

        if not scores:

            continue

        mean, ci_low_score, ci_high_score = score_ci(scores)

        pass_rate = successes / total if total > 0 else 0.0

        ci_low_pass, ci_high_pass = wilson_ci(successes, total)

        sd = float(np.std(scores, ddof=1)) if len(scores) > 1 else 0.0

        weighted_pass = 0

        weighted_total = 0

        if metric_name == "Final State (Derived)":

            for tc in test_cases:

                m = tc.get("metrics", {}).get(metric_name)

                if m is None or m.get("success") is None:

                    continue

                num_tools = len(tc.get("expected_tools", []))

                weight = max(num_tools, 1)

                weighted_total += weight

                if m["success"]:

                    weighted_pass += weight

        weighted_pass_rate = weighted_pass / weighted_total if weighted_total > 0 else None

        rows.append({

            "benchmark": data.get("_benchmark", data.get("benchmark", "")),

            "agent_type": data.get("agent_type", ""),

            "mode": data.get("mode", ""),

            "num_tools": data.get("num_tools"),

            "n": len(scores),

            "metric": metric_name,

            "mean_score": round(mean, 4),

            "sd": round(sd, 4),

            "ci_low_score": round(ci_low_score, 4),

            "ci_high_score": round(ci_high_score, 4),

            "pass_rate": round(pass_rate, 4),

            "ci_low_pass": round(ci_low_pass, 4),

            "ci_high_pass": round(ci_high_pass, 4),

            "weighted_pass_rate": round(weighted_pass_rate, 4) if weighted_pass_rate is not None else None,

        })

    return rows
def format_ci(value: float, low: float, high: float, pct: bool = True) -> str:

    """Format a value with CI as string."""

    if pct:

        return f"{value*100:.1f}% [{low*100:.1f}-{high*100:.1f}]"

    return f"{value:.3f} [{low:.3f}-{high:.3f}]"
def print_analysis(all_rows: list[dict]) -> None:

    """Print analysis results grouped by benchmark → metric → agent."""

    if not all_rows:

        print("No results found.")

        return

    df = pd.DataFrame(all_rows)

    for benchmark, bdf in df.groupby("benchmark"):

        print(f"\n{'='*80}")

        print(f"  {benchmark}")

        print(f"{'='*80}")

        for metric, mdf in bdf.groupby("metric"):

            print(f"\n  {metric}:")

            print(f"  {'Agent':<25} {'Mode':<30} {'Tools':>5} {'n':>4}  {'Pass Rate':>22}  {'Mean (SD)':>16}  {'95% CI':>18}")

            print(f"  {'-'*25} {'-'*30} {'-'*5} {'-'*4}  {'-'*22}  {'-'*16}  {'-'*18}")

            for _, row in mdf.sort_values(["agent_type", "mode"]).iterrows():

                tools_str = str(int(row["num_tools"])) if pd.notna(row["num_tools"]) else "all"

                pass_ci = format_ci(row["pass_rate"], row["ci_low_pass"], row["ci_high_pass"])

                mean_sd = f"{row['mean_score']:.3f} ({row['sd']:.3f})"

                ci_str = f"[{row['ci_low_score']:.3f}-{row['ci_high_score']:.3f}]"

                line = (

                    f"  {row['agent_type']:<25} "

                    f"{row['mode']:<30} "

                    f"{tools_str:>5} "

                    f"{row['n']:>4}  "

                    f"{pass_ci:>22}  "

                    f"{mean_sd:>16}  "

                    f"{ci_str:>18}"

                )

                wpr = row.get("weighted_pass_rate")

                if wpr is not None:

                    line += f"  TFS={wpr*100:.1f}%"

                print(line)
def aggregate_across_modes(all_rows: list[dict]) -> list[dict]:

    """Aggregate scores across all modes per benchmark × agent × num_tools × metric.

    Collects all individual test case scores from the underlying result files
    and recomputes CIs on the combined data.
    """

    return _aggregate_from_rows(all_rows)
def _aggregate_from_rows(rows: list[dict]) -> list[dict]:

    """Aggregate rows by (benchmark, agent_type, num_tools, metric), merging modes."""

    df = pd.DataFrame(rows)

    if df.empty:

        return []

    aggregated = []

    group_cols = ["benchmark", "agent_type", "num_tools", "metric"]

    for key, group in df.groupby(group_cols, dropna=False):

        benchmark, agent_type, num_tools, metric = key

        total_n = int(group["n"].sum())

        if total_n == 0:

            continue

        weighted_mean = float((group["mean_score"] * group["n"]).sum() / total_n)

        pooled_var = float(

            (group["n"] * (group["sd"]**2 + (group["mean_score"] - weighted_mean)**2)).sum()

            / total_n

        )

        pooled_sd = math.sqrt(pooled_var) if pooled_var > 0 else 0.0

        se = pooled_sd / math.sqrt(total_n) if total_n > 1 else 0.0

        ci_low = max(0.0, weighted_mean - 1.96 * se)

        ci_high = min(1.0, weighted_mean + 1.96 * se)

        total_pass = int((group["pass_rate"] * group["n"]).sum())

        pass_rate = total_pass / total_n if total_n > 0 else 0.0

        ci_low_pass, ci_high_pass = wilson_ci(total_pass, total_n)

        modes = sorted(group["mode"].unique())

        aggregated.append({

            "benchmark": benchmark,

            "agent_type": agent_type,

            "mode": f"ALL ({len(modes)} modes)",

            "num_tools": num_tools,

            "n": total_n,

            "metric": metric,

            "mean_score": round(weighted_mean, 4),

            "sd": round(pooled_sd, 4),

            "ci_low_score": round(ci_low, 4),

            "ci_high_score": round(ci_high, 4),

            "pass_rate": round(pass_rate, 4),

            "ci_low_pass": round(ci_low_pass, 4),

            "ci_high_pass": round(ci_high_pass, 4),

        })

    return aggregated
def print_aggregate(agg_rows: list[dict]) -> None:

    """Print aggregated overview table."""

    if not agg_rows:

        print("No aggregated results.")

        return

    df = pd.DataFrame(agg_rows)

    for benchmark, bdf in df.groupby("benchmark"):

        print(f"\n{'='*80}")

        print(f"  {benchmark} — AGGREGATE (all modes combined)")

        print(f"{'='*80}")

        for metric, mdf in bdf.groupby("metric"):

            print(f"\n  {metric}:")

            print(f"  {'Agent':<25} {'Tools':>5} {'n':>5}  {'Pass Rate':>22}  {'Mean (SD)':>16}  {'95% CI':>18}")

            print(f"  {'-'*25} {'-'*5} {'-'*5}  {'-'*22}  {'-'*16}  {'-'*18}")

            for _, row in mdf.sort_values("agent_type").iterrows():

                tools_str = str(int(row["num_tools"])) if pd.notna(row["num_tools"]) else "all"

                pass_ci = format_ci(row["pass_rate"], row["ci_low_pass"], row["ci_high_pass"])

                mean_sd = f"{row['mean_score']:.3f} ({row['sd']:.3f})"

                ci_str = f"[{row['ci_low_score']:.3f}-{row['ci_high_score']:.3f}]"

                line = (

                    f"  {row['agent_type']:<25} "

                    f"{tools_str:>5} "

                    f"{row['n']:>5}  "

                    f"{pass_ci:>22}  "

                    f"{mean_sd:>16}  "

                    f"{ci_str:>18}"

                )

                wpr = row.get("weighted_pass_rate")

                if wpr is not None:

                    line += f"  TFS={wpr*100:.1f}%"

                print(line)
def save_csv(all_rows: list[dict], output_path: Path) -> None:

    """Save analysis as CSV for further processing."""

    df = pd.DataFrame(all_rows)

    df.to_csv(output_path, index=False)

    print(f"\nCSV saved to: {output_path}")
def main() -> None:

    parser = argparse.ArgumentParser(

        description="Compute 95% Confidence Intervals for evaluation results"

    )

    parser.add_argument(

        "--benchmark", "-b",

        help="Filter by benchmark (bfcl_multiturn, mcpagentbench)",

    )

    parser.add_argument(

        "--agent", "-a",

        help="Filter by agent type (single, orchestrator_fine, etc.)",

    )

    parser.add_argument(

        "--latest", action="store_true",

        help="Only analyze the most recent run per configuration",

    )

    parser.add_argument(

        "--aggregate", action="store_true",

        help="Show aggregate overview (all modes combined per agent)",

    )

    parser.add_argument(

        "--csv", type=str,

        help="Save per-mode results as CSV",

    )

    parser.add_argument(

        "--csv-aggregate", type=str,

        help="Save aggregate results as CSV",

    )

    args = parser.parse_args()

    print("Loading results...")

    results = load_results(

        benchmark=args.benchmark,

        agent=args.agent,

        latest_only=args.latest,

    )

    print(f"Found {len(results)} result files.")

    all_rows = []

    for data in results:

        all_rows.extend(analyze_run(data))

    if args.aggregate:

        agg_rows = aggregate_across_modes(all_rows)

        print_aggregate(agg_rows)

        if args.csv_aggregate:

            save_csv(agg_rows, Path(args.csv_aggregate))

    else:

        print_analysis(all_rows)

    if args.csv:

        save_csv(all_rows, Path(args.csv))
if __name__ == "__main__":

    main()

