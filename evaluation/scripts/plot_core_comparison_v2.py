"""
Core Comparison Plots: TC and AC per architecture, aggregated across all tool counts.
Generates one plot per (model x benchmark) combination:
  - X-axis: 5 architectures
  - Y-axis: Score (0-1)
  - Grouped bars: Tool Correctness + Argument Correctness
  - 95% CI error bars
  - Significance stars vs Single Agent (from statistical_tests.json)
Usage:
    cd agenttim/evaluation
    python scripts/plot_core_comparison_v2.py
    python scripts/plot_core_comparison_v2.py --format pdf
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
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "plots"
STATS_FILE = Path(__file__).resolve().parent.parent / "results" / "statistical_tests.json"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent",

    "orchestrator_fine": "Orch. (Fine)",

    "orchestrator_coarse": "Orch. (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
METRIC_COLORS = {

    "Tool Correctness": "#2980b9",

    "Argument Correctness [Reference]": "#e67e22",
}
METRIC_LABELS = {

    "Tool Correctness": "Tool Correctness",

    "Argument Correctness [Reference]": "Argument Correctness",
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
METRICS = ["Tool Correctness", "Argument Correctness [Reference]"]
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
def load_significance() -> dict[str, dict]:

    """Load statistical test results, keyed by (model, benchmark, metric, arch_a, arch_b)."""

    if not STATS_FILE.exists():

        return {}

    data = json.loads(STATS_FILE.read_text(encoding="utf-8"))

    lookup = {}

    for r in data.get("results", []):

        key = (r["model"], r["benchmark"], r["metric"], r["arch_a"], r["arch_b"])

        if key not in lookup or r["p_value"] < lookup[key]["p_value"]:

            lookup[key] = r

    return lookup
def aggregate_scores(

    all_data: list[dict], model: str, benchmark: str, agent: str, metric: str,
) -> dict:

    """Aggregate scores across all tool counts and modes for a given config."""

    runs = [

        r for r in all_data

        if r.get("model") == model

        and r.get("benchmark") == benchmark

        and r.get("agent_type") == agent

    ]

    if not runs:

        return {}

    all_scores = []

    for run in runs:

        for tc in run.get("test_cases", []):

            m = tc.get("metrics", {}).get(metric, {})

            score = m.get("score")

            if score is not None:

                all_scores.append(float(score))

    if not all_scores:

        return {}

    arr = np.array(all_scores)

    n = len(arr)

    mean = float(np.mean(arr))

    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0

    se = std / np.sqrt(n) if n > 1 else 0.0

    return {

        "mean": mean,

        "ci_lower": max(0.0, mean - 1.96 * se),

        "ci_upper": min(1.0, mean + 1.96 * se),

        "n": n,

        "std": std,

        "se": se,

    }
def get_sig_stars(p: float) -> str:

    if p < 0.001:

        return "***"

    if p < 0.01:

        return "**"

    if p < 0.05:

        return "*"

    return "ns"
def aggregate_significance(

    all_data: list[dict], model: str, benchmark: str, metric: str,

    arch_a: str, arch_b: str,
) -> dict:

    """Run Wilcoxon on aggregated (all tool counts) paired scores."""

    from scipy.stats import wilcoxon

    runs_a = {}

    runs_b = {}

    for r in all_data:

        if r.get("model") != model or r.get("benchmark") != benchmark:

            continue

        mode = r.get("mode", "")

        num_tools = r.get("num_tools")

        key = (mode, num_tools)

        if r.get("agent_type") == arch_a:

            runs_a[key] = r

        elif r.get("agent_type") == arch_b:

            runs_b[key] = r

    scores_a = []

    scores_b = []

    for key in runs_a:

        if key not in runs_b:

            continue

        ra = runs_a[key]

        rb = runs_b[key]

        rb_by_id = {}

        for tc in rb.get("test_cases", []):

            tc_id = tc.get("id", "")

            if tc_id:

                m = tc.get("metrics", {}).get(metric, {})

                s = m.get("score")

                if s is not None:

                    rb_by_id[tc_id] = float(s)

        for tc in ra.get("test_cases", []):

            tc_id = tc.get("id", "")

            m = tc.get("metrics", {}).get(metric, {})

            sa = m.get("score")

            if sa is not None and tc_id in rb_by_id:

                scores_a.append(float(sa))

                scores_b.append(rb_by_id[tc_id])

    if len(scores_a) < 5:

        return {"n": len(scores_a), "p_value": 1.0, "sig": "ns"}

    diffs = np.array(scores_a) - np.array(scores_b)

    non_zero = diffs[diffs != 0]

    if len(non_zero) == 0:

        return {"n": len(scores_a), "p_value": 1.0, "sig": "ns"}

    stat, p = wilcoxon(non_zero)

    return {"n": len(scores_a), "p_value": p, "sig": get_sig_stars(p)}
def plot_core_comparison(all_data: list[dict], fmt: str) -> None:

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

            n_agents = len(agents)

            n_metrics = len(METRICS)

            bar_width = 0.35

            x = np.arange(n_agents)

            fig, ax = plt.subplots(figsize=(max(8, n_agents * 1.8), 5.5))

            max_height = 0

            bar_positions = {}

            for i, metric in enumerate(METRICS):

                means, ci_lows, ci_highs = [], [], []

                for agent in agents:

                    agg = aggregate_scores(all_data, model, benchmark, agent, metric)

                    m = agg.get("mean", 0)

                    means.append(m)

                    ci_lows.append(m - agg.get("ci_lower", 0))

                    ci_highs.append(agg.get("ci_upper", 0) - m)

                    max_height = max(max_height, agg.get("ci_upper", m))

                offset = (i - 0.5) * bar_width

                positions = x + offset

                bars = ax.bar(

                    positions, means,

                    width=bar_width,

                    yerr=[ci_lows, ci_highs],

                    capsize=3,

                    color=METRIC_COLORS[metric],

                    edgecolor="black",

                    linewidth=0.5,

                    label=METRIC_LABELS[metric],

                    error_kw={"elinewidth": 1.0, "capthick": 1.0},

                    alpha=0.85,

                )

                bar_positions[metric] = positions

                for bar, val in zip(bars, means):

                    if val > 0:

                        ax.text(

                            bar.get_x() + bar.get_width() / 2,

                            bar.get_height() + ci_highs[means.index(val)] + 0.01,

                            f"{val:.2f}",

                            ha="center", va="bottom", fontsize=8, fontweight="bold",

                        )

            if "single" in agents:

                star_y = max_height + 0.08

                for agent in agents:

                    if agent == "single":

                        continue

                    agent_idx = agents.index(agent)

                    sig_tc = aggregate_significance(

                        all_data, model, benchmark, "Tool Correctness", "single", agent,

                    )

                    sig_ac = aggregate_significance(

                        all_data, model, benchmark,

                        "Argument Correctness [Reference]", "single", agent,

                    )

                    best_sig = sig_tc if sig_tc["p_value"] <= sig_ac["p_value"] else sig_ac

                    stars = best_sig["sig"]

                    if stars != "ns":

                        ax.text(

                            x[agent_idx], star_y,

                            stars, ha="center", va="bottom",

                            fontsize=10, fontweight="bold", color="#c0392b",

                        )

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

            ax.set_ylabel("Score")

            ax.set_ylim(0, min(1.05, max_height + 0.15))

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} — {BENCH_NAMES.get(benchmark, benchmark)}")

            ax.legend(loc="upper right")

            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))

            sample_agg = aggregate_scores(all_data, model, benchmark, agents[0], METRICS[0])

            n_total = sample_agg.get("n", "?")

            ax.text(

                0.02, 0.02, f"n = {n_total} TCs/arch (aggregated)",

                transform=ax.transAxes, fontsize=8, color="gray", style="italic",

            )

            plt.tight_layout()

            fname = f"core_comparison_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(OUTPUT_DIR / fname)

            plt.close(fig)

            print(f"  Saved: {fname}")
def main():

    parser = argparse.ArgumentParser(description="Core Comparison Plots (TC + AC)")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\nGenerating core comparison plots...")

    plot_core_comparison(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

