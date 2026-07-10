"""
Generate all plots for thesis Chapter 5 (Ergebnisse).
Based on ERGEBNIS_DISKUSSION_STRUKTUR.md structure:
  5.1 - Gesamtvergleich der Agenten-Architekturen
  5.2 - Skalierungsverhalten über Tool-Anzahl
  5.3 - Einfluss der Benchmark-Domäne
  5.4 - Kosten- und Effizienzanalyse
Usage:
    cd agenttim/evaluation
    python scripts/plot_thesis_chapter5.py
    python scripts/plot_thesis_chapter5.py --format pdf
"""
import argparse
import json
from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
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
MODEL_NAMES = {"gpt-5.4-mini": "GPT-5.4-mini", "deepseek": "Deepseek V4 Pro"}
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
TOOL_COUNTS = [10, 20, 40, 80]
METRICS_FACET = [

    ("Tool Correctness", "Tool Correctness"),

    ("Argument Correctness [Reference]", "Argument Correctness"),

    ("Final State (Derived)", "Final State"),
]
def load_all() -> list[dict[str, Any]]:

    results = []

    for fp in sorted(RESULTS_DIR.rglob("*.json")):

        if "_errors" in fp.name:

            continue

        try:

            data = json.loads(fp.read_text(encoding="utf-8"))

            fp_str = str(fp).lower()

            data["_model"] = "deepseek" if "deepseek" in fp_str else "gpt-5.4-mini" if "gpt" in fp_str else "unknown"

            results.append(data)

        except (json.JSONDecodeError, OSError):

            continue

    return results
def get_ci(run: dict, metric: str) -> dict:

    return run.get("confidence_intervals", {}).get(metric, {})
def weighted_mean(runs: list[dict], metric: str) -> dict:

    """Compute weighted mean + CI across runs for a metric."""

    means, ns = [], []

    for r in runs:

        ci = get_ci(r, metric)

        if ci.get("mean") is not None:

            means.append(ci["mean"])

            ns.append(ci.get("n", 0))

    if not means:

        return {}

    total_n = sum(ns)

    wmean = sum(m * n for m, n in zip(means, ns)) / total_n if total_n else np.mean(means)

    std = np.std(means) if len(means) > 1 else 0.03

    se = std / np.sqrt(len(means)) if len(means) > 1 else 0.03

    pr_vals = [get_ci(r, metric).get("pass_rate") for r in runs if get_ci(r, metric).get("pass_rate") is not None]

    pr_mean = np.mean(pr_vals) if pr_vals else None

    return {"mean": wmean, "ci_lower": max(0, wmean - 1.96 * se), "ci_upper": min(1, wmean + 1.96 * se),

            "n": total_n, "pass_rate": pr_mean}
def plot_1_correctness_facet(all_data: list, fmt: str) -> None:

    """Facetted bar plot: TC / AC / Final State per architecture, per benchmark."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        metrics = [m for m in METRICS_FACET if any(

            get_ci(r, m[0]).get("mean") is not None for r in bench_data

        )]

        if not metrics:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        n_metrics = len(metrics)

        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 5), sharey=True)

        if n_metrics == 1:

            axes = [axes]

        for ax, (metric_key, metric_label) in zip(axes, metrics):

            means, ci_lows, ci_highs, colors = [], [], [], []

            for agent in agents:

                agent_runs = [r for r in bench_data if r.get("agent_type") == agent]

                wm = weighted_mean(agent_runs, metric_key)

                means.append(wm.get("mean", 0))

                ci_lows.append(wm.get("mean", 0) - wm.get("ci_lower", 0))

                ci_highs.append(wm.get("ci_upper", 0) - wm.get("mean", 0))

                colors.append(AGENT_COLORS.get(agent, "#95a5a6"))

            x = np.arange(len(agents))

            bars = ax.bar(x, means, yerr=[ci_lows, ci_highs], capsize=4,

                         color=colors, edgecolor="black", linewidth=0.5,

                         error_kw={"elinewidth": 1.2, "capthick": 1.2})

            for bar, val in zip(bars, means):

                ax.annotate(f"{val:.2f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                           xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=20, ha="right")

            ax.set_title(metric_label)

            ax.set_ylim(0, 1.15)

            if ax == axes[0]:

                ax.set_ylabel("Score (95% CI)")

        fig.suptitle(f"{BENCH_NAMES[benchmark]} — Correctness Decomposition", fontsize=14, fontweight="bold")

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_1_correctness_facet_{benchmark}.{fmt}")

        plt.close()

        print(f"  [1] 5_1_correctness_facet_{benchmark}.{fmt}")
def plot_6_pass_rates(all_data: list, fmt: str) -> None:

    """Pass rates for TC, AC, Final State per architecture, per benchmark."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        metrics = [("Tool Correctness", "Tool Corr."), ("Argument Correctness [Reference]", "Arg. Corr."),

                   ("Final State (Derived)", "Final State")]

        metrics = [(k, l) for k, l in metrics if any(

            weighted_mean([r for r in bench_data if r.get("agent_type") == agents[0]], k).get("pass_rate") is not None

            for _ in [1]

        )]

        fig, ax = plt.subplots(figsize=(10, 5))

        x = np.arange(len(agents))

        width = 0.8 / len(metrics)

        metric_colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]

        for i, (mk, ml) in enumerate(metrics):

            rates = []

            for agent in agents:

                wm = weighted_mean([r for r in bench_data if r.get("agent_type") == agent], mk)

                rates.append((wm.get("pass_rate", 0) or 0) * 100)

            offset = (i - len(metrics) / 2 + 0.5) * width

            bars = ax.bar(x + offset, rates, width, label=ml, color=metric_colors[i],

                         edgecolor="black", linewidth=0.5)

            for bar, val in zip(bars, rates):

                if val > 0:

                    ax.annotate(f"{val:.0f}%", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                               xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=7)

        ax.set_xticks(x)

        ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

        ax.set_ylabel("Pass Rate (%)")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Pass Rates")

        ax.set_ylim(0, 110)

        ax.legend(loc="upper right")

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_1_pass_rates_{benchmark}.{fmt}")

        plt.close()

        print(f"  [6] 5_1_pass_rates_{benchmark}.{fmt}")
def plot_2_tool_scaling(all_data: list, fmt: str) -> None:

    """Line plot: score over tool count, per model x benchmark."""

    for model in ["gpt-5.4-mini", "deepseek"]:

        for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

            bench_data = [r for r in all_data

                         if r.get("benchmark") == benchmark and r.get("_model") == model]

            if not bench_data:

                continue

            metric_pairs = [("Tool Correctness", "Tool Correctness"),

                           ("Final State (Derived)", "Final State")]

            has_fs = any(get_ci(r, "Final State (Derived)").get("mean") is not None for r in bench_data)

            if not has_fs:

                metric_pairs[1] = ("Argument Correctness [Reference]", "Argument Correctness")

            fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

            for ax, (mk, ml) in zip(axes, metric_pairs):

                for agent in AGENT_ORDER:

                    vals, cil, cih, valid_tc = [], [], [], []

                    for tc in TOOL_COUNTS:

                        runs = [r for r in bench_data if r.get("agent_type") == agent and r.get("num_tools") == tc]

                        wm = weighted_mean(runs, mk)

                        if wm.get("mean") is not None:

                            valid_tc.append(tc)

                            vals.append(wm["mean"])

                            cil.append(wm["ci_lower"])

                            cih.append(wm["ci_upper"])

                    if valid_tc:

                        ax.plot(valid_tc, vals, marker=AGENT_MARKERS.get(agent, "o"),

                               color=AGENT_COLORS.get(agent), label=AGENT_NAMES.get(agent),

                               linewidth=2, markersize=8)

                        ax.fill_between(valid_tc, cil, cih, color=AGENT_COLORS.get(agent), alpha=0.12)

                ax.set_xlabel("Number of Tools")

                ax.set_ylabel("Score" if ax == axes[0] else "")

                ax.set_title(ml)

                ax.set_xticks(TOOL_COUNTS)

                ax.set_xticklabels([f"t{t}" for t in TOOL_COUNTS])

                ax.set_ylim(0, 1.05)

                ax.legend(loc="lower left", fontsize=8)

            fig.suptitle(f"{MODEL_NAMES[model]} — {BENCH_NAMES[benchmark]} — Tool Scaling",

                        fontsize=14, fontweight="bold")

            plt.tight_layout()

            out = OUTPUT_DIR / f"5_2_scaling_{model.replace('.', '')}_{benchmark}.{fmt}"

            plt.savefig(out)

            plt.close()

            print(f"  [2] {out.name}")
def plot_5_tc_per_turn(all_data: list, fmt: str) -> None:

    """Line plot: Tool Correctness per turn index (BFCL only)."""

    bfcl_data = [r for r in all_data if r.get("benchmark") == "bfcl_multiturn"]

    if not bfcl_data:

        print("  [5] Skipped (no BFCL data)")

        return

    max_turns = 6

    fig, ax = plt.subplots(figsize=(10, 6))

    for agent in AGENT_ORDER:

        agent_runs = [r for r in bfcl_data if r.get("agent_type") == agent]

        if not agent_runs:

            continue

        turn_scores = {t: [] for t in range(max_turns)}

        for run in agent_runs:

            for tc in run.get("test_cases", []):

                per_turn = tc.get("per_turn", [])

                for turn in per_turn:

                    tidx = turn.get("turn", 0)

                    tm = turn.get("tool_match")

                    if tidx < max_turns and tm is not None:

                        turn_scores[tidx].append(1.0 if tm else 0.0)

        valid_turns, means, stds = [], [], []

        for t in range(max_turns):

            if turn_scores[t]:

                valid_turns.append(t + 1)

                means.append(np.mean(turn_scores[t]))

                stds.append(np.std(turn_scores[t]) / np.sqrt(len(turn_scores[t])))

        if valid_turns:

            means = np.array(means)

            stds = np.array(stds)

            ax.plot(valid_turns, means, marker=AGENT_MARKERS.get(agent, "o"),

                   color=AGENT_COLORS.get(agent), label=AGENT_NAMES.get(agent),

                   linewidth=2, markersize=7)

            ax.fill_between(valid_turns, means - 1.96 * stds, means + 1.96 * stds,

                          color=AGENT_COLORS.get(agent), alpha=0.12)

    ax.set_xlabel("Turn")

    ax.set_ylabel("Tool Match Rate")

    ax.set_title("BFCL Multiturn — Tool Correctness per Turn")

    ax.set_ylim(0, 1.05)

    ax.set_xticks(range(1, max_turns + 1))

    ax.legend()

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / f"5_3_tc_per_turn_bfcl.{fmt}")

    plt.close()

    print(f"  [5] 5_3_tc_per_turn_bfcl.{fmt}")
def plot_8_base_vs_longcontext(all_data: list, fmt: str) -> None:

    """Grouped bar: base vs long_context State Match per architecture."""

    bfcl_data = [r for r in all_data if r.get("benchmark") == "bfcl_multiturn"]

    if not bfcl_data:

        print("  [8] Skipped (no BFCL data)")

        return

    metric_key = "State Match"

    metric_label = "State Match"

    if not any(get_ci(r, metric_key).get("mean") is not None for r in bfcl_data):

        metric_key = "Tool Correctness"

        metric_label = "Tool Correctness"

    agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bfcl_data)]

    modes = ["base", "long_context"]

    mode_colors = ["#3498db", "#e74c3c"]

    mode_labels = ["Base", "Long Context"]

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(agents))

    width = 0.35

    for i, (mode, color, label) in enumerate(zip(modes, mode_colors, mode_labels)):

        means, errs_low, errs_high = [], [], []

        for agent in agents:

            runs = [r for r in bfcl_data if r.get("agent_type") == agent and r.get("mode") == mode]

            wm = weighted_mean(runs, metric_key)

            m = wm.get("mean", 0)

            means.append(m)

            errs_low.append(m - wm.get("ci_lower", m))

            errs_high.append(wm.get("ci_upper", m) - m)

        offset = (i - 0.5) * width

        bars = ax.bar(x + offset, means, width, label=label, color=color,

                     edgecolor="black", linewidth=0.5,

                     yerr=[errs_low, errs_high], capsize=4,

                     error_kw={"elinewidth": 1.2, "capthick": 1.2})

        for bar, val in zip(bars, means):

            if val > 0:

                ax.annotate(f"{val:.2f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                           xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

    ax.set_ylabel(f"{metric_label} Score (95% CI)")

    ax.set_title(f"BFCL Multiturn — Base vs. Long Context ({metric_label})")

    ax.set_ylim(0, 1.15)

    ax.legend()

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / f"5_3_base_vs_longcontext.{fmt}")

    plt.close()

    print(f"  [8] 5_3_base_vs_longcontext.{fmt}")
def plot_9_token_overhead(all_data: list, fmt: str) -> None:

    """Bar plot: avg tokens per architecture, showing coordination overhead."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        fig, ax = plt.subplots(figsize=(10, 5))

        agent_tokens = []

        for agent in agents:

            agent_runs = [r for r in bench_data if r.get("agent_type") == agent]

            all_tokens = []

            for run in agent_runs:

                for tc in run.get("test_cases", []):

                    tok = tc.get("tokens", {}).get("total_tokens")

                    if tok and tok > 0:

                        all_tokens.append(tok)

            if all_tokens:

                agent_tokens.append({

                    "agent": agent, "mean": np.mean(all_tokens),

                    "std": np.std(all_tokens), "median": np.median(all_tokens),

                })

            else:

                agent_tokens.append({"agent": agent, "mean": 0, "std": 0, "median": 0})

        single_mean = next((at["mean"] for at in agent_tokens if at["agent"] == "single"), 1)

        x = np.arange(len(agents))

        means = [at["mean"] / 1000 for at in agent_tokens]

        stds = [at["std"] / 1000 for at in agent_tokens]

        colors = [AGENT_COLORS.get(a, "#95a5a6") for a in agents]

        bars = ax.bar(x, means, yerr=stds, capsize=4, color=colors,

                     edgecolor="black", linewidth=0.5)

        for bar, at in zip(bars, agent_tokens):

            val_k = at["mean"] / 1000

            ax.annotate(f"{val_k:.1f}k", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                       xytext=(0, 12), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

            if at["agent"] != "single" and single_mean > 0:

                overhead = (at["mean"] - single_mean) / single_mean * 100

                color = "#e74c3c" if overhead > 0 else "#2ecc71"

                ax.annotate(f"{overhead:+.0f}%", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                           xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8,

                           color=color, fontweight="bold")

        ax.set_xticks(x)

        ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

        ax.set_ylabel("Avg. Tokens per Test Case (thousands)")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Token Usage & Coordination Overhead")

        ax.axhline(y=single_mean / 1000, color="#2ecc71", linestyle="--", alpha=0.5, linewidth=1, label="Single Agent Baseline")

        ax.legend(loc="upper left")

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_4_token_overhead_{benchmark}.{fmt}")

        plt.close()

        print(f"  [9] 5_4_token_overhead_{benchmark}.{fmt}")
def plot_10_cost_performance(all_data: list, fmt: str) -> None:

    """Scatter: cost vs Tool Correctness per architecture."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        fig, ax = plt.subplots(figsize=(9, 6))

        for agent in agents:

            agent_runs = [r for r in bench_data if r.get("agent_type") == agent]

            wm = weighted_mean(agent_runs, "Tool Correctness")

            tc_score = wm.get("mean")

            if tc_score is None:

                continue

            all_costs = []

            for run in agent_runs:

                for tc in run.get("test_cases", []):

                    cost = tc.get("tokens", {}).get("cost")

                    if cost and cost > 0:

                        all_costs.append(cost)

            if not all_costs:

                continue

            avg_cost = np.mean(all_costs) * 1000

            color = AGENT_COLORS.get(agent)

            ax.scatter(avg_cost, tc_score, s=200, c=color, edgecolors="black",

                      linewidth=1.2, zorder=3, marker=AGENT_MARKERS.get(agent, "o"))

            ax.annotate(AGENT_NAMES.get(agent), (avg_cost, tc_score),

                       xytext=(8, 5), textcoords="offset points", fontsize=9)

        ax.set_xlabel("Avg. Cost per Test Case (m$)")

        ax.set_ylabel("Tool Correctness Score")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Cost vs. Performance")

        ax.set_ylim(0, 1.05)

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_4_cost_performance_{benchmark}.{fmt}")

        plt.close()

        print(f"  [10] 5_4_cost_performance_{benchmark}.{fmt}")
def plot_11_latency(all_data: list, fmt: str) -> None:

    """Box plot: latency distribution per architecture."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        fig, ax = plt.subplots(figsize=(10, 5))

        data_boxes = []

        for agent in agents:

            agent_runs = [r for r in bench_data if r.get("agent_type") == agent]

            latencies = []

            for run in agent_runs:

                for tc in run.get("test_cases", []):

                    lat = tc.get("latency")

                    if isinstance(lat, dict):

                        lat = lat.get("total", 0)

                    if lat and lat > 0:

                        latencies.append(lat)

            data_boxes.append(latencies if latencies else [0])

        bp = ax.boxplot(data_boxes, tick_labels=[AGENT_NAMES.get(a, a) for a in agents],

                       patch_artist=True, showfliers=False)

        for patch, agent in zip(bp["boxes"], agents):

            patch.set_facecolor(AGENT_COLORS.get(agent, "#95a5a6"))

            patch.set_alpha(0.7)

        for i, (median_line, agent) in enumerate(zip(bp["medians"], agents)):

            median_val = median_line.get_ydata()[0]

            ax.annotate(f"{median_val:.1f}s", xy=(i + 1, median_val),

                       xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, fontweight="bold")

        ax.set_ylabel("Latency (seconds)")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Latency Distribution (outliers hidden)")

        plt.xticks(rotation=15, ha="right")

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_4_latency_{benchmark}.{fmt}")

        plt.close()

        print(f"  [11] 5_4_latency_{benchmark}.{fmt}")
def plot_B_error_composition(all_data: list, fmt: str) -> None:

    """Stacked bar: error types per architecture (timeouts, TC failures, AC failures)."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        error_data = {a: {"timeout": 0, "tc_fail": 0, "ac_fail": 0, "pass": 0, "total": 0} for a in agents}

        for run in bench_data:

            agent = run.get("agent_type")

            if agent not in error_data:

                continue

            for tc in run.get("test_cases", []):

                error_data[agent]["total"] += 1

                err = tc.get("error")

                if err and "Timeout" in str(err):

                    error_data[agent]["timeout"] += 1

                    continue

                metrics = tc.get("metrics", {})

                tc_m = metrics.get("Tool Correctness", {})

                ac_m = metrics.get("Argument Correctness [Reference]", {})

                tc_ok = tc_m.get("success", False)

                ac_ok = ac_m.get("success", False)

                if tc_ok and ac_ok:

                    error_data[agent]["pass"] += 1

                elif not tc_ok:

                    error_data[agent]["tc_fail"] += 1

                else:

                    error_data[agent]["ac_fail"] += 1

        fig, ax = plt.subplots(figsize=(10, 5))

        x = np.arange(len(agents))

        categories = ["pass", "tc_fail", "ac_fail", "timeout"]

        cat_labels = ["Pass", "Tool Error", "Arg Error", "Timeout"]

        cat_colors = ["#2ecc71", "#e74c3c", "#f39c12", "#95a5a6"]

        bottom = np.zeros(len(agents))

        for cat, label, color in zip(categories, cat_labels, cat_colors):

            vals = []

            for agent in agents:

                total = error_data[agent]["total"]

                vals.append(error_data[agent][cat] / total * 100 if total else 0)

            ax.bar(x, vals, bottom=bottom, label=label, color=color, edgecolor="black", linewidth=0.3)

            bottom += vals

        ax.set_xticks(x)

        ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

        ax.set_ylabel("Percentage of Test Cases")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Error Composition")

        ax.set_ylim(0, 105)

        ax.legend(loc="upper right")

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_1_error_composition_{benchmark}.{fmt}")

        plt.close()

        print(f"  [B] 5_1_error_composition_{benchmark}.{fmt}")
def plot_model_comparison(all_data: list, fmt: str) -> None:

    """Grouped bar: GPT vs Deepseek per architecture for TC."""

    for benchmark in ["mcpagentbench", "bfcl_multiturn"]:

        bench_data = [r for r in all_data if r.get("benchmark") == benchmark]

        if not bench_data:

            continue

        agents = [a for a in AGENT_ORDER if any(r.get("agent_type") == a for r in bench_data)]

        models = ["gpt-5.4-mini", "deepseek"]

        model_colors = ["#3498db", "#e74c3c"]

        fig, ax = plt.subplots(figsize=(10, 5))

        x = np.arange(len(agents))

        width = 0.35

        for i, (model, color) in enumerate(zip(models, model_colors)):

            means, errs_low, errs_high = [], [], []

            for agent in agents:

                runs = [r for r in bench_data if r.get("agent_type") == agent and r.get("_model") == model]

                wm = weighted_mean(runs, "Tool Correctness")

                m = wm.get("mean", 0)

                means.append(m)

                errs_low.append(m - wm.get("ci_lower", m))

                errs_high.append(wm.get("ci_upper", m) - m)

            offset = (i - 0.5) * width

            bars = ax.bar(x + offset, means, width, label=MODEL_NAMES[model], color=color,

                         edgecolor="black", linewidth=0.5,

                         yerr=[errs_low, errs_high], capsize=4)

            for bar, val in zip(bars, means):

                if val > 0:

                    ax.annotate(f"{val:.2f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),

                               xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

        ax.set_xticks(x)

        ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents])

        ax.set_ylabel("Tool Correctness (95% CI)")

        ax.set_title(f"{BENCH_NAMES[benchmark]} — Model Comparison")

        ax.set_ylim(0, 1.15)

        ax.legend()

        plt.tight_layout()

        plt.savefig(OUTPUT_DIR / f"5_1_model_comparison_{benchmark}.{fmt}")

        plt.close()

        print(f"  [+] 5_1_model_comparison_{benchmark}.{fmt}")
def main():

    parser = argparse.ArgumentParser(description="Generate thesis Chapter 5 plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    fmt = args.format

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading results from: {RESULTS_DIR}")

    all_data = load_all()

    print(f"Loaded {len(all_data)} result files.\n")

    print("=== 5.1 Gesamtvergleich ===")

    plot_1_correctness_facet(all_data, fmt)

    plot_6_pass_rates(all_data, fmt)

    plot_B_error_composition(all_data, fmt)

    plot_model_comparison(all_data, fmt)

    print("\n=== 5.2 Skalierung ===")

    plot_2_tool_scaling(all_data, fmt)

    print("\n=== 5.3 Benchmark-Domäne ===")

    plot_5_tc_per_turn(all_data, fmt)

    plot_8_base_vs_longcontext(all_data, fmt)

    print("\n=== 5.4 Kosten & Effizienz ===")

    plot_9_token_overhead(all_data, fmt)

    plot_10_cost_performance(all_data, fmt)

    plot_11_latency(all_data, fmt)

    print(f"\nAll plots saved to: {OUTPUT_DIR}")
if __name__ == "__main__":

    main()

