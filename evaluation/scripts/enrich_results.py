"""
Enrich Evaluation Results with Post-hoc Metrics.
Reads original result JSONs, computes missing metrics, and writes
enriched copies to a separate directory (originals remain unchanged).
Computed metrics:
- Coordination Token Overhead (requires single-agent baseline)
- Cost recalculation (if model pricing was missing during evaluation)
- 95% Confidence Intervals (Wilson for pass/fail, Standard Error for scores)
- Descriptive statistics (mean, median, std, variance, percentiles, IQR)
- Latency statistics (mean, median, p95, p99)
- Token usage statistics
Statistical methods aligned with BFCL (variance, std, percentiles) and
scientific best practices for thesis evaluation.
Usage:
    cd agenttim/evaluation
    python scripts/enrich_results.py
    python scripts/enrich_results.py --benchmark mcpagentbench
    python scripts/enrich_results.py --output results_enriched
"""
import argparse
import json
import math
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any
import numpy as np
_SCRIPT_DIR = Path(__file__).resolve().parent
_EVAL_DIR = _SCRIPT_DIR.parent
_AGENTTIM_DIR = _EVAL_DIR.parent
if str(_AGENTTIM_DIR) not in sys.path:

    sys.path.insert(0, str(_AGENTTIM_DIR))
import importlib.util
_constants_path = _EVAL_DIR / "eval_utils" / "constants.py"
_spec = importlib.util.spec_from_file_location("constants", _constants_path)
_constants_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_constants_mod)
MODEL_PRICING = _constants_mod.MODEL_PRICING
warnings.filterwarnings("ignore", category=RuntimeWarning)
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
METRIC_KEYS = [

    "Tool Correctness",

    "Argument Correctness [Reference]",

    "Execution Efficiency",

    "Final State (Derived)",

    "State Match",

    "Coordination Token Overhead",
]
def safe_float(value: Any, default: float = 0.0) -> float:

    """Safely convert value to float, handling None, NaN, Inf."""

    if value is None:

        return default

    try:

        f = float(value)

        if math.isnan(f) or math.isinf(f):

            return default

        return f

    except (ValueError, TypeError):

        return default
def safe_round(value: float, decimals: int = 4) -> float:

    """Safely round a value, handling NaN/Inf."""

    if math.isnan(value) or math.isinf(value):

        return 0.0

    return round(value, decimals)
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:

    """Wilson score confidence interval for binomial proportion.

    Recommended for pass/fail metrics as it handles edge cases (p=0, p=1)
    better than normal approximation. Used in BFCL and other benchmarks.

    Args:
        k: Number of successes (PASS)
        n: Total number of trials
        z: Z-score (1.96 for 95% CI)

    Returns:
        (lower, upper) bounds as proportions
    """

    if n <= 0 or k < 0:

        return 0.0, 0.0

    k = min(k, n)

    p = k / n

    denominator = 1 + z**2 / n

    center = (p + z**2 / (2 * n)) / denominator

    margin = (z / denominator) * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))

    return max(0.0, center - margin), min(1.0, center + margin)
def compute_descriptive_stats(values: list[float]) -> dict[str, float]:

    """Compute comprehensive descriptive statistics for a list of values.

    Aligned with BFCL statistical methods (variance, std, percentiles).

    Args:
        values: List of numeric values

    Returns:
        Dict with n, mean, median, std, variance, min, max, p25, p75, p95, p99, iqr
    """

    if not values:

        return {

            "n": 0, "mean": 0.0, "median": 0.0, "std": 0.0, "variance": 0.0,

            "min": 0.0, "max": 0.0, "p25": 0.0, "p75": 0.0, "p95": 0.0, "p99": 0.0, "iqr": 0.0,

        }

    clean_values = [safe_float(v) for v in values if safe_float(v, None) is not None]

    if not clean_values:

        return {

            "n": 0, "mean": 0.0, "median": 0.0, "std": 0.0, "variance": 0.0,

            "min": 0.0, "max": 0.0, "p25": 0.0, "p75": 0.0, "p95": 0.0, "p99": 0.0, "iqr": 0.0,

        }

    arr = np.array(clean_values)

    n = len(arr)

    mean = float(np.mean(arr))

    median = float(np.median(arr))

    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0

    variance = std ** 2

    p25 = float(np.percentile(arr, 25))

    p75 = float(np.percentile(arr, 75))

    p95 = float(np.percentile(arr, 95))

    p99 = float(np.percentile(arr, 99))

    iqr = p75 - p25

    return {

        "n": n,

        "mean": safe_round(mean),

        "median": safe_round(median),

        "std": safe_round(std),

        "variance": safe_round(variance),

        "min": safe_round(float(np.min(arr))),

        "max": safe_round(float(np.max(arr))),

        "p25": safe_round(p25),

        "p75": safe_round(p75),

        "p95": safe_round(p95),

        "p99": safe_round(p99),

        "iqr": safe_round(iqr),

    }
def score_ci(scores: list[float], z: float = 1.96) -> tuple[float, float, float, float]:

    """Standard error confidence interval for continuous scores.

    Args:
        scores: List of scores (0.0 - 1.0)
        z: Z-score (1.96 for 95% CI)

    Returns:
        (mean, std, ci_lower, ci_upper)
    """

    if not scores:

        return 0.0, 0.0, 0.0, 0.0

    clean_scores = [safe_float(s) for s in scores if safe_float(s, None) is not None]

    if not clean_scores:

        return 0.0, 0.0, 0.0, 0.0

    arr = np.array(clean_scores)

    mean = float(np.mean(arr))

    std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0

    se = std / np.sqrt(len(arr)) if len(arr) > 1 else 0.0

    return mean, std, max(0.0, mean - z * se), min(1.0, mean + z * se)
def compute_confidence_intervals(data: dict) -> dict[str, dict]:

    """Compute confidence intervals for all metrics in a result file.

    Returns:
        Dict of metric_name -> {mean, std, ci_lower, ci_upper, pass_rate, pass_ci_lower, pass_ci_upper, n, ...}
    """

    test_cases = data.get("test_cases", [])

    if not test_cases:

        return {}

    ci_results = {}

    for metric_name in METRIC_KEYS:

        scores = []

        successes = 0

        total = 0

        for tc in test_cases:

            m = tc.get("metrics", {}).get(metric_name)

            if m is None:

                continue

            s = m.get("score")

            if s is not None:

                score_val = safe_float(s, None)

                if score_val is not None:

                    scores.append(score_val)

            if m.get("success") is not None:

                total += 1

                if m["success"]:

                    successes += 1

        if not scores:

            continue

        mean, std, ci_low, ci_high = score_ci(scores)

        pass_rate = successes / total if total > 0 else 0.0

        pass_ci_low, pass_ci_high = wilson_ci(successes, total)

        desc_stats = compute_descriptive_stats(scores)

        ci_results[metric_name] = {

            "n": len(scores),

            "mean": safe_round(mean),

            "median": desc_stats["median"],

            "std": safe_round(std),

            "variance": desc_stats["variance"],

            "ci_lower": safe_round(ci_low),

            "ci_upper": safe_round(ci_high),

            "min": desc_stats["min"],

            "max": desc_stats["max"],

            "p25": desc_stats["p25"],

            "p75": desc_stats["p75"],

            "iqr": desc_stats["iqr"],

            "pass_rate": safe_round(pass_rate),

            "pass_ci_lower": safe_round(pass_ci_low),

            "pass_ci_upper": safe_round(pass_ci_high),

            "passed": successes,

            "total": total,

        }

    return ci_results
def compute_latency_statistics(data: dict) -> dict[str, Any]:

    """Compute latency statistics across all test cases.

    Aligned with BFCL which uses percentiles for latency analysis.

    Returns:
        Dict with latency statistics including percentiles
    """

    test_cases = data.get("test_cases", [])

    if not test_cases:

        return {}

    latencies = []

    for tc in test_cases:

        lat = tc.get("latency")

        if lat is not None:

            lat_val = safe_float(lat, None)

            if lat_val is not None and lat_val > 0:

                latencies.append(lat_val)

    if not latencies:

        return {}

    stats = compute_descriptive_stats(latencies)

    return {

        "latency": {

            **stats,

            "unit": "seconds",

        }

    }
def compute_token_statistics(data: dict) -> dict[str, Any]:

    """Compute token usage statistics across all test cases.

    Returns:
        Dict with token usage statistics
    """

    test_cases = data.get("test_cases", [])

    if not test_cases:

        return {}

    prompt_tokens = []

    completion_tokens = []

    total_tokens = []

    costs = []

    for tc in test_cases:

        tokens = tc.get("tokens", {})

        pt = safe_float(tokens.get("prompt_tokens"), None)

        if pt is not None:

            prompt_tokens.append(pt)

        ct = safe_float(tokens.get("completion_tokens"), None)

        if ct is not None:

            completion_tokens.append(ct)

        tt = safe_float(tokens.get("total_tokens"), None)

        if tt is not None:

            total_tokens.append(tt)

        cost = safe_float(tokens.get("cost"), None)

        if cost is not None:

            costs.append(cost)

    result = {}

    if prompt_tokens:

        result["prompt_tokens"] = compute_descriptive_stats(prompt_tokens)

    if completion_tokens:

        result["completion_tokens"] = compute_descriptive_stats(completion_tokens)

    if total_tokens:

        result["total_tokens"] = compute_descriptive_stats(total_tokens)

    if costs:

        cost_stats = compute_descriptive_stats(costs)

        cost_stats["total"] = safe_round(sum(costs), 6)

        result["cost"] = cost_stats

    return result
def load_results(

    benchmark: str | None = None,

    latest_only: bool = True,
) -> list[dict[str, Any]]:

    """Load all result JSONs from results directory."""

    results = []

    for filepath in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in filepath.name:

            continue

        try:

            data = json.loads(filepath.read_text(encoding="utf-8"))

            data["_filepath"] = str(filepath)

            data["_relative_path"] = str(filepath.relative_to(RESULTS_DIR))

            data["_benchmark"] = data.get("benchmark", "")

            if benchmark and data["_benchmark"] != benchmark:

                continue

            results.append(data)

        except (json.JSONDecodeError, OSError):

            continue

    if latest_only:

        results = _keep_latest(results)

    return results
def _keep_latest(results: list[dict]) -> list[dict]:

    """Keep only the most recent result per (model, benchmark, agent_type, mode, num_tools)."""

    latest = {}

    for r in results:

        key = (

            r.get("model", ""),

            r.get("_benchmark", ""),

            r.get("agent_type", ""),

            r.get("mode", ""),

            r.get("num_tools"),

        )

        existing = latest.get(key)

        if not existing or r.get("timestamp", "") > existing.get("timestamp", ""):

            latest[key] = r

    return list(latest.values())
def recalculate_costs(data: dict) -> tuple[int, int]:

    """Recalculate costs for all test cases if model pricing is available.

    Returns:
        (updated_count, skipped_count)
    """

    model = data.get("model", "")

    pricing = MODEL_PRICING.get(model)

    if not pricing:

        return 0, len(data.get("test_cases", []))

    updated = 0

    for tc in data.get("test_cases", []):

        tokens = tc.get("tokens", {})

        prompt = tokens.get("prompt_tokens", 0)

        completion = tokens.get("completion_tokens", 0)

        if prompt > 0 or completion > 0:

            input_cost = (prompt / 1_000_000) * pricing["input"]

            output_cost = (completion / 1_000_000) * pricing["output"]

            new_cost = input_cost + output_cost

            old_cost = tokens.get("cost", 0)

            if abs(new_cost - old_cost) > 0.000001:

                tokens["cost"] = round(new_cost, 8)

                updated += 1

    if updated > 0 and "aggregate" in data:

        total_cost = sum(

            tc.get("tokens", {}).get("cost", 0)

            for tc in data.get("test_cases", [])

        )

        data["aggregate"]["total_cost"] = round(total_cost, 6)

    return updated, len(data.get("test_cases", [])) - updated
def compute_token_overhead(

    all_results: list[dict],
) -> dict[str, dict[str, Any]]:

    """Compute Coordination Token Overhead for all multi-agent results.

    Returns:
        Dict mapping (benchmark, mode, num_tools, agent_type) -> overhead data per test case
    """

    by_config: dict[tuple, dict[str, dict]] = {}

    for data in all_results:

        model = data.get("model", "")

        benchmark = data.get("benchmark", data.get("_benchmark", ""))

        mode = data.get("mode", "")

        num_tools = data.get("num_tools")

        agent = data.get("agent_type", "")

        key = (model, benchmark, mode, num_tools)

        if key not in by_config:

            by_config[key] = {}

        by_config[key][agent] = data

    overhead_results: dict[str, dict[str, Any]] = {}

    for (model, benchmark, mode, num_tools), agents in by_config.items():

        baseline = agents.get("single") or agents.get("baseline")

        if not baseline:

            continue

        baseline_by_id = {

            tc.get("id", ""): tc.get("tokens", {}).get("total_tokens", 0)

            for tc in baseline.get("test_cases", [])

        }

        baseline_avg = np.mean(list(baseline_by_id.values())) if baseline_by_id else 0

        if baseline_avg <= 0:

            continue

        for agent_type, data in agents.items():

            if agent_type in ("single", "baseline"):

                continue

            result_key = f"{model}|{benchmark}|{mode}|{num_tools}|{agent_type}"

            overhead_results[result_key] = {

                "baseline_avg": baseline_avg,

                "per_case": {},

            }

            for tc in data.get("test_cases", []):

                tc_id = tc.get("id", "")

                tc_tokens = tc.get("tokens", {}).get("total_tokens", 0)

                baseline_tokens = baseline_by_id.get(tc_id, baseline_avg)

                if baseline_tokens > 0:

                    overhead_pct = (tc_tokens - baseline_tokens) / baseline_tokens * 100

                    score = max(0.0, min(1.0, 1.0 - overhead_pct / 300))

                else:

                    overhead_pct = 0.0

                    score = 1.0

                overhead_results[result_key]["per_case"][tc_id] = {

                    "overhead_pct": round(overhead_pct, 2),

                    "score": round(score, 4),

                    "success": score >= 0.5,

                    "agent_tokens": tc_tokens,

                    "baseline_tokens": round(baseline_tokens, 0),

                }

    return overhead_results
def apply_token_overhead(data: dict, overhead_results: dict) -> int:

    """Apply token overhead metrics to test cases.

    Returns:
        Number of test cases updated
    """

    model = data.get("model", "")

    benchmark = data.get("benchmark", data.get("_benchmark", ""))

    mode = data.get("mode", "")

    num_tools = data.get("num_tools")

    agent_type = data.get("agent_type", "")

    result_key = f"{model}|{benchmark}|{mode}|{num_tools}|{agent_type}"

    overhead_data = overhead_results.get(result_key)

    if not overhead_data:

        return 0

    updated = 0

    for tc in data.get("test_cases", []):

        tc_id = tc.get("id", "")

        case_overhead = overhead_data["per_case"].get(tc_id)

        if case_overhead:

            tc.setdefault("metrics", {})["Coordination Token Overhead"] = {

                "score": case_overhead["score"],

                "threshold": 0.5,

                "success": case_overhead["success"],

                "reason": (

                    f"Overhead: {case_overhead['overhead_pct']:.1f}% "

                    f"(MAS: {case_overhead['agent_tokens']} vs "

                    f"SAS: {case_overhead['baseline_tokens']:.0f} tokens)"

                ),

            }

            updated += 1

    return updated
def compute_token_efficiency(data: dict) -> dict[str, Any]:

    """Compute token efficiency metrics for the run.

    Metrics:
    - tokens_per_pass: Total tokens / passed tests (lower is better)
    - success_per_1k_tokens: Passed tests per 1000 tokens (higher is better)

    These metrics normalize for errors and retries, enabling fair comparison
    between models with different error rates.

    Returns:
        Dict with efficiency metrics
    """

    agg = data.get("aggregate", {})

    total_tokens = agg.get("total_tokens", 0)

    passed = agg.get("passed", 0)

    failed = agg.get("failed", 0)

    errors = agg.get("errors", 0)

    total_tests = passed + failed + errors

    result = {

        "total_tests": total_tests,

        "passed": passed,

        "failed": failed,

        "errors": errors,

        "total_tokens": total_tokens,

    }

    if passed > 0 and total_tokens > 0:

        tokens_per_pass = total_tokens / passed

        result["tokens_per_pass"] = safe_round(tokens_per_pass, 2)

    else:

        result["tokens_per_pass"] = None

    if total_tokens > 0:

        success_per_1k = (passed / total_tokens) * 1000

        result["success_per_1k_tokens"] = safe_round(success_per_1k, 4)

    else:

        result["success_per_1k_tokens"] = None

    if total_tests > 0:

        result["pass_rate"] = safe_round(passed / total_tests, 4)

    else:

        result["pass_rate"] = None

    if total_tests > 0:

        result["error_rate"] = safe_round(errors / total_tests, 4)

    else:

        result["error_rate"] = None

    return {"efficiency": result}
def enrich_and_save(

    results: list[dict],

    output_dir: Path,

    dry_run: bool = False,
) -> dict[str, int]:

    """Enrich all results and save to output directory.

    Returns:
        Statistics dict
    """

    stats = {

        "files_processed": 0,

        "files_written": 0,

        "files_failed": 0,

        "costs_recalculated": 0,

        "overhead_computed": 0,

        "confidence_intervals": 0,

        "latency_statistics": 0,

        "token_statistics": 0,

        "efficiency_computed": 0,

    }

    print("Computing Coordination Token Overhead...")

    try:

        overhead_results = compute_token_overhead(results)

        print(f"  Found baselines for {len(overhead_results)} multi-agent configurations")

    except Exception as e:

        print(f"  WARNING: Failed to compute token overhead: {e}")

        overhead_results = {}

    print(f"\nEnriching {len(results)} result files...")

    for data in results:

        stats["files_processed"] += 1

        relative_path = data.get("_relative_path", "unknown.json")

        try:

            clean_data = {k: v for k, v in data.items() if not k.startswith("_")}

            try:

                cost_updated, _ = recalculate_costs(clean_data)

                if cost_updated > 0:

                    stats["costs_recalculated"] += cost_updated

            except Exception as e:

                print(f"    WARNING: Cost recalculation failed: {e}")

                cost_updated = 0

            try:

                overhead_updated = apply_token_overhead(clean_data, overhead_results)

                if overhead_updated > 0:

                    stats["overhead_computed"] += overhead_updated

            except Exception as e:

                print(f"    WARNING: Token overhead application failed: {e}")

                overhead_updated = 0

            try:

                ci_results = compute_confidence_intervals(clean_data)

                if ci_results:

                    clean_data["confidence_intervals"] = ci_results

                    stats["confidence_intervals"] += 1

            except Exception as e:

                print(f"    WARNING: Confidence interval computation failed: {e}")

                ci_results = {}

            try:

                latency_stats = compute_latency_statistics(clean_data)

                if latency_stats:

                    clean_data.setdefault("statistics", {}).update(latency_stats)

                    stats["latency_statistics"] += 1

            except Exception as e:

                print(f"    WARNING: Latency statistics computation failed: {e}")

            try:

                token_stats = compute_token_statistics(clean_data)

                if token_stats:

                    clean_data.setdefault("statistics", {})["tokens"] = token_stats

                    stats["token_statistics"] += 1

            except Exception as e:

                print(f"    WARNING: Token statistics computation failed: {e}")

            efficiency_data = None

            try:

                efficiency_data = compute_token_efficiency(clean_data)

                if efficiency_data:

                    clean_data.setdefault("statistics", {}).update(efficiency_data)

                    stats["efficiency_computed"] += 1

            except Exception as e:

                print(f"    WARNING: Token efficiency computation failed: {e}")

            clean_data["_enriched"] = {

                "timestamp": datetime.now().isoformat(),

                "version": "2.1",

                "costs_recalculated": cost_updated,

                "overhead_computed": overhead_updated,

                "confidence_intervals_computed": len(ci_results),

                "statistics_computed": bool(clean_data.get("statistics")),

                "efficiency_computed": bool(efficiency_data),

            }

            output_path = output_dir / relative_path

            if dry_run:

                print(f"  [DRY RUN] Would write: {output_path}")

            else:

                output_path.parent.mkdir(parents=True, exist_ok=True)

                output_path.write_text(

                    json.dumps(clean_data, indent=2, ensure_ascii=False, default=str),

                    encoding="utf-8",

                )

                stats["files_written"] += 1

            agent = clean_data.get("agent_type", "?")

            mode = clean_data.get("mode", "?")

            ci_count = len(ci_results)

            has_stats = "Y" if clean_data.get("statistics") else "-"

            print(f"  [{agent}/{mode}] costs: {cost_updated}, overhead: {overhead_updated}, CIs: {ci_count}, stats: {has_stats}")

        except Exception as e:

            stats["files_failed"] += 1

            print(f"  ERROR processing {relative_path}: {e}")

    return stats
def main():

    parser = argparse.ArgumentParser(

        description="Enrich evaluation results with post-hoc metrics"

    )

    parser.add_argument(

        "--benchmark", "-b",

        help="Filter by benchmark (mcpagentbench, bfcl_multiturn)",

    )

    parser.add_argument(

        "--output", "-o", default=str(DEFAULT_OUTPUT_DIR),

        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",

    )

    parser.add_argument(

        "--all-runs", action="store_true",

        help="Process all runs, not just the latest per configuration",

    )

    parser.add_argument(

        "--dry-run", action="store_true",

        help="Show what would be done without writing files",

    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    print("=" * 60)

    print("  Enrich Evaluation Results")

    print("=" * 60)

    print(f"Source:      {RESULTS_DIR}")

    print(f"Destination: {output_dir}")

    if args.benchmark:

        print(f"Benchmark:   {args.benchmark}")

    if args.dry_run:

        print("Mode:        DRY RUN (no files will be written)")

    print()

    print("Loading results...")

    results = load_results(

        benchmark=args.benchmark,

        latest_only=not args.all_runs,

    )

    print(f"Found {len(results)} result files.")

    if not results:

        print("No results to process.")

        return

    stats = enrich_and_save(results, output_dir, dry_run=args.dry_run)

    print()

    print("=" * 60)

    print("  Summary")

    print("=" * 60)

    print(f"Files processed:      {stats['files_processed']}")

    print(f"Files written:        {stats['files_written']}")

    if stats.get("files_failed", 0) > 0:

        print(f"Files failed:         {stats['files_failed']} (see warnings above)")

    print(f"Costs recalculated:   {stats['costs_recalculated']} test cases")

    print(f"Overhead computed:    {stats['overhead_computed']} test cases")

    print(f"Confidence intervals: {stats['confidence_intervals']} files")

    print(f"Latency statistics:   {stats['latency_statistics']} files")

    print(f"Token statistics:     {stats['token_statistics']} files")

    print(f"Efficiency metrics:   {stats['efficiency_computed']} files")

    print()

    print(f"Enriched results saved to: {output_dir}")

    print()

    print("Statistics include:")

    print("  - Mean, median, std, variance (descriptive)")

    print("  - Min, max, p25, p75, p95, p99, IQR (distribution)")

    print("  - 95% CI (Wilson for pass/fail, SE for scores)")

    print("  - Latency percentiles (aligned with BFCL)")

    print("  - Token usage breakdown")

    print("  - Token Efficiency: tokens_per_pass, success_per_1k_tokens")
if __name__ == "__main__":

    main()

