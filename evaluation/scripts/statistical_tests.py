"""
statistical_tests.py
Runs pairwise Wilcoxon signed-rank tests and Cliff's Delta effect sizes
across all configurations of models, benchmarks, tool counts, and
architecture pairs for the JUNE agenttim evaluation.
Also runs scaling degradation tests that compare the same architecture
at t=10 vs t=80 to detect significant performance changes with tool count.
Usage:
    python statistical_tests.py [--input DIR] [--output DIR]
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any
import numpy as np
from scipy import stats
ARCHITECTURES = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
MODELS = ["gpt-5.4-mini", "deepseek/deepseek-v4-pro", "june-gpt-5-4-datazone"]
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
TOOL_COUNTS = [10, 20, 40, 80]
METRICS = ["Tool Correctness", "Argument Correctness [Reference]"]
ALPHA = 0.05
MODEL_DIR_MAP = {

    "gpt-5.4-mini": "gpt-5.4-mini",

    "deepseek/deepseek-v4-pro": "deepseek/deepseek-v4-pro",

    "june-gpt-5-4-datazone": "june-gpt-5-4-datazone",
}
CLIFFS_NEGLIGIBLE = 0.147
CLIFFS_SMALL = 0.33
CLIFFS_MEDIUM = 0.474
def _model_dir(base_dir: Path, model: str) -> Path:

    """Return the directory that holds a model's benchmark results."""

    if model == "gpt-5.4-mini":

        return base_dir / "gpt-5.4-mini"

    if model == "deepseek/deepseek-v4-pro":

        return base_dir / "deepseek" / "deepseek-v4-pro"

    if model == "june-gpt-5-4-datazone":

        return base_dir / "june-gpt-5-4-datazone"

    raise ValueError(f"Unknown model: {model}")
def load_run_files(base_dir: Path, model: str, benchmark: str, num_tools: int) -> list[dict]:

    """Load all JSON run files for a specific (model, benchmark, num_tools) combination."""

    tool_dir = _model_dir(base_dir, model) / benchmark / f"t{num_tools}"

    if not tool_dir.exists():

        return []

    runs: list[dict] = []

    for json_file in sorted(tool_dir.glob("*.json")):

        try:

            with open(json_file, encoding="utf-8") as f:

                data = json.load(f)

            runs.append(data)

        except (json.JSONDecodeError, OSError) as exc:

            print(f"  Warning: could not read {json_file}: {exc}", file=sys.stderr)

    return runs
def extract_arch_from_filename(filename: str) -> str | None:

    """
    Extract architecture name from a filename like:
      20260618_130212_single_sturn-1t-daytasks.json
      20260625_104608_single_base.json
    Returns the arch token (e.g. 'single', 'orchestrator_fine', 'swarm', …).
    """

    stem = Path(filename).stem

    parts = stem.split("_", 2)

    if len(parts) < 3:

        return None

    rest = parts[2]

    for arch in ARCHITECTURES:

        if rest.startswith(arch):

            return arch

    return None
def group_runs_by_arch_mode(runs: list[dict]) -> dict[str, dict[str, dict]]:

    """
    Organise runs into {arch: {mode: run_data}} using the 'agent_type' and
    'mode' fields stored in the JSON itself (fall back to filename parsing for
    the arch when the field is missing).
    """

    arch_mode: dict[str, dict[str, dict]] = {}

    for run in runs:

        arch = run.get("agent_type") or extract_arch_from_filename(

            run.get("_source_file", "")

        )

        if arch is None:

            continue

        mode = run.get("mode", "unknown")

        arch_mode.setdefault(arch, {})[mode] = run

    return arch_mode
def load_all_arch_modes(base_dir: Path, model: str, benchmark: str, num_tools: int) -> dict[str, dict[str, dict]]:

    """
    Load and group every run for a configuration into {arch: {mode: run_data}}.
    Stores the source filename in each run for debugging.
    """

    tool_dir = _model_dir(base_dir, model) / benchmark / f"t{num_tools}"

    if not tool_dir.exists():

        return {}

    arch_mode: dict[str, dict[str, dict]] = {}

    for json_file in sorted(tool_dir.glob("*.json")):

        try:

            with open(json_file, encoding="utf-8") as f:

                data = json.load(f)

        except (json.JSONDecodeError, OSError) as exc:

            print(f"  Warning: could not read {json_file}: {exc}", file=sys.stderr)

            continue

        data["_source_file"] = json_file.name

        arch = data.get("agent_type") or extract_arch_from_filename(json_file.name)

        if arch is None:

            continue

        mode = data.get("mode", "unknown")

        arch_mode.setdefault(arch, {})[mode] = data

    return arch_mode
def collect_paired_scores(

    arch_mode_a: dict[str, dict],

    arch_mode_b: dict[str, dict],

    metric: str,
) -> tuple[list[float], list[float]]:

    """
    For each mode that both architectures have data for, match test cases by
    their 'id' field and collect the metric scores.  Returns (scores_a, scores_b).
    """

    shared_modes = set(arch_mode_a.keys()) & set(arch_mode_b.keys())

    scores_a: list[float] = []

    scores_b: list[float] = []

    for mode in sorted(shared_modes):

        run_a = arch_mode_a[mode]

        run_b = arch_mode_b[mode]

        cases_a: dict[str, float] = _index_cases(run_a, metric)

        cases_b: dict[str, float] = _index_cases(run_b, metric)

        shared_ids = set(cases_a.keys()) & set(cases_b.keys())

        for case_id in sorted(shared_ids):

            scores_a.append(cases_a[case_id])

            scores_b.append(cases_b[case_id])

    return scores_a, scores_b
def _index_cases(run: dict, metric: str) -> dict[str, float]:

    """Return {case_id: metric_score} for all test cases that have the metric."""

    result: dict[str, float] = {}

    for case in run.get("test_cases", []):

        case_id = case.get("id")

        if case_id is None:

            continue

        metric_data = case.get("metrics", {}).get(metric)

        if metric_data is None:

            continue

        score = metric_data.get("score")

        if score is None:

            continue

        result[case_id] = float(score)

    return result
def wilcoxon_test(scores_a: list[float], scores_b: list[float]) -> tuple[float | None, float]:

    """
    Run a two-sided Wilcoxon signed-rank test.
    Returns (statistic, p_value).  If all differences are zero, returns (None, 1.0).
    """

    diffs = [a - b for a, b in zip(scores_a, scores_b)]

    if all(d == 0 for d in diffs):

        return None, 1.0

    if len(diffs) < 2:

        return None, 1.0

    stat, p = stats.wilcoxon(scores_a, scores_b, alternative="two-sided")

    return float(stat), float(p)
def cliffs_delta(scores_a: list[float], scores_b: list[float]) -> float:

    """
    Cliff's Delta: (#{a > b} - #{a < b}) / n
    Values range from -1 to +1.
    """

    n = len(scores_a)

    if n == 0:

        return 0.0

    greater = sum(1 for a, b in zip(scores_a, scores_b) if a > b)

    lesser = sum(1 for a, b in zip(scores_a, scores_b) if a < b)

    return (greater - lesser) / n
def effect_size_label(delta: float) -> str:

    """Map |Cliff's delta| to a descriptive label."""

    abs_d = abs(delta)

    if abs_d < CLIFFS_NEGLIGIBLE:

        return "negligible"

    if abs_d < CLIFFS_SMALL:

        return "small"

    if abs_d < CLIFFS_MEDIUM:

        return "medium"

    return "large"
def run_all_tests(base_dir: Path) -> list[dict[str, Any]]:

    """
    Iterate over every (model, benchmark, num_tools, metric, arch_a, arch_b)
    combination and collect raw results (without Bonferroni correction yet).
    """

    raw_results: list[dict[str, Any]] = []

    arch_pairs = list(combinations(ARCHITECTURES, 2))

    for model in MODELS:

        for benchmark in BENCHMARKS:

            for num_tools in TOOL_COUNTS:

                arch_mode = load_all_arch_modes(base_dir, model, benchmark, num_tools)

                if not arch_mode:

                    continue

                for metric in METRICS:

                    for arch_a, arch_b in arch_pairs:

                        data_a = arch_mode.get(arch_a, {})

                        data_b = arch_mode.get(arch_b, {})

                        if not data_a or not data_b:

                            continue

                        scores_a, scores_b = collect_paired_scores(data_a, data_b, metric)

                        if len(scores_a) == 0:

                            continue

                        stat, p = wilcoxon_test(scores_a, scores_b)

                        delta = cliffs_delta(scores_a, scores_b)

                        mean_a = float(np.mean(scores_a))

                        mean_b = float(np.mean(scores_b))

                        raw_results.append(

                            {

                                "model": model,

                                "benchmark": benchmark,

                                "num_tools": num_tools,

                                "metric": metric,

                                "arch_a": arch_a,

                                "arch_b": arch_b,

                                "n_paired": len(scores_a),

                                "mean_a": round(mean_a, 4),

                                "mean_b": round(mean_b, 4),

                                "mean_diff": round(mean_a - mean_b, 4),

                                "wilcoxon_stat": stat,

                                "p_value": round(p, 6),

                                "significant_nominal": p < ALPHA,

                                "significant_bonferroni": False,

                                "cliffs_delta": round(delta, 4),

                                "effect_size_label": effect_size_label(delta),

                            }

                        )

    return raw_results
def apply_bonferroni(results: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, float]:

    """Apply Bonferroni correction and return (updated_results, n_tests, corrected_alpha)."""

    n_tests = len(results)

    corrected_alpha = ALPHA / n_tests if n_tests > 0 else ALPHA

    for r in results:

        r["significant_bonferroni"] = r["p_value"] < corrected_alpha

    return results, n_tests, corrected_alpha
SCALING_METRIC = "Tool Correctness"
SCALING_T_LOW = 10
SCALING_T_HIGH = 80
def collect_scaling_paired_scores(

    arch_mode_low: dict[str, dict],

    arch_mode_high: dict[str, dict],

    metric: str,
) -> tuple[list[float], list[float]]:

    """
    For each mode that exists in both t=10 and t=80 data for a given architecture,
    match test cases by their 'id' field and collect metric scores.
    Returns (scores_t10, scores_t80).
    """

    shared_modes = set(arch_mode_low.keys()) & set(arch_mode_high.keys())

    scores_low: list[float] = []

    scores_high: list[float] = []

    for mode in sorted(shared_modes):

        run_low = arch_mode_low[mode]

        run_high = arch_mode_high[mode]

        cases_low = _index_cases(run_low, metric)

        cases_high = _index_cases(run_high, metric)

        shared_ids = set(cases_low.keys()) & set(cases_high.keys())

        for case_id in sorted(shared_ids):

            scores_low.append(cases_low[case_id])

            scores_high.append(cases_high[case_id])

    return scores_low, scores_high
def run_scaling_tests(base_dir: Path) -> list[dict[str, Any]]:

    """
    For each (model, benchmark, architecture), compare the same architecture
    at t=10 vs t=80 using Wilcoxon signed-rank test and Cliff's Delta.
    Metric: Tool Correctness only.
    Returns raw results (without Bonferroni correction).
    """

    raw_results: list[dict[str, Any]] = []

    for model in MODELS:

        for benchmark in BENCHMARKS:

            arch_mode_low = load_all_arch_modes(base_dir, model, benchmark, SCALING_T_LOW)

            arch_mode_high = load_all_arch_modes(base_dir, model, benchmark, SCALING_T_HIGH)

            if not arch_mode_low or not arch_mode_high:

                continue

            for arch in ARCHITECTURES:

                data_low = arch_mode_low.get(arch, {})

                data_high = arch_mode_high.get(arch, {})

                if not data_low or not data_high:

                    continue

                scores_low, scores_high = collect_scaling_paired_scores(

                    data_low, data_high, SCALING_METRIC

                )

                if len(scores_low) == 0:

                    continue

                stat, p = wilcoxon_test(scores_low, scores_high)

                delta = cliffs_delta(scores_low, scores_high)

                mean_low = float(np.mean(scores_low))

                mean_high = float(np.mean(scores_high))

                raw_results.append(

                    {

                        "model": model,

                        "benchmark": benchmark,

                        "architecture": arch,

                        "metric": SCALING_METRIC,

                        "t_low": SCALING_T_LOW,

                        "t_high": SCALING_T_HIGH,

                        "n_paired": len(scores_low),

                        "mean_t10": round(mean_low, 4),

                        "mean_t80": round(mean_high, 4),

                        "mean_diff": round(mean_low - mean_high, 4),

                        "wilcoxon_stat": stat,

                        "p_value": round(p, 6),

                        "significant_nominal": p < ALPHA,

                        "significant_bonferroni": False,

                        "cliffs_delta": round(delta, 4),

                        "effect_size_label": effect_size_label(delta),

                    }

                )

    return raw_results
def apply_bonferroni_scaling(

    results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, float]:

    """Apply Bonferroni correction to scaling results."""

    n_tests = len(results)

    corrected_alpha = ALPHA / n_tests if n_tests > 0 else ALPHA

    for r in results:

        r["significant_bonferroni"] = r["p_value"] < corrected_alpha

    return results, n_tests, corrected_alpha
def _sig_stars(p: float, corrected_alpha: float) -> str:

    if p < 0.001:

        return "***"

    if p < 0.01:

        return "**"

    if p < ALPHA:

        return "*"

    return "ns"
def build_json_output(

    results: list[dict[str, Any]],

    bonferroni_n: int,

    corrected_alpha: float,

    scaling_results: list[dict[str, Any]] | None = None,

    scaling_bonferroni_n: int = 0,

    scaling_corrected_alpha: float = ALPHA,
) -> dict[str, Any]:

    output: dict[str, Any] = {

        "metadata": {

            "timestamp": datetime.now(timezone.utc).isoformat(),

            "bonferroni_n": bonferroni_n,

            "alpha": ALPHA,

            "corrected_alpha": corrected_alpha,

        },

        "results": results,

    }

    if scaling_results is not None:

        output["scaling_metadata"] = {

            "bonferroni_n": scaling_bonferroni_n,

            "alpha": ALPHA,

            "corrected_alpha": scaling_corrected_alpha,

            "metric": SCALING_METRIC,

            "t_low": SCALING_T_LOW,

            "t_high": SCALING_T_HIGH,

        }

        output["scaling_results"] = scaling_results

    return output
def build_markdown_summary(

    results: list[dict[str, Any]],

    bonferroni_n: int,

    corrected_alpha: float,

    scaling_results: list[dict[str, Any]] | None = None,

    scaling_bonferroni_n: int = 0,

    scaling_corrected_alpha: float = ALPHA,
) -> str:

    lines: list[str] = []

    lines.append("# Statistical Tests: Pairwise Wilcoxon + Cliff's Delta\n")

    lines.append(

        f"**Bonferroni correction**: {bonferroni_n} tests performed, "

        f"corrected α = {corrected_alpha:.6f}\n"

    )

    for model in MODELS:

        lines.append(f"\n## Model: {model}\n")

        for benchmark in BENCHMARKS:

            lines.append(f"\n### Benchmark: {benchmark}\n")

            relevant = [

                r for r in results if r["model"] == model and r["benchmark"] == benchmark

            ]

            if not relevant:

                lines.append("_No data_\n")

                continue

            lines.append(

                "| Tools | Metric | Arch A | Arch B | N | Mean A | Mean B | "

                "p-value | Sig | Cliff's δ | Effect |\n"

            )

            lines.append(

                "|------:|--------|--------|--------|--:|-------:|-------:|"

                "--------:|-----|----------:|--------|\n"

            )

            sort_key = lambda r: (r["num_tools"], r["metric"], r["arch_a"], r["arch_b"])

            for r in sorted(relevant, key=sort_key):

                stars = _sig_stars(r["p_value"], corrected_alpha)

                p_str = f"{r['p_value']:.4f}" if r["p_value"] < 0.9999 else "1.0"

                lines.append(

                    f"| {r['num_tools']} | {r['metric']} | {r['arch_a']} | {r['arch_b']} "

                    f"| {r['n_paired']} | {r['mean_a']:.3f} | {r['mean_b']:.3f} "

                    f"| {p_str} | {stars} | {r['cliffs_delta']:.3f} | {r['effect_size_label']} |\n"

                )

    if scaling_results is not None:

        lines.append("\n\n## Scaling Degradation Tests (t=10 vs t=80)\n\n")

        lines.append(

            f"**Metric**: {SCALING_METRIC} | "

            f"**Bonferroni correction**: {scaling_bonferroni_n} tests performed, "

            f"corrected α = {scaling_corrected_alpha:.6f}\n"

        )

        lines.append(

            "\nFor each architecture, test cases are paired by ID across t=10 and t=80. "

            "Cliff's δ > 0 indicates higher scores at t=10 (degradation at t=80).\n"

        )

        for model in MODELS:

            lines.append(f"\n### Model: {model}\n")

            for benchmark in BENCHMARKS:

                relevant_scaling = [

                    r for r in scaling_results

                    if r["model"] == model and r["benchmark"] == benchmark

                ]

                if not relevant_scaling:

                    continue

                lines.append(f"\n#### Benchmark: {benchmark}\n\n")

                lines.append(

                    "| Architecture | N | Mean t=10 | Mean t=80 | Δ mean | "

                    "p-value | Sig | Cliff's δ | Effect |\n"

                )

                lines.append(

                    "|--------------|--:|----------:|----------:|-------:|"

                    "--------:|-----|----------:|--------|\n"

                )

                sort_key_s = lambda r: r["architecture"]

                for r in sorted(relevant_scaling, key=sort_key_s):

                    stars = _sig_stars(r["p_value"], scaling_corrected_alpha)

                    p_str = f"{r['p_value']:.4f}" if r["p_value"] < 0.9999 else "1.0"

                    lines.append(

                        f"| {r['architecture']} | {r['n_paired']} "

                        f"| {r['mean_t10']:.3f} | {r['mean_t80']:.3f} "

                        f"| {r['mean_diff']:+.3f} | {p_str} | {stars} "

                        f"| {r['cliffs_delta']:.3f} | {r['effect_size_label']} |\n"

                    )

    return "".join(lines)
def print_console_summary(

    results: list[dict[str, Any]],

    bonferroni_n: int,

    corrected_alpha: float,
) -> None:

    print(f"\n{'='*80}")

    print("STATISTICAL TESTS SUMMARY")

    print(f"{'='*80}")

    print(f"Total tests performed : {bonferroni_n}")

    print(f"Nominal alpha         : {ALPHA}")

    print(f"Corrected alpha (Bonf): {corrected_alpha:.6f}")

    print()

    header = (

        f"{'Model':<25} {'Bench':<15} {'T':>3} {'Metric':<35} "

        f"{'A':<20} {'B':<20} {'N':>5} "

        f"{'d_mean':>7} {'p-val':>8} {'Sig':<4} {'delta':>7} {'Effect'}"

    )

    print(header)

    print("-" * len(header))

    sort_key = lambda r: (r["model"], r["benchmark"], r["num_tools"], r["metric"], r["arch_a"])

    for r in sorted(results, key=sort_key):

        stars = _sig_stars(r["p_value"], corrected_alpha)

        p_str = f"{r['p_value']:.4f}"

        print(

            f"{r['model']:<25} {r['benchmark']:<15} {r['num_tools']:>3} "

            f"{r['metric']:<35} {r['arch_a']:<20} {r['arch_b']:<20} "

            f"{r['n_paired']:>5} {r['mean_diff']:>+7.3f} {p_str:>8} {stars:<4} "

            f"{r['cliffs_delta']:>+7.3f} {r['effect_size_label']}"

        )

    sig_nom = sum(1 for r in results if r["significant_nominal"])

    sig_bon = sum(1 for r in results if r["significant_bonferroni"])

    print(f"\nSignificant (nominal p < {ALPHA}): {sig_nom}/{bonferroni_n}")

    print(f"Significant (Bonferroni)       : {sig_bon}/{bonferroni_n}")

    print(f"{'='*80}\n")
def print_scaling_console_summary(

    scaling_results: list[dict[str, Any]],

    scaling_bonferroni_n: int,

    scaling_corrected_alpha: float,
) -> None:

    print(f"\n{'='*80}")

    print(f"SCALING DEGRADATION TESTS (t={SCALING_T_LOW} vs t={SCALING_T_HIGH})")

    print(f"{'='*80}")

    print(f"Metric                : {SCALING_METRIC}")

    print(f"Total tests performed : {scaling_bonferroni_n}")

    print(f"Nominal alpha         : {ALPHA}")

    print(f"Corrected alpha (Bonf): {scaling_corrected_alpha:.6f}")

    print()

    header = (

        f"{'Model':<25} {'Bench':<15} {'Architecture':<22} {'N':>5} "

        f"{'t10':>7} {'t80':>7} {'diff':>7} {'p-val':>8} {'Sig':<4} "

        f"{'delta':>7} {'Effect'}"

    )

    print(header)

    print("-" * len(header))

    sort_key = lambda r: (r["model"], r["benchmark"], r["architecture"])

    for r in sorted(scaling_results, key=sort_key):

        stars = _sig_stars(r["p_value"], scaling_corrected_alpha)

        p_str = f"{r['p_value']:.4f}"

        print(

            f"{r['model']:<25} {r['benchmark']:<15} {r['architecture']:<22} "

            f"{r['n_paired']:>5} {r['mean_t10']:>7.3f} {r['mean_t80']:>7.3f} "

            f"{r['mean_diff']:>+7.3f} {p_str:>8} {stars:<4} "

            f"{r['cliffs_delta']:>+7.3f} {r['effect_size_label']}"

        )

    sig_nom = sum(1 for r in scaling_results if r["significant_nominal"])

    sig_bon = sum(1 for r in scaling_results if r["significant_bonferroni"])

    print(f"\nSignificant (nominal p < {ALPHA}): {sig_nom}/{scaling_bonferroni_n}")

    print(f"Significant (Bonferroni)       : {sig_bon}/{scaling_bonferroni_n}")

    print(f"{'='*80}\n")
def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(

        description="Run pairwise Wilcoxon + Cliff's Delta tests across evaluation configurations."

    )

    parser.add_argument(

        "--input",

        type=Path,

        default=None,

        help="Path to results_enriched directory (default: sibling of this script's parent).",

    )

    parser.add_argument(

        "--output",

        type=Path,

        default=None,

        help="Path to output directory for JSON and MD files (default: ../results relative to this script).",

    )

    return parser.parse_args()
def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:

    script_dir = Path(__file__).resolve().parent

    eval_dir = script_dir.parent

    input_dir = args.input if args.input else eval_dir / "results_enriched"

    output_dir = args.output if args.output else eval_dir / "results"

    return input_dir, output_dir
def main() -> None:

    args = parse_args()

    input_dir, output_dir = resolve_paths(args)

    print(f"Input directory : {input_dir}")

    print(f"Output directory: {output_dir}")

    if not input_dir.exists():

        print(f"ERROR: Input directory does not exist: {input_dir}", file=sys.stderr)

        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nLoading data and running pairwise architecture tests …")

    raw_results = run_all_tests(input_dir)

    if not raw_results:

        print("No results found. Check that the input directory has the expected structure.")

        sys.exit(1)

    results, bonferroni_n, corrected_alpha = apply_bonferroni(raw_results)

    print_console_summary(results, bonferroni_n, corrected_alpha)

    print(f"Running scaling degradation tests (t={SCALING_T_LOW} vs t={SCALING_T_HIGH}) …")

    raw_scaling_results = run_scaling_tests(input_dir)

    scaling_results: list[dict[str, Any]] = []

    scaling_bonferroni_n = 0

    scaling_corrected_alpha = ALPHA

    if raw_scaling_results:

        scaling_results, scaling_bonferroni_n, scaling_corrected_alpha = apply_bonferroni_scaling(

            raw_scaling_results

        )

        print_scaling_console_summary(scaling_results, scaling_bonferroni_n, scaling_corrected_alpha)

    else:

        print("No scaling results found.")

    json_path = output_dir / "statistical_tests.json"

    json_data = build_json_output(

        results,

        bonferroni_n,

        corrected_alpha,

        scaling_results if scaling_results else None,

        scaling_bonferroni_n,

        scaling_corrected_alpha,

    )

    with open(json_path, "w", encoding="utf-8") as f:

        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"JSON saved : {json_path}")

    md_path = output_dir / "statistical_tests.md"

    md_text = build_markdown_summary(

        results,

        bonferroni_n,

        corrected_alpha,

        scaling_results if scaling_results else None,

        scaling_bonferroni_n,

        scaling_corrected_alpha,

    )

    with open(md_path, "w", encoding="utf-8") as f:

        f.write(md_text)

    print(f"Markdown saved: {md_path}")
if __name__ == "__main__":

    main()

