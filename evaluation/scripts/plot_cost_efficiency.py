"""
Cost & Efficiency Plots for thesis Chapter 5.
Section 5.2 (Scaling): Token consumption over tool counts
Section 5.4 (Cost):     Aggregated tokens, cost, success/1k tokens per architecture
Usage:
    cd agenttim/evaluation
    python scripts/plot_cost_efficiency.py
    python scripts/plot_cost_efficiency.py --format pdf
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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
SCALING_DIR = Path(__file__).resolve().parent.parent / "plots" / "skalierung"
COST_DIR = Path(__file__).resolve().parent.parent / "plots" / "kosten"
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
def load_all() -> list[dict[str, Any]]:

    results = []

    for fp in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in fp.name:

            continue

        try:

            results.append(json.loads(fp.read_text(encoding="utf-8")))

        except (json.JSONDecodeError, OSError):

            continue

    return results
def get_token_data(all_data, model, benchmark, agent, num_tools=None):

    """Get per-TC token data for a specific config. If num_tools is None, aggregate all."""

    prompt, completion, costs = [], [], []

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        if num_tools is not None and r.get("num_tools") != num_tools:

            continue

        for tc in r.get("test_cases", []):

            tokens = tc.get("tokens", {})

            pt = tokens.get("prompt_tokens")

            ct = tokens.get("completion_tokens")

            cost = tokens.get("cost")

            if pt is not None:

                prompt.append(float(pt))

            if ct is not None:

                completion.append(float(ct))

            if cost is not None:

                costs.append(float(cost))

    return prompt, completion, costs
def get_efficiency(all_data, model, benchmark, agent, num_tools=None):

    """Get success/1k tokens for a config."""

    total_tokens = 0

    passed = 0

    total_tcs = 0

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        if num_tools is not None and r.get("num_tools") != num_tools:

            continue

        for tc in r.get("test_cases", []):

            tokens = tc.get("tokens", {})

            tt = tokens.get("total_tokens", 0)

            total_tokens += tt

            total_tcs += 1

            tc_metric = tc.get("metrics", {}).get("Tool Correctness", {})

            if tc_metric.get("success"):

                passed += 1

    if total_tokens == 0:

        return None, None, None

    success_per_1k = (passed / total_tokens) * 1000 if total_tokens > 0 else 0

    return success_per_1k, passed, total_tcs
def plot_token_scaling(all_data, fmt):

    """Token consumption per TC over tool counts."""

    SCALING_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = [

                a for a in AGENT_ORDER

                if any(r.get("model") == model and r.get("benchmark") == benchmark

                       and r.get("agent_type") == a for r in all_data)

            ]

            if not agents:

                continue

            fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=False)

            ax_prompt = axes[0]

            ax_total = axes[1]

            for agent in agents:

                prompt_means, total_means = [], []

                prompt_cis, total_cis = [], []

                valid_tools = []

                for t in TOOL_COUNTS:

                    prompt, completion, _ = get_token_data(all_data, model, benchmark, agent, t)

                    if not prompt:

                        continue

                    total = [p + c for p, c in zip(prompt, completion)]

                    valid_tools.append(t)

                    pm = np.mean(prompt)

                    tm = np.mean(total)

                    prompt_means.append(pm)

                    total_means.append(tm)

                    pse = np.std(prompt, ddof=1) / np.sqrt(len(prompt)) if len(prompt) > 1 else 0

                    tse = np.std(total, ddof=1) / np.sqrt(len(total)) if len(total) > 1 else 0

                    prompt_cis.append(1.96 * pse)

                    total_cis.append(1.96 * tse)

                if not valid_tools:

                    continue

                color = AGENT_COLORS.get(agent, "#95a5a6")

                marker = AGENT_MARKERS.get(agent, "o")

                label = AGENT_NAMES.get(agent, agent)

                ax_prompt.plot(valid_tools, prompt_means, color=color, marker=marker,

                              markersize=7, linewidth=2, label=label)

                ax_prompt.fill_between(valid_tools,

                                       [m - c for m, c in zip(prompt_means, prompt_cis)],

                                       [m + c for m, c in zip(prompt_means, prompt_cis)],

                                       alpha=0.15, color=color)

                ax_total.plot(valid_tools, total_means, color=color, marker=marker,

                             markersize=7, linewidth=2, label=label)

                ax_total.fill_between(valid_tools,

                                      [m - c for m, c in zip(total_means, total_cis)],

                                      [m + c for m, c in zip(total_means, total_cis)],

                                      alpha=0.15, color=color)

            for ax, title in [(ax_prompt, "Prompt Tokens / TC"),

                              (ax_total, "Total Tokens / TC")]:

                ax.set_xlabel("Number of Tools")

                ax.set_ylabel("Tokens")

                ax.set_title(title)

                ax.set_xticks(TOOL_COUNTS)

                ax.yaxis.set_major_formatter(mticker.FuncFormatter(

                    lambda x, _: f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"))

            ax_prompt.legend(loc="upper left", framealpha=0.9)

            fig.suptitle(

                f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES.get(benchmark, benchmark)}",

                fontsize=14, fontweight="bold", y=1.02)

            plt.tight_layout()

            fname = f"scaling_tokens_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(SCALING_DIR / fname)

            plt.close(fig)

            print(f"  Saved: skalierung/{fname}")
def plot_token_bars(all_data, fmt):

    """Stacked bar: prompt vs completion tokens per architecture, aggregated."""

    COST_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = [

                a for a in AGENT_ORDER

                if any(r.get("model") == model and r.get("benchmark") == benchmark

                       and r.get("agent_type") == a for r in all_data)

            ]

            if not agents:

                continue

            prompt_means, comp_means, n_tcs = [], [], []

            for agent in agents:

                prompt, completion, _ = get_token_data(all_data, model, benchmark, agent)

                if prompt:

                    prompt_means.append(np.mean(prompt))

                    comp_means.append(np.mean(completion))

                    n_tcs.append(len(prompt))

                else:

                    prompt_means.append(0)

                    comp_means.append(0)

                    n_tcs.append(0)

            x = np.arange(len(agents))

            fig, ax = plt.subplots(figsize=(max(8, len(agents) * 1.8), 5.5))

            bars_p = ax.bar(x, prompt_means, width=0.6, label="Prompt Tokens",

                           color="#3498db", edgecolor="black", linewidth=0.5)

            bars_c = ax.bar(x, comp_means, width=0.6, bottom=prompt_means,

                           label="Completion Tokens", color="#e67e22",

                           edgecolor="black", linewidth=0.5)

            for i, (p, c) in enumerate(zip(prompt_means, comp_means)):

                total = p + c

                ax.text(i, total + total * 0.02,

                        f"{total/1000:.1f}k", ha="center", va="bottom",

                        fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

            ax.set_ylabel("Tokens / Test Case")

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES.get(benchmark, benchmark)}")

            ax.legend(loc="upper right")

            ax.yaxis.set_major_formatter(mticker.FuncFormatter(

                lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))

            plt.tight_layout()

            fname = f"tokens_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(COST_DIR / fname)

            plt.close(fig)

            print(f"  Saved: kosten/{fname}")
def plot_efficiency(all_data, fmt):

    """Success/1k tokens per architecture, aggregated."""

    COST_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = [

                a for a in AGENT_ORDER

                if any(r.get("model") == model and r.get("benchmark") == benchmark

                       and r.get("agent_type") == a for r in all_data)

            ]

            if not agents:

                continue

            efficiencies, colors_list = [], []

            valid_agents = []

            for agent in agents:

                eff, passed, total = get_efficiency(all_data, model, benchmark, agent)

                if eff is not None:

                    efficiencies.append(eff)

                    colors_list.append(AGENT_COLORS.get(agent, "#95a5a6"))

                    valid_agents.append(agent)

            if not valid_agents:

                continue

            x = np.arange(len(valid_agents))

            fig, ax = plt.subplots(figsize=(max(8, len(valid_agents) * 1.8), 5.5))

            bars = ax.bar(x, efficiencies, width=0.6, color=colors_list,

                         edgecolor="black", linewidth=0.5)

            for bar, val in zip(bars, efficiencies):

                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,

                        f"{val:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in valid_agents],

                              rotation=15, ha="right")

            ax.set_ylabel("Passed TCs / 1k Tokens")

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES.get(benchmark, benchmark)}")

            plt.tight_layout()

            fname = f"efficiency_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(COST_DIR / fname)

            plt.close(fig)

            print(f"  Saved: kosten/{fname}")
def plot_cost_bars(all_data, fmt):

    """Cost per TC per architecture, aggregated."""

    COST_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = [

                a for a in AGENT_ORDER

                if any(r.get("model") == model and r.get("benchmark") == benchmark

                       and r.get("agent_type") == a for r in all_data)

            ]

            if not agents:

                continue

            cost_means, colors_list, valid_agents = [], [], []

            for agent in agents:

                _, _, costs = get_token_data(all_data, model, benchmark, agent)

                if costs:

                    cost_means.append(np.mean(costs) * 1000)

                    colors_list.append(AGENT_COLORS.get(agent, "#95a5a6"))

                    valid_agents.append(agent)

            if not valid_agents:

                continue

            x = np.arange(len(valid_agents))

            fig, ax = plt.subplots(figsize=(max(8, len(valid_agents) * 1.8), 5.5))

            bars = ax.bar(x, cost_means, width=0.6, color=colors_list,

                         edgecolor="black", linewidth=0.5)

            for bar, val in zip(bars, cost_means):

                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,

                        f"${val:.2f}m", ha="center", va="bottom", fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in valid_agents],

                              rotation=15, ha="right")

            ax.set_ylabel("Cost / TC (milli-USD)")

            ax.set_title(f"{MODEL_DISPLAY.get(model, model)} -- {BENCH_NAMES.get(benchmark, benchmark)}")

            plt.tight_layout()

            fname = f"cost_{MODEL_FILE_KEY.get(model, model)}_{benchmark}.{fmt}"

            fig.savefig(COST_DIR / fname)

            plt.close(fig)

            print(f"  Saved: kosten/{fname}")
def main():

    parser = argparse.ArgumentParser(description="Cost & Efficiency Plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\n--- 5.2: Token Scaling ---")

    plot_token_scaling(all_data, args.format)

    print("\n--- 5.4: Token Consumption ---")

    plot_token_bars(all_data, args.format)

    print("\n--- 5.4: Cost per TC ---")

    plot_cost_bars(all_data, args.format)

    print("\n--- 5.4: Success/1k Tokens ---")

    plot_efficiency(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

