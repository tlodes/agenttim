"""
Latency plots: average wall-clock time per test case (seconds).
Core comparison (aggregated bars) + Scaling per model x benchmark.
Per-TC latency = max(start_time + latency) across all tool calls in that TC.
Falls back to sum(latency) if start_time is missing.
Usage:
    cd agenttim/evaluation
    python scripts/plot_latency.py
"""
import argparse
import json
from pathlib import Path
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
def tc_latency(tc):

    """Compute wall-clock latency for a single test case (seconds)."""

    tools = tc.get("tools_called", [])

    if not tools:

        return None

    wall_times = []

    for t in tools:

        st = t.get("start_time")

        lat = t.get("latency")

        if st is not None and lat is not None:

            wall_times.append(float(st) + float(lat))

    if wall_times:

        return max(wall_times)

    lats = [float(t["latency"]) for t in tools if t.get("latency") is not None]

    return sum(lats) if lats else None
def aggregate_latency(all_data, model, benchmark, agent, num_tools=None):

    values = []

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        if num_tools is not None and r.get("num_tools") != num_tools:

            continue

        for tc in r.get("test_cases", []):

            lat = tc_latency(tc)

            if lat is not None:

                values.append(lat)

    if not values:

        return {}

    arr = np.array(values)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lower": max(0, mean - 1.96 * se),

            "ci_upper": mean + 1.96 * se, "n": n}
def plot_core(all_data, fmt):

    """Aggregated bar plot: avg latency per TC across all tool variations."""

    OUTPUT_GESAMT.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCH_NAMES:

            agents = [a for a in AGENT_ORDER

                      if aggregate_latency(all_data, model, benchmark, a)]

            if not agents:

                continue

            means, ci_lows, ci_highs, colors = [], [], [], []

            for agent in agents:

                agg = aggregate_latency(all_data, model, benchmark, agent)

                m = agg["mean"]

                means.append(m)

                ci_lows.append(m - agg["ci_lower"])

                ci_highs.append(agg["ci_upper"] - m)

                colors.append(AGENT_COLORS.get(agent, "#95a5a6"))

            x = np.arange(len(agents))

            fig, ax = plt.subplots(figsize=(max(8, len(agents) * 1.8), 5.5))

            bars = ax.bar(x, means, width=0.6, yerr=[ci_lows, ci_highs], capsize=4,

                         color=colors, edgecolor="black", linewidth=0.5,

                         error_kw={"elinewidth": 1.0, "capthick": 1.0}, alpha=0.85)

            for bar, val in zip(bars, means):

                idx = means.index(val)

                ax.text(bar.get_x() + bar.get_width() / 2,

                        bar.get_height() + ci_highs[idx] + 0.3,

                        f"{val:.1f}s", ha="center", va="bottom",

                        fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents],

                               rotation=15, ha="right")

            ax.set_ylabel("Avg. Latency per TC (s)")

            ax.set_ylim(0, max(means) * 1.25)

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES[benchmark]}")

            plt.tight_layout()

            fname = f"latency_{MODEL_FK.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_GESAMT / fname)

            plt.close(fig)

            print(f"  Saved: gesamtvergleich/{fname}")
def plot_scaling(all_data, fmt):

    """Scaling line plot: latency over tool counts."""

    OUTPUT_SKAL.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCH_NAMES:

            agents = [a for a in AGENT_ORDER

                      if aggregate_latency(all_data, model, benchmark, a)]

            if not agents:

                continue

            fig, ax = plt.subplots(figsize=(8, 5.5))

            for agent in agents:

                means, ci_lows, ci_highs, valid_tools = [], [], [], []

                for t in TOOL_COUNTS:

                    agg = aggregate_latency(all_data, model, benchmark, agent, t)

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

                    ax.annotate(f"{m:.1f}s", xy=(t, m), xytext=(0, 8),

                               textcoords="offset points", ha="center", va="bottom",

                               fontsize=8, color=color, fontweight="bold")

            ax.set_xlabel("Number of Tools")

            ax.set_ylabel("Avg. Latency per TC (s)")

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES[benchmark]}")

            ax.set_xticks(TOOL_COUNTS)

            ax.set_ylim(0)

            ax.legend(loc="upper left", framealpha=0.9)

            plt.tight_layout()

            fname = f"scaling_latency_{MODEL_FK.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_SKAL / fname)

            plt.close(fig)

            print(f"  Saved: skalierung/{fname}")
def main():

    parser = argparse.ArgumentParser(description="Latency Plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\n--- Core Comparison (Latency) ---")

    plot_core(all_data, args.format)

    print("\n--- Scaling (Latency) ---")

    plot_scaling(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

