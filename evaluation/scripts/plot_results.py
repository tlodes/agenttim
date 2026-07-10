"""
Plot Evaluation Results for Thesis.
Generates publication-ready matplotlib charts from evaluation results.
Reads from enriched results (results_enriched/) by default to use
pre-computed confidence intervals and statistics.
Usage:
    cd agenttim/evaluation
    python scripts/plot_results.py
    python scripts/plot_results.py --benchmark mcpagentbench --output plots/
    python scripts/plot_results.py --benchmark bfcl_multiturn --format pdf
    python scripts/plot_results.py --input results  # Use original results
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({

    'font.size': 11,

    'axes.titlesize': 12,

    'axes.labelsize': 11,

    'xtick.labelsize': 10,

    'ytick.labelsize': 10,

    'legend.fontsize': 10,

    'figure.titlesize': 14,

    'figure.dpi': 150,

    'savefig.dpi': 300,

    'savefig.bbox': 'tight',

    'savefig.pad_inches': 0.1,
})
ENRICHED_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
def get_default_input_dir() -> Path:

    """Return enriched dir if it exists and has files, else original results."""

    if ENRICHED_DIR.exists() and any(ENRICHED_DIR.rglob("*.json")):

        return ENRICHED_DIR

    return RESULTS_DIR
AGENT_NAMES = {

    "single": "Single Agent",

    "orchestrator_fine": "Orchestrator (Fine)",

    "orchestrator_coarse": "Orchestrator (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
METRIC_NAMES = {

    "Tool Correctness": "Tool Correctness",

    "Argument Correctness [Reference]": "Argument Correctness",

    "Execution Efficiency": "Execution Efficiency",

    "Final State (Derived)": "Final State",

    "State Match": "State Match",

    "Coordination Token Overhead": "Token Overhead",
}
AGENT_COLORS = {

    "single": "#2ecc71",

    "orchestrator_fine": "#3498db",

    "orchestrator_coarse": "#9b59b6",

    "router": "#e74c3c",

    "swarm": "#f39c12",
}
def load_results(

    benchmark: str | None = None,

    latest_only: bool = True,

    input_dir: Path | None = None,
) -> list[dict[str, Any]]:

    """Load all result JSONs from results directory.

    Args:
        benchmark: Filter by benchmark name
        latest_only: Keep only latest result per config
        input_dir: Directory to load from (default: enriched if available, else results)
    """

    if input_dir is None:

        input_dir = get_default_input_dir()

    results = []

    for filepath in sorted(input_dir.rglob("*.json")):

        if "_errors" in filepath.name:

            continue

        try:

            data = json.loads(filepath.read_text(encoding="utf-8"))

            data["_filepath"] = str(filepath)

            data["_benchmark"] = data.get("benchmark", filepath.parent.name)

            data["_is_enriched"] = "_enriched" in data

            if benchmark and data["_benchmark"] != benchmark:

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
def extract_metrics_df(results: list[dict]) -> pd.DataFrame:

    """Extract metrics into a DataFrame for plotting."""

    rows = []

    for run in results:

        agent = run.get("agent_type", "unknown")

        mode = run.get("mode", "unknown")

        num_tools = run.get("num_tools")

        benchmark = run.get("_benchmark", "unknown")

        for tc in run.get("test_cases", []):

            latency_val = tc.get("latency")

            if isinstance(latency_val, dict):

                latency_val = latency_val.get("total", 0)

            elif latency_val is None:

                latency_val = 0

            row = {

                "benchmark": benchmark,

                "agent_type": agent,

                "agent_display": AGENT_NAMES.get(agent, agent),

                "mode": mode,

                "num_tools": num_tools,

                "test_case_id": tc.get("id", ""),

                "latency": latency_val,

                "tokens": tc.get("tokens", {}).get("total_tokens", 0),

                "cost": tc.get("tokens", {}).get("cost", 0),

            }

            for metric_key, metric_display in METRIC_NAMES.items():

                m = tc.get("metrics", {}).get(metric_key, {})

                row[f"{metric_display}_score"] = m.get("score")

                row[f"{metric_display}_success"] = m.get("success")

            rows.append(row)

    return pd.DataFrame(rows)
def extract_aggregate_df(results: list[dict]) -> pd.DataFrame:

    """Extract pre-computed aggregate statistics from enriched results.

    Returns DataFrame with one row per (agent, mode, benchmark) containing
    pre-computed means, CIs, and statistics from enrich_results.py.
    """

    rows = []

    for run in results:

        agent = run.get("agent_type", "unknown")

        mode = run.get("mode", "unknown")

        num_tools = run.get("num_tools")

        benchmark = run.get("_benchmark", "unknown")

        row = {

            "benchmark": benchmark,

            "agent_type": agent,

            "agent_display": AGENT_NAMES.get(agent, agent),

            "mode": mode,

            "num_tools": num_tools,

            "is_enriched": run.get("_is_enriched", False),

        }

        ci_data = run.get("confidence_intervals", {})

        for metric_key, metric_display in METRIC_NAMES.items():

            ci = ci_data.get(metric_key, {})

            row[f"{metric_display}_mean"] = ci.get("mean")

            row[f"{metric_display}_std"] = ci.get("std")

            row[f"{metric_display}_ci_lower"] = ci.get("ci_lower")

            row[f"{metric_display}_ci_upper"] = ci.get("ci_upper")

            row[f"{metric_display}_median"] = ci.get("median")

            row[f"{metric_display}_pass_rate"] = ci.get("pass_rate")

            row[f"{metric_display}_pass_ci_lower"] = ci.get("pass_ci_lower")

            row[f"{metric_display}_pass_ci_upper"] = ci.get("pass_ci_upper")

            row[f"{metric_display}_n"] = ci.get("n")

        stats = run.get("statistics", {})

        latency_stats = stats.get("latency", {})

        row["latency_mean"] = latency_stats.get("mean")

        row["latency_std"] = latency_stats.get("std")

        row["latency_median"] = latency_stats.get("median")

        row["latency_p95"] = latency_stats.get("p95")

        row["latency_p99"] = latency_stats.get("p99")

        token_stats = stats.get("tokens", {}).get("total_tokens", {})

        row["tokens_mean"] = token_stats.get("mean")

        row["tokens_std"] = token_stats.get("std")

        cost_stats = stats.get("tokens", {}).get("cost", {})

        row["cost_mean"] = cost_stats.get("mean")

        row["cost_total"] = cost_stats.get("total")

        rows.append(row)

    return pd.DataFrame(rows)
def plot_metric_comparison(

    df: pd.DataFrame,

    metric: str,

    output_dir: Path,

    fmt: str = "png",

    agg_df: pd.DataFrame | None = None,

    use_ci: bool = True,
) -> None:

    """Bar chart comparing agents on a single metric.

    Args:
        df: Raw test case DataFrame
        metric: Metric display name
        output_dir: Output directory
        fmt: Image format
        agg_df: Pre-computed aggregate DataFrame (from enriched results)
        use_ci: Use 95% CI for error bars instead of std (requires agg_df)
    """

    score_col = f"{metric}_score"

    if score_col not in df.columns:

        return

    if agg_df is not None and use_ci and f"{metric}_mean" in agg_df.columns:

        agg = agg_df[["agent_display", "agent_type", f"{metric}_mean", f"{metric}_std",

                      f"{metric}_ci_lower", f"{metric}_ci_upper"]].dropna(subset=[f"{metric}_mean"])

        agg = agg.rename(columns={f"{metric}_mean": "mean", f"{metric}_std": "std",

                                   f"{metric}_ci_lower": "ci_lower", f"{metric}_ci_upper": "ci_upper"})

        if not agg.empty:

            agg["yerr_low"] = agg["mean"] - agg["ci_lower"]

            agg["yerr_high"] = agg["ci_upper"] - agg["mean"]

            yerr = [agg["yerr_low"].values, agg["yerr_high"].values]

            error_label = "95% CI"

        else:

            agg_df = None

    if agg_df is None or f"{metric}_mean" not in agg_df.columns:

        agg = df.groupby(["agent_display", "agent_type"])[score_col].agg(["mean", "std", "count"]).reset_index()

        agg = agg.dropna(subset=["mean"])

        yerr = agg["std"]

        error_label = "Std Dev"

    if agg.empty:

        return

    fig, ax = plt.subplots(figsize=(8, 5))

    colors = [AGENT_COLORS.get(at, "#95a5a6") for at in agg["agent_type"]]

    x = np.arange(len(agg))

    bars = ax.bar(x, agg["mean"], yerr=yerr, capsize=4, color=colors, edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)

    ax.set_xticklabels(agg["agent_display"], rotation=15, ha="right")

    ax.set_ylabel(f"Score ({error_label})")

    ax.set_title(f"{metric} by Agent Type")

    ax.set_ylim(0, 1.05)

    for bar, val in zip(bars, agg["mean"]):

        ax.annotate(f'{val:.2f}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    plt.savefig(output_dir / f"metric_{metric.lower().replace(' ', '_')}.{fmt}")

    plt.close()
def plot_all_metrics_grouped(

    df: pd.DataFrame,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Grouped bar chart with all metrics per agent."""

    metrics = [m for m in METRIC_NAMES.values() if f"{m}_score" in df.columns]

    agents = df["agent_display"].unique()

    agg_data = []

    for agent in agents:

        agent_df = df[df["agent_display"] == agent]

        for metric in metrics:

            score_col = f"{metric}_score"

            scores = agent_df[score_col].dropna()

            if len(scores) > 0:

                agg_data.append({

                    "agent": agent,

                    "metric": metric,

                    "mean": scores.mean(),

                    "std": scores.std(),

                })

    agg_df = pd.DataFrame(agg_data)

    if agg_df.empty:

        return

    fig, ax = plt.subplots(figsize=(12, 6))

    pivot = agg_df.pivot(index="metric", columns="agent", values="mean")

    pivot_std = agg_df.pivot(index="metric", columns="agent", values="std")

    x = np.arange(len(pivot.index))

    width = 0.15

    n_agents = len(pivot.columns)

    for i, agent in enumerate(pivot.columns):

        offset = (i - n_agents / 2 + 0.5) * width

        agent_type = df[df["agent_display"] == agent]["agent_type"].iloc[0] if len(df[df["agent_display"] == agent]) > 0 else "unknown"

        color = AGENT_COLORS.get(agent_type, "#95a5a6")

        bars = ax.bar(x + offset, pivot[agent], width, label=agent,

                     yerr=pivot_std[agent], capsize=2, color=color, edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)

    ax.set_xticklabels(pivot.index, rotation=20, ha="right")

    ax.set_ylabel("Score")

    ax.set_title("All Metrics by Agent Type")

    ax.set_ylim(0, 1.15)

    ax.legend(loc="upper right", ncol=2)

    plt.tight_layout()

    plt.savefig(output_dir / f"all_metrics_grouped.{fmt}")

    plt.close()
def plot_tool_scaling(

    df: pd.DataFrame,

    metric: str,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Line chart showing metric performance across different tool counts."""

    score_col = f"{metric}_score"

    if score_col not in df.columns or df["num_tools"].isna().all():

        return

    plot_df = df[df["num_tools"].notna()].copy()

    if plot_df.empty:

        return

    fig, ax = plt.subplots(figsize=(8, 5))

    for agent in plot_df["agent_display"].unique():

        agent_df = plot_df[plot_df["agent_display"] == agent]

        agg = agent_df.groupby("num_tools")[score_col].agg(["mean", "std"]).reset_index()

        agent_type = agent_df["agent_type"].iloc[0]

        color = AGENT_COLORS.get(agent_type, "#95a5a6")

        ax.errorbar(agg["num_tools"], agg["mean"], yerr=agg["std"],

                   marker="o", label=agent, color=color, capsize=3, linewidth=2, markersize=6)

    ax.set_xlabel("Number of Tools")

    ax.set_ylabel("Score")

    ax.set_title(f"{metric} vs Tool Count")

    ax.set_ylim(0, 1.05)

    ax.legend()

    plt.tight_layout()

    plt.savefig(output_dir / f"scaling_{metric.lower().replace(' ', '_')}.{fmt}")

    plt.close()
def plot_cost_performance_tradeoff(

    df: pd.DataFrame,

    metric: str,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Scatter plot of cost vs performance."""

    score_col = f"{metric}_score"

    if score_col not in df.columns:

        return

    agg = df.groupby(["agent_type", "agent_display"]).agg({

        score_col: "mean",

        "cost": "mean",

        "tokens": "mean",

    }).reset_index()

    agg = agg.dropna()

    if agg.empty:

        return

    fig, ax = plt.subplots(figsize=(8, 6))

    for _, row in agg.iterrows():

        color = AGENT_COLORS.get(row["agent_type"], "#95a5a6")

        ax.scatter(row["cost"] * 1000, row[score_col], s=150, c=color,

                  edgecolors="black", linewidth=1, zorder=3)

        ax.annotate(row["agent_display"], (row["cost"] * 1000, row[score_col]),

                   xytext=(5, 5), textcoords="offset points", fontsize=9)

    ax.set_xlabel("Cost per Test Case ($ × 1000)")

    ax.set_ylabel(f"{metric} Score")

    ax.set_title(f"Cost vs {metric} Trade-off")

    ax.set_ylim(0, 1.05)

    plt.tight_layout()

    plt.savefig(output_dir / f"tradeoff_cost_{metric.lower().replace(' ', '_')}.{fmt}")

    plt.close()
def plot_latency_comparison(

    df: pd.DataFrame,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Box plot of latency by agent type."""

    fig, ax = plt.subplots(figsize=(8, 5))

    agents = df["agent_display"].unique()

    data = [df[df["agent_display"] == a]["latency"].dropna().values for a in agents]

    bp = ax.boxplot(data, tick_labels=agents, patch_artist=True)

    for i, (patch, agent) in enumerate(zip(bp["boxes"], df.groupby("agent_display")["agent_type"].first())):

        color = AGENT_COLORS.get(agent, "#95a5a6")

        patch.set_facecolor(color)

        patch.set_alpha(0.7)

    ax.set_ylabel("Latency (seconds)")

    ax.set_title("Latency Distribution by Agent Type")

    plt.xticks(rotation=15, ha="right")

    plt.tight_layout()

    plt.savefig(output_dir / f"latency_boxplot.{fmt}")

    plt.close()
def plot_token_comparison(

    df: pd.DataFrame,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Bar chart of average tokens by agent type."""

    agg = df.groupby("agent_display")["tokens"].agg(["mean", "std"]).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))

    colors = [AGENT_COLORS.get(df[df["agent_display"] == a]["agent_type"].iloc[0], "#95a5a6")

              for a in agg["agent_display"]]

    x = np.arange(len(agg))

    bars = ax.bar(x, agg["mean"], yerr=agg["std"], capsize=4, color=colors,

                 edgecolor="black", linewidth=0.5)

    ax.set_xticks(x)

    ax.set_xticklabels(agg["agent_display"], rotation=15, ha="right")

    ax.set_ylabel("Tokens")

    ax.set_title("Average Token Usage by Agent Type")

    for bar, val in zip(bars, agg["mean"]):

        ax.annotate(f'{val:.0f}', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    plt.savefig(output_dir / f"tokens_comparison.{fmt}")

    plt.close()
def plot_heatmap_agent_mode(

    df: pd.DataFrame,

    metric: str,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Heatmap of metric scores by agent × mode."""

    score_col = f"{metric}_score"

    if score_col not in df.columns:

        return

    pivot = df.pivot_table(index="agent_display", columns="mode", values=score_col, aggfunc="mean")

    if pivot.empty or pivot.shape[0] < 2 or pivot.shape[1] < 2:

        return

    fig, ax = plt.subplots(figsize=(12, 6))

    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1,

                ax=ax, cbar_kws={"label": "Score"})

    ax.set_title(f"{metric} by Agent × Mode")

    ax.set_xlabel("Mode")

    ax.set_ylabel("Agent Type")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    plt.savefig(output_dir / f"heatmap_{metric.lower().replace(' ', '_')}.{fmt}")

    plt.close()
def plot_pass_rate_comparison(

    df: pd.DataFrame,

    output_dir: Path,

    fmt: str = "png",
) -> None:

    """Bar chart of pass rates for key metrics."""

    metrics = ["Tool Correctness", "Argument Correctness", "Final State"]

    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 5), sharey=True)

    for ax, metric in zip(axes, metrics):

        success_col = f"{metric}_success"

        if success_col not in df.columns:

            continue

        agg = df.groupby("agent_display")[success_col].mean().reset_index()

        agg.columns = ["agent", "pass_rate"]

        colors = [AGENT_COLORS.get(df[df["agent_display"] == a]["agent_type"].iloc[0], "#95a5a6")

                  for a in agg["agent"]]

        x = np.arange(len(agg))

        bars = ax.bar(x, agg["pass_rate"] * 100, color=colors, edgecolor="black", linewidth=0.5)

        ax.set_xticks(x)

        ax.set_xticklabels(agg["agent"], rotation=30, ha="right")

        ax.set_ylabel("Pass Rate (%)" if ax == axes[0] else "")

        ax.set_title(metric)

        ax.set_ylim(0, 105)

        for bar, val in zip(bars, agg["pass_rate"]):

            ax.annotate(f'{val*100:.0f}%', xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                        xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)

    plt.suptitle("Pass Rates by Agent Type", fontsize=14)

    plt.tight_layout()

    plt.savefig(output_dir / f"pass_rates.{fmt}")

    plt.close()
def generate_all_plots(

    benchmark: str | None,

    output_dir: Path,

    fmt: str = "png",

    input_dir: Path | None = None,

    use_ci: bool = True,
) -> None:

    """Generate all plots for a benchmark.

    Args:
        benchmark: Filter by benchmark name
        output_dir: Output directory for plots
        fmt: Image format (png, pdf, svg)
        input_dir: Input directory (default: enriched if available, else results)
        use_ci: Use 95% CI for error bars (requires enriched results)
    """

    if input_dir is None:

        input_dir = get_default_input_dir()

    print(f"Loading results from: {input_dir}")

    if benchmark:

        print(f"Filtering by benchmark: {benchmark}")

    results = load_results(benchmark=benchmark, latest_only=True, input_dir=input_dir)

    if not results:

        print("No results found.")

        return

    print(f"Loaded {len(results)} result files.")

    enriched_count = sum(1 for r in results if r.get("_is_enriched", False))

    if enriched_count > 0:

        print(f"  ({enriched_count} enriched with pre-computed statistics)")

    df = extract_metrics_df(results)

    print(f"Extracted {len(df)} test cases.")

    agg_df = extract_aggregate_df(results)

    print(f"Extracted {len(agg_df)} aggregate entries.")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating plots...")

    for metric in METRIC_NAMES.values():

        plot_metric_comparison(df, metric, output_dir, fmt, agg_df=agg_df, use_ci=use_ci)

        plot_tool_scaling(df, metric, output_dir, fmt)

        plot_cost_performance_tradeoff(df, metric, output_dir, fmt)

        plot_heatmap_agent_mode(df, metric, output_dir, fmt)

    plot_all_metrics_grouped(df, output_dir, fmt)

    plot_latency_comparison(df, output_dir, fmt)

    plot_token_comparison(df, output_dir, fmt)

    plot_pass_rate_comparison(df, output_dir, fmt)

    print(f"Plots saved to: {output_dir}")

    if use_ci and enriched_count > 0:

        print("  (Using 95% CI error bars from enriched statistics)")
def main():

    parser = argparse.ArgumentParser(

        description="Generate plots from evaluation results",

        epilog="By default, reads from results_enriched/ if available (for pre-computed CIs).",

    )

    parser.add_argument(

        "--benchmark", "-b",

        help="Filter by benchmark (mcpagentbench, bfcl_multiturn)",

    )

    parser.add_argument(

        "--output", "-o", default="plots",

        help="Output directory for plots (default: plots/)",

    )

    parser.add_argument(

        "--input", "-i",

        help="Input directory (default: results_enriched if exists, else results)",

    )

    parser.add_argument(

        "--format", "-f", default="png", choices=["png", "pdf", "svg"],

        help="Output format (default: png)",

    )

    parser.add_argument(

        "--no-ci", action="store_true",

        help="Use std instead of 95%% CI for error bars",

    )

    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.benchmark:

        output_dir = output_dir / args.benchmark

    input_dir = Path(args.input) if args.input else None

    generate_all_plots(

        benchmark=args.benchmark,

        output_dir=output_dir,

        fmt=args.format,

        input_dir=input_dir,

        use_ci=not args.no_ci,

    )
if __name__ == "__main__":

    main()

