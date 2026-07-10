"""
Final State (MCPAgentBench) and State Match (BFCL) plots.
Core comparison (aggregated) + Scaling per model x benchmark.
Usage:
    cd agenttim/evaluation
    python scripts/plot_final_state.py
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({

    "font.size": 11, "font.family": "serif", "axes.titlesize": 13,

    "axes.labelsize": 12, "xtick.labelsize": 10, "ytick.labelsize": 10,

    "legend.fontsize": 9, "figure.dpi": 150, "savefig.dpi": 300,

    "savefig.bbox": "tight", "savefig.pad_inches": 0.1,
})
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
OUTPUT_GESAMT = Path(__file__).resolve().parent.parent / "plots" / "gesamtvergleich"
OUTPUT_SKAL = Path(__file__).resolve().parent.parent / "plots" / "skalierung"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent", "orchestrator_fine": "Orch. (Fine)",

    "orchestrator_coarse": "Orch. (Coarse)", "router": "Router", "swarm": "Swarm",
}
AGENT_COLORS = {

    "single": "#2ecc71", "orchestrator_fine": "#3498db",

    "orchestrator_coarse": "#9b59b6", "router": "#e74c3c", "swarm": "#f39c12",
}
AGENT_MARKERS = {

    "single": "o", "orchestrator_fine": "s", "orchestrator_coarse": "D",

    "router": "^", "swarm": "v",
}
MODELS = ["gpt-5.4-mini", "deepseek/deepseek-v4-pro", "june-gpt-5-4-datazone"]
MODEL_DISPLAY = {

    "gpt-5.4-mini": "GPT-5.4-mini", "deepseek/deepseek-v4-pro": "Deepseek V4 Pro",

    "june-gpt-5-4-datazone": "GPT-5.4",
}
MODEL_FK = {

    "gpt-5.4-mini": "gpt-54-mini", "deepseek/deepseek-v4-pro": "deepseek",

    "june-gpt-5-4-datazone": "gpt-54",
}
BENCH_METRIC = {

    "mcpagentbench": ("Final State (Derived)", "Final State"),

    "bfcl_multiturn": ("State Match", "State Match"),
}
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
TOOL_COUNTS = [10, 20, 40, 80]
def load_all():

    results = []

    for fp in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in fp.name:

            continue

        try:

            results.append(json.loads(fp.read_text(encoding="utf-8")))

        except (json.JSONDecodeError, OSError):

            continue

    return results
def aggregate(all_data, model, benchmark, agent, metric, num_tools=None):

    scores = []

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        if num_tools is not None and r.get("num_tools") != num_tools:

            continue

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric, {}).get("score")

            if s is not None:

                scores.append(float(s))

    if not scores:

        return {}

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lower": max(0, mean - 1.96 * se),

            "ci_upper": min(1, mean + 1.96 * se), "n": n}
def plot_core(all_data, fmt):

    """Aggregated bar plot per model x benchmark."""

    OUTPUT_GESAMT.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark, (metric_key, metric_label) in BENCH_METRIC.items():

            agents = [a for a in AGENT_ORDER if aggregate(all_data, model, benchmark, a, metric_key)]

            if not agents:

                continue

            means, ci_lows, ci_highs, colors = [], [], [], []

            for agent in agents:

                agg = aggregate(all_data, model, benchmark, agent, metric_key)

                m = agg.get("mean", 0)

                means.append(m)

                ci_lows.append(m - agg.get("ci_lower", 0))

                ci_highs.append(agg.get("ci_upper", 0) - m)

                colors.append(AGENT_COLORS.get(agent, "#95a5a6"))

            x = np.arange(len(agents))

            fig, ax = plt.subplots(figsize=(max(8, len(agents) * 1.8), 5.5))

            bars = ax.bar(x, means, width=0.6, yerr=[ci_lows, ci_highs], capsize=4,

                         color=colors, edgecolor="black", linewidth=0.5,

                         error_kw={"elinewidth": 1.0, "capthick": 1.0}, alpha=0.85)

            for bar, val in zip(bars, means):

                ax.text(bar.get_x() + bar.get_width() / 2,

                        bar.get_height() + ci_highs[means.index(val)] + 0.01,

                        f"{val:.2f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

            ax.set_ylabel(metric_label)

            ax.set_ylim(0, min(1.05, max(means) + 0.15))

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES[benchmark]}")

            plt.tight_layout()

            fname = f"final_state_{MODEL_FK.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_GESAMT / fname)

            plt.close(fig)

            print(f"  Saved: gesamtvergleich/{fname}")
def plot_scaling(all_data, fmt):

    """Scaling line plot per model x benchmark."""

    OUTPUT_SKAL.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark, (metric_key, metric_label) in BENCH_METRIC.items():

            agents = [a for a in AGENT_ORDER if aggregate(all_data, model, benchmark, a, metric_key)]

            if not agents:

                continue

            fig, ax = plt.subplots(figsize=(8, 5.5))

            for agent in agents:

                means, ci_lows, ci_highs, valid_tools = [], [], [], []

                for t in TOOL_COUNTS:

                    agg = aggregate(all_data, model, benchmark, agent, metric_key, t)

                    if agg:

                        means.append(agg["mean"])

                        ci_lows.append(agg["ci_lower"])

                        ci_highs.append(agg["ci_upper"])

                        valid_tools.append(t)

                if not means:

                    continue

                color = AGENT_COLORS.get(agent, "#95a5a6")

                marker = AGENT_MARKERS.get(agent, "o")

                ax.plot(valid_tools, means, color=color, marker=marker,

                       markersize=7, linewidth=2, label=AGENT_NAMES.get(agent, agent))

                ax.fill_between(valid_tools, ci_lows, ci_highs, alpha=0.15, color=color)

                for t, m in zip(valid_tools, means):

                    ax.annotate(f"{m:.2f}", xy=(t, m), xytext=(0, 8),

                               textcoords="offset points", ha="center", va="bottom",

                               fontsize=8, color=color, fontweight="bold")

            ax.set_xlabel("Number of Tools")

            ax.set_ylabel(metric_label)

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES[benchmark]}")

            ax.set_xticks(TOOL_COUNTS)

            ax.set_ylim(0, 1.05)

            ax.legend(loc="lower left", framealpha=0.9)

            plt.tight_layout()

            fname = f"scaling_final_state_{MODEL_FK.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_SKAL / fname)

            plt.close(fig)

            print(f"  Saved: skalierung/{fname}")
def main():

    parser = argparse.ArgumentParser(description="Final State / State Match Plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\n--- Core Comparison ---")

    plot_core(all_data, args.format)

    print("\n--- Scaling ---")

    plot_scaling(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

