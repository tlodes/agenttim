"""
Tool Scaling Plots: TC and AC over tool count per architecture.
Generates one plot per (model x benchmark) combination:
  - X-axis: Tool count (10, 20, 40, 80)
  - Y-axis: Score (0-1)
  - Lines: One per architecture, with markers
  - Two subplots: Tool Correctness (left) + Argument Correctness (right)
  - 95% CI as shaded bands
  - Significance annotation for Single vs best MAS at t80
Usage:
    cd agenttim/evaluation
    python scripts/plot_scaling_v2.py
    python scripts/plot_scaling_v2.py --format pdf
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({

    "font.size": 11,

    "font.family": "serif",

    "axes.titlesize": 13,

    "axes.labelsize": 12,

    "xtick.labelsize": 10,

    "ytick.labelsize": 10,

    "legend.fontsize": 9,

    "figure.dpi": 150,

    "savefig.dpi": 300,

    "savefig.bbox": "tight",

    "savefig.pad_inches": 0.1,
})
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "plots" / "skalierung"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent",

    "orchestrator_fine": "Orch. (Fine)",

    "orchestrator_coarse": "Orch. (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
AGENT_COLORS = {

    "single": "#2ecc71",

    "orchestrator_fine": "#3498db",

    "orchestrator_coarse": "#9b59b6",

    "router": "#e74c3c",

    "swarm": "#f39c12",
}
AGENT_MARKERS = {

    "single": "o",

    "orchestrator_fine": "s",

    "orchestrator_coarse": "D",

    "router": "^",

    "swarm": "v",
}
MODELS = ["gpt-5.4-mini", "deepseek/deepseek-v4-pro", "june-gpt-5-4-datazone"]
MODEL_DISPLAY = {

    "gpt-5.4-mini": "GPT-5.4-mini",

    "deepseek/deepseek-v4-pro": "Deepseek V4 Pro",

    "june-gpt-5-4-datazone": "GPT-5.4",
}
MODEL_FILE_KEY = {

    "gpt-5.4-mini": "gpt-54-mini",

    "deepseek/deepseek-v4-pro": "deepseek",

    "june-gpt-5-4-datazone": "gpt-54",
}
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
TOOL_COUNTS = [10, 20, 40, 80]
METRICS = [

    ("Tool Correctness", "Tool Correctness"),

    ("Argument Correctness [Reference]", "Argument Correctness"),
]
def load_all() -> list[dict[str, Any]]:

    results = []

    for fp in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in fp.name:

            continue

        try:

            data = json.loads(fp.read_text(encoding="utf-8"))

            results.append(data)

        except (json.JSONDecodeError, OSError):

            continue

    return results
def aggregate_scores(

    all_data: list[dict], model: str, benchmark: str,

    agent: str, metric: str, num_tools: int,
) -> dict:

    """Aggregate scores for a specific (model, benchmark, agent, metric, num_tools)."""

    scores = []

    for r in all_data:

        if (r.get("model") != model

                or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent

                or r.get("num_tools") != num_tools):

            continue

        for tc in r.get("test_cases", []):

            m = tc.get("metrics", {}).get(metric, {})

            s = m.get("score")

            if s is not None:

                scores.append(float(s))

    if not scores:

        return {}

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0

    se = std / np.sqrt(n) if n > 1 else 0.0

    return {

        "mean": mean,

        "ci_lower": max(0.0, mean - 1.96 * se),

        "ci_upper": min(1.0, mean + 1.96 * se),

        "n": n,

    }
def plot_scaling(all_data: list[dict], fmt: str) -> None:

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = [

                a for a in AGENT_ORDER

                if any(

                    r.get("model") == model

                    and r.get("benchmark") == benchmark

                    and r.get("agent_type") == a

                    for r in all_data

                )

            ]

            if not agents:

                continue

            fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=True)

            for ax, (metric_key, metric_label) in zip(axes, METRICS):

                for agent in agents:

                    means, ci_lows, ci_highs, valid_tools = [], [], [], []

                    for t in TOOL_COUNTS:

                        agg = aggregate_scores(

                            all_data, model, benchmark, agent, metric_key, t,

                        )

                        if agg:

                            means.append(agg["mean"])

                            ci_lows.append(agg["ci_lower"])

                            ci_highs.append(agg["ci_upper"])

                            valid_tools.append(t)

                    if not means:

                        continue

                    color = AGENT_COLORS.get(agent, "#95a5a6")

                    marker = AGENT_MARKERS.get(agent, "o")

                    label = AGENT_NAMES.get(agent, agent)

                    ax.plot(

                        valid_tools, means,

                        color=color, marker=marker, markersize=7,

                        linewidth=2, label=label, zorder=3,

                    )

                    ax.fill_between(

                        valid_tools, ci_lows, ci_highs,

                        alpha=0.15, color=color, zorder=1,

                    )

                    for t, m in zip(valid_tools, means):

                        ax.annotate(

                            f"{m:.2f}",

                            xy=(t, m), xytext=(0, 8),

                            textcoords="offset points",

                            ha="center", va="bottom",

                            fontsize=7.5, color=color, fontweight="bold",

                        )

                ax.set_xlabel("Number of Tools")

                ax.set_ylabel("Score" if ax == axes[0] else "")

                ax.set_title(metric_label)

                ax.set_xticks(TOOL_COUNTS)

                ax.set_xticklabels([str(t) for t in TOOL_COUNTS])

                ax.set_ylim(0, 1.05)

                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))

            axes[0].legend(loc="lower left", framealpha=0.9)

            fig.suptitle(

                f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES.get(benchmark, benchmark)}",

                fontsize=14, fontweight="bold", y=1.02,

            )

            plt.tight_layout()

            fname = f"scaling_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_DIR / fname)

            plt.close(fig)

            print(f"  Saved: {fname}")
def main():

    parser = argparse.ArgumentParser(description="Tool Scaling Plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\nGenerating scaling plots...")

    plot_scaling(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

