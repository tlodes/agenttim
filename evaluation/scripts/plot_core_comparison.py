"""
Plot Core Comparison: Tool Correctness & Argument Correctness.
Generates publication-ready bar charts comparing MAS vs SAS architectures
for the two primary metrics.
Usage:
    cd agenttim/evaluation
    python scripts/plot_core_comparison.py
    python scripts/plot_core_comparison.py --benchmark bfcl_multiturn --tools t10
    python scripts/plot_core_comparison.py --model gpt-5.4-mini
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({

    'font.size': 11,

    'axes.titlesize': 13,

    'axes.labelsize': 12,

    'xtick.labelsize': 10,

    'ytick.labelsize': 10,

    'legend.fontsize': 10,

    'figure.titlesize': 14,

    'figure.dpi': 150,

    'savefig.dpi': 300,

    'savefig.bbox': 'tight',

    'savefig.pad_inches': 0.1,
})
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "plots"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent",

    "orchestrator_fine": "Orch. (Fine)",

    "orchestrator_coarse": "Orch. (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
METRIC_COLORS = {

    "Tool Correctness": "#3498db",

    "Argument Correctness [Reference]": "#e74c3c",
}
def load_results(

    model: str | None = None,

    benchmark: str | None = None,

    tools: str | None = None,

    mode: str | None = None,
) -> list[dict[str, Any]]:

    """Load enriched results with optional filters."""

    results = []

    for filepath in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in filepath.name:

            continue

        try:

            data = json.loads(filepath.read_text(encoding="utf-8"))

            if model and model not in str(filepath):

                continue

            if benchmark and data.get("benchmark", "") != benchmark:

                continue

            if tools:

                num_tools = data.get("num_tools")

                if num_tools is None or f"t{num_tools}" != tools:

                    continue

            if mode and data.get("mode", "") != mode:

                continue

            data["_filepath"] = str(filepath)

            results.append(data)

        except (json.JSONDecodeError, OSError):

            continue

    return results
def extract_metrics(results: list[dict]) -> dict[str, dict[str, dict]]:

    """Extract Tool Correctness and Argument Correctness per agent type.

    Returns:
        Dict[agent_type, Dict[metric_name, {mean, ci_lower, ci_upper, n}]]
    """

    by_agent: dict[str, list[dict]] = {}

    for r in results:

        agent = r.get("agent_type", "unknown")

        if agent not in by_agent:

            by_agent[agent] = []

        by_agent[agent].append(r)

    metrics_by_agent = {}

    for agent, agent_results in by_agent.items():

        metrics_by_agent[agent] = {}

        for metric_name in ["Tool Correctness", "Argument Correctness [Reference]"]:

            all_means = []

            all_n = []

            for r in agent_results:

                ci = r.get("confidence_intervals", {}).get(metric_name, {})

                if ci.get("mean") is not None:

                    all_means.append(ci["mean"])

                    all_n.append(ci.get("n", 0))

            if all_means:

                total_n = sum(all_n)

                if total_n > 0:

                    weighted_mean = sum(m * n for m, n in zip(all_means, all_n)) / total_n

                else:

                    weighted_mean = np.mean(all_means)

                std = np.std(all_means) if len(all_means) > 1 else 0.05

                se = std / np.sqrt(len(all_means)) if len(all_means) > 1 else 0.05

                metrics_by_agent[agent][metric_name] = {

                    "mean": weighted_mean,

                    "ci_lower": max(0, weighted_mean - 1.96 * se),

                    "ci_upper": min(1, weighted_mean + 1.96 * se),

                    "n": total_n,

                    "n_runs": len(all_means),

                }

    return metrics_by_agent
def plot_core_comparison(

    results: list[dict],

    title: str = "Tool Correctness & Argument Correctness",

    output_path: Path | None = None,
):

    """Create grouped bar chart comparing metrics across agent types."""

    metrics_by_agent = extract_metrics(results)

    agents = [a for a in AGENT_ORDER if a in metrics_by_agent]

    if not agents:

        print("No data found for any agent type.")

        return

    metric_names = ["Tool Correctness", "Argument Correctness [Reference]"]

    x = np.arange(len(agents))

    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, metric_name in enumerate(metric_names):

        means = []

        errors_lower = []

        errors_upper = []

        for agent in agents:

            m = metrics_by_agent[agent].get(metric_name, {})

            mean = m.get("mean", 0)

            ci_low = m.get("ci_lower", mean)

            ci_high = m.get("ci_upper", mean)

            means.append(mean)

            errors_lower.append(mean - ci_low)

            errors_upper.append(ci_high - mean)

        offset = (i - 0.5) * width

        color = METRIC_COLORS[metric_name]

        label = "Tool Correctness" if "Tool" in metric_name else "Argument Correctness"

        bars = ax.bar(

            x + offset, means, width,

            label=label,

            color=color,

            edgecolor="black",

            linewidth=0.5,

            yerr=[errors_lower, errors_upper],

            capsize=4,

            error_kw={"elinewidth": 1.5, "capthick": 1.5},

        )

        for bar, mean in zip(bars, means):

            height = bar.get_height()

            ax.annotate(

                f'{mean:.2f}',

                xy=(bar.get_x() + bar.get_width() / 2, height),

                xytext=(0, 3),

                textcoords="offset points",

                ha='center', va='bottom',

                fontsize=9, fontweight='bold',

            )

    ax.set_xlabel("Agent Architecture")

    ax.set_ylabel("Score")

    ax.set_title(title)

    ax.set_xticks(x)

    ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

    ax.set_ylim(0, 1.15)

    ax.legend(loc="upper right")

    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3, linewidth=1)

    n_info = []

    for agent in agents:

        tc = metrics_by_agent[agent].get("Tool Correctness", {})

        n_info.append(f"n={tc.get('n', 0)}")

    ax.set_xticks(x)

    ax.set_xticklabels([f"{AGENT_NAMES.get(a, a)}\n({n})" for a, n in zip(agents, n_info)])

    plt.tight_layout()

    if output_path:

        output_path.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(output_path)

        print(f"Plot saved to: {output_path}")

    plt.close()

    return output_path
def plot_by_tool_count(

    results: list[dict],

    model: str,

    benchmark: str,

    output_dir: Path,
):

    """Create separate plots for each tool count."""

    by_tools: dict[int, list[dict]] = {}

    for r in results:

        t = r.get("num_tools")

        if t not in by_tools:

            by_tools[t] = []

        by_tools[t].append(r)

    for tool_count, tool_results in sorted(by_tools.items()):

        title = f"{model} - {benchmark} (t{tool_count})\nTool Correctness & Argument Correctness"

        output_path = output_dir / f"core_comparison_{model}_{benchmark}_t{tool_count}.png"

        plot_core_comparison(tool_results, title=title, output_path=output_path)
def main():

    parser = argparse.ArgumentParser(description="Plot core metric comparison")

    parser.add_argument("--model", "-m", help="Filter by model (e.g., gpt-5.4-mini)")

    parser.add_argument("--benchmark", "-b", help="Filter by benchmark")

    parser.add_argument("--tools", "-t", help="Filter by tool count (e.g., t10)")

    parser.add_argument("--mode", help="Filter by mode (e.g., base, long_context)")

    parser.add_argument("--output", "-o", default=str(OUTPUT_DIR), help="Output directory")

    parser.add_argument("--by-tools", action="store_true", help="Create separate plot per tool count")

    args = parser.parse_args()

    output_dir = Path(args.output)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading results from: {RESULTS_DIR}")

    results = load_results(

        model=args.model,

        benchmark=args.benchmark,

        tools=args.tools,

        mode=args.mode,

    )

    print(f"Found {len(results)} result files.")

    if not results:

        print("No results found matching filters.")

        return

    if args.by_tools and args.model and args.benchmark:

        plot_by_tool_count(results, args.model, args.benchmark, output_dir)

    else:

        title_parts = []

        if args.model:

            title_parts.append(args.model)

        if args.benchmark:

            title_parts.append(args.benchmark)

        if args.tools:

            title_parts.append(args.tools)

        if args.mode:

            title_parts.append(args.mode)

        title = " - ".join(title_parts) if title_parts else "All Results"

        title += "\nTool Correctness & Argument Correctness"

        filename_parts = ["core_comparison"]

        if args.model:

            filename_parts.append(args.model.replace("-", "_"))

        if args.benchmark:

            filename_parts.append(args.benchmark)

        if args.tools:

            filename_parts.append(args.tools)

        if args.mode:

            filename_parts.append(args.mode)

        output_path = output_dir / f"{'_'.join(filename_parts)}.png"

        plot_core_comparison(results, title=title, output_path=output_path)
if __name__ == "__main__":

    main()

