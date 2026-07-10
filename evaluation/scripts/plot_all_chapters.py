"""
Generate ALL thesis plots — one plot per metric x benchmark, all 3 models combined.
Overall: grouped bars (models side by side per architecture).
Scaling: 3 subplots (one per model) in a single figure.
Folder structure:
  plots/5_1_core_comparison/{overall,skalierung}/
  plots/5_2_kosten_tokens/{overall,skalierung}/
  plots/5_3_latenz/{overall,skalierung}/
  plots/5_4_benchmark_spezifisch/{overall,skalierung}/
Usage:
    cd agenttim/evaluation
    python scripts/plot_all_chapters.py
    python scripts/plot_all_chapters.py --format pdf
"""
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({

    "font.size": 11, "font.family": "serif", "axes.titlesize": 13,

    "axes.labelsize": 12, "xtick.labelsize": 10, "ytick.labelsize": 10,

    "legend.fontsize": 9, "figure.dpi": 150, "savefig.dpi": 300,

    "savefig.bbox": "tight", "savefig.pad_inches": 0.1,
})
BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_enriched"
DIRS = {

    "5_1_overall": BASE / "plots" / "5_1_core_comparison" / "overall",

    "5_1_skal":    BASE / "plots" / "5_1_core_comparison" / "skalierung",

    "5_2_overall": BASE / "plots" / "5_2_kosten_tokens" / "overall",

    "5_2_skal":    BASE / "plots" / "5_2_kosten_tokens" / "skalierung",

    "5_3_overall": BASE / "plots" / "5_3_latenz" / "overall",

    "5_3_skal":    BASE / "plots" / "5_3_latenz" / "skalierung",

    "5_4_overall": BASE / "plots" / "5_4_benchmark_spezifisch" / "overall",

    "5_4_skal":    BASE / "plots" / "5_4_benchmark_spezifisch" / "skalierung",
}
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
MODEL_COLORS = {

    "gpt-5.4-mini": "#3498db", "deepseek/deepseek-v4-pro": "#e74c3c",

    "june-gpt-5-4-datazone": "#2ecc71",
}
MODEL_HATCHES = {

    "gpt-5.4-mini": "", "deepseek/deepseek-v4-pro": "//",

    "june-gpt-5-4-datazone": "xx",
}
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
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
def _filter(all_data, model, benchmark, agent, num_tools=None):

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        if num_tools is not None and r.get("num_tools") != num_tools:

            continue

        yield r
def available_agents_for_benchmark(all_data, benchmark):

    """Agents available for ANY model on this benchmark."""

    found = set()

    for r in all_data:

        if r.get("benchmark") == benchmark:

            found.add(r.get("agent_type"))

    return [a for a in AGENT_ORDER if a in found]
def agg_metric(all_data, model, benchmark, agent, metric_key, num_tools=None):

    scores = []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric_key, {}).get("score")

            if s is not None:

                scores.append(float(s))

    if not scores:

        return None

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

            "ci_hi": min(1, mean + 1.96 * se), "n": n}
def agg_latency(all_data, model, benchmark, agent, num_tools=None):

    vals = []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            tools = tc.get("tools_called", [])

            if not tools:

                continue

            wall = []

            for t in tools:

                st = t.get("start_time")

                lat = t.get("latency")

                if st is not None and lat is not None:

                    wall.append(float(st) + float(lat))

            if wall:

                vals.append(max(wall))

    if not vals:

        return None

    arr = np.array(vals)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

            "ci_hi": mean + 1.96 * se, "n": n}
def agg_tokens(all_data, model, benchmark, agent, num_tools=None):

    prompt, completion = [], []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            tokens = tc.get("tokens", {})

            pt = tokens.get("prompt_tokens")

            ct = tokens.get("completion_tokens")

            if pt is not None:

                prompt.append(float(pt))

            if ct is not None:

                completion.append(float(ct))

    if not prompt:

        return None

    return {"prompt": np.array(prompt), "completion": np.array(completion)}
def agg_efficiency(all_data, model, benchmark, agent):

    total_tokens = 0

    passed = 0

    for r in _filter(all_data, model, benchmark, agent):

        for tc in r.get("test_cases", []):

            tt = tc.get("tokens", {}).get("total_tokens", 0)

            total_tokens += tt

            if tc.get("metrics", {}).get("Tool Correctness", {}).get("success"):

                passed += 1

    if total_tokens == 0:

        return None

    return (passed / total_tokens) * 1000
def agg_token_overhead(all_data, model, benchmark, agent, num_tools=None):

    scores = []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            oh = tc.get("metrics", {}).get("Coordination Token Overhead", {})

            s = oh.get("score")

            if s is not None:

                scores.append(float(s))

    if not scores:

        return None

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

            "ci_hi": min(1, mean + 1.96 * se), "n": n}
def _save(fig, out_dir, fname):

    out_dir.mkdir(parents=True, exist_ok=True)

    fig.savefig(out_dir / fname)

    plt.close(fig)

    rel = str(out_dir.relative_to(BASE / "plots"))

    print(f"  Saved: {rel}/{fname}")
def agent_comparison_plot(agents, model_data, ylabel, title, out_dir, fname,

                          fmt_val=".2f", suffix="", ylim_max=None):

    """Grouped bar plot: MODELS on x-axis, one bar per agent architecture.
    model_data = {model: {agent: {"mean":, "ci_lo":, "ci_hi":}}}
    """

    models_with_data = [m for m in MODELS if m in model_data and model_data[m]]

    if not models_with_data:

        return

    valid_agents = [a for a in agents if any(

        a in model_data.get(m, {}) for m in models_with_data)]

    if not valid_agents:

        return

    n_models = len(models_with_data)

    n_agents = len(valid_agents)

    bar_width = 0.7 / n_agents

    x = np.arange(n_models)

    fig, ax = plt.subplots(figsize=(max(9, n_models * 3), 6))

    for j, agent in enumerate(valid_agents):

        means, ci_lows, ci_highs = [], [], []

        for m in models_with_data:

            d = model_data[m].get(agent)

            if d:

                means.append(d["mean"])

                ci_lows.append(d["mean"] - d["ci_lo"])

                ci_highs.append(d["ci_hi"] - d["mean"])

            else:

                means.append(0)

                ci_lows.append(0)

                ci_highs.append(0)

        offset = (j - n_agents / 2 + 0.5) * bar_width

        bars = ax.bar(x + offset, means, bar_width * 0.9,

                      yerr=[ci_lows, ci_highs], capsize=3,

                      color=AGENT_COLORS.get(agent, "#95a5a6"), alpha=0.85,

                      edgecolor="black", linewidth=0.5,

                      error_kw={"elinewidth": 0.8, "capthick": 0.8},

                      label=AGENT_NAMES.get(agent, agent))

        for bar, val, ci_h in zip(bars, means, ci_highs):

            if val > 0:

                ax.text(bar.get_x() + bar.get_width() / 2,

                        bar.get_height() + ci_h + (ylim_max or max(means)) * 0.015,

                        f"{val:{fmt_val}}{suffix}", ha="center", va="bottom",

                        fontsize=7, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels([MODEL_DISPLAY[m] for m in models_with_data])

    ax.set_ylabel(ylabel)

    ax.set_title(title)

    if ylim_max:

        ax.set_ylim(0, ylim_max)

    else:

        all_means = [model_data[m].get(a, {}).get("mean", 0)

                     for m in models_with_data for a in valid_agents]

        ax.set_ylim(0, max(all_means) * 1.25 if all_means and max(all_means) > 0 else 1)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12),

              ncol=min(n_agents, 3), framealpha=0.9, fontsize=8)

    plt.tight_layout()

    _save(fig, out_dir, fname)
def grouped_bar_plot(agents, model_data, ylabel, title, out_dir, fname,

                     fmt_val=".2f", suffix="", ylim_max=None):

    """Grouped bar plot: agents on x-axis, one bar per model (MODEL comparison).
    model_data = {model: {agent: {"mean":, "ci_lo":, "ci_hi":}}}
    """

    models_with_data = [m for m in MODELS if m in model_data and model_data[m]]

    if not models_with_data or not agents:

        return

    n_agents = len(agents)

    n_models = len(models_with_data)

    bar_width = 0.7 / n_models

    x = np.arange(n_agents)

    fig, ax = plt.subplots(figsize=(max(10, n_agents * 2.2), 6))

    for j, model in enumerate(models_with_data):

        means, ci_lows, ci_highs = [], [], []

        for a in agents:

            d = model_data[model].get(a)

            if d:

                means.append(d["mean"])

                ci_lows.append(d["mean"] - d["ci_lo"])

                ci_highs.append(d["ci_hi"] - d["mean"])

            else:

                means.append(0)

                ci_lows.append(0)

                ci_highs.append(0)

        offset = (j - n_models / 2 + 0.5) * bar_width

        bars = ax.bar(x + offset, means, bar_width * 0.9,

                      yerr=[ci_lows, ci_highs], capsize=3,

                      color=MODEL_COLORS[model], alpha=0.85,

                      edgecolor="black", linewidth=0.5,

                      hatch=MODEL_HATCHES.get(model, ""),

                      error_kw={"elinewidth": 0.8, "capthick": 0.8},

                      label=MODEL_DISPLAY[model])

        for bar, val, ci_h in zip(bars, means, ci_highs):

            if val > 0:

                ax.text(bar.get_x() + bar.get_width() / 2,

                        bar.get_height() + ci_h + (ylim_max or max(means)) * 0.015,

                        f"{val:{fmt_val}}{suffix}", ha="center", va="bottom",

                        fontsize=7, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

    ax.set_ylabel(ylabel)

    ax.set_title(title)

    if ylim_max:

        ax.set_ylim(0, ylim_max)

    else:

        all_means = [model_data[m].get(a, {}).get("mean", 0)

                     for m in models_with_data for a in agents]

        ax.set_ylim(0, max(all_means) * 1.25 if all_means and max(all_means) > 0 else 1)

    ax.legend(loc="upper right", framealpha=0.9)

    plt.tight_layout()

    _save(fig, out_dir, fname)
def scaling_subplots(agents, model_tool_data, ylabel, title, out_dir, fname,

                     fmt_val=".2f", suffix="", ylim=None):

    """3 subplots (one per model) with scaling lines.
    model_tool_data = {model: {agent: {t: agg_dict}}}
    """

    models_with_data = [m for m in MODELS if m in model_tool_data and model_tool_data[m]]

    if not models_with_data:

        return

    share = ylim is not None

    n = len(models_with_data)

    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5), sharey=share)

    if n == 1:

        axes = [axes]

    for ax, model in zip(axes, models_with_data):

        for agent in agents:

            data = model_tool_data[model].get(agent, {})

            if not data:

                continue

            tools = sorted(data.keys())

            means = [data[t]["mean"] for t in tools]

            ci_lo = [data[t]["ci_lo"] for t in tools]

            ci_hi = [data[t]["ci_hi"] for t in tools]

            color = AGENT_COLORS.get(agent, "#95a5a6")

            marker = AGENT_MARKERS.get(agent, "o")

            ax.plot(tools, means, color=color, marker=marker, markersize=6,

                    linewidth=2, label=AGENT_NAMES.get(agent, agent))

            ax.fill_between(tools, ci_lo, ci_hi, alpha=0.12, color=color)

            for t, m in zip(tools, means):

                ax.annotate(f"{m:{fmt_val}}{suffix}", xy=(t, m), xytext=(0, 7),

                            textcoords="offset points", ha="center", va="bottom",

                            fontsize=7, color=color, fontweight="bold")

        ax.set_xlabel("Number of Tools")

        ax.set_title(MODEL_DISPLAY[model])

        ax.set_xticks(TOOL_COUNTS)

        if ylim is not None:

            ax.set_ylim(*ylim)

        else:

            ax.set_ylim(0)

    axes[0].set_ylabel(ylabel)

    axes[0].legend(loc="best", framealpha=0.9, fontsize=8)

    fig.suptitle(title, fontsize=14, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    _save(fig, out_dir, fname)
def scaling_model_subplots(agents, model_tool_data, ylabel, title, out_dir, fname,

                           fmt_val=".2f", suffix="", ylim=None):

    """Scaling subplots: one subplot per AGENT, lines = MODELS (Modellvergleich).
    model_tool_data = {model: {agent: {t: agg_dict}}}
    """

    valid_agents = [a for a in agents if any(

        a in model_tool_data.get(m, {}) for m in MODELS)]

    if not valid_agents:

        return

    n = len(valid_agents)

    share = ylim is not None

    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), sharey=share)

    if n == 1:

        axes = [axes]

    for ax, agent in zip(axes, valid_agents):

        for model in MODELS:

            data = model_tool_data.get(model, {}).get(agent, {})

            if not data:

                continue

            tools = sorted(data.keys())

            means = [data[t]["mean"] for t in tools]

            ci_lo = [data[t]["ci_lo"] for t in tools]

            ci_hi = [data[t]["ci_hi"] for t in tools]

            color = MODEL_COLORS[model]

            ax.plot(tools, means, color=color, marker="o", markersize=6,

                    linewidth=2, label=MODEL_DISPLAY[model],

                    linestyle="--" if "deepseek" in model else "-")

            ax.fill_between(tools, ci_lo, ci_hi, alpha=0.12, color=color)

            for t, m in zip(tools, means):

                ax.annotate(f"{m:{fmt_val}}{suffix}", xy=(t, m), xytext=(0, 7),

                            textcoords="offset points", ha="center", va="bottom",

                            fontsize=7, color=color, fontweight="bold")

        ax.set_xlabel("Number of Tools")

        ax.set_title(AGENT_NAMES.get(agent, agent))

        ax.set_xticks(TOOL_COUNTS)

        if ylim is not None:

            ax.set_ylim(*ylim)

        else:

            ax.set_ylim(0)

    axes[0].set_ylabel(ylabel)

    axes[0].legend(loc="best", framealpha=0.9, fontsize=8)

    fig.suptitle(title, fontsize=14, fontweight="bold")

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    _save(fig, out_dir, fname)
CORE_METRICS = {

    "mcpagentbench": [

        ("Tool Correctness", "Tool Correctness"),

        ("Argument Correctness [Reference]", "Argument Correctness"),

        ("Final State (Derived)", "Final State"),

    ],

    "bfcl_multiturn": [

        ("Tool Correctness", "Tool Correctness"),

        ("Argument Correctness [Reference]", "Argument Correctness"),

        ("State Match", "State Match"),

    ],
}
def plot_5_1(all_data, fmt):

    print("\n=== 5.1 Core Comparison ===")

    for benchmark in BENCHMARKS:

        agents = available_agents_for_benchmark(all_data, benchmark)

        bname = BENCH_NAMES[benchmark]

        for metric_key, metric_label in CORE_METRICS[benchmark]:

            model_data = {}

            for model in MODELS:

                agent_aggs = {}

                for a in agents:

                    ag = agg_metric(all_data, model, benchmark, a, metric_key)

                    if ag:

                        agent_aggs[a] = ag

                if agent_aggs:

                    model_data[model] = agent_aggs

            tag = metric_label.lower().replace(" ", "_")

            grouped_bar_plot(agents, model_data, metric_label,

                             f"{bname} -- {metric_label} (Modellvergleich)",

                             DIRS["5_1_overall"],

                             f"{tag}_{benchmark}.{fmt}",

                             ylim_max=1.05)

            agent_comparison_plot(agents, model_data, metric_label,

                                  f"{bname} -- {metric_label} (Architekturvergleich)",

                                  DIRS["5_1_overall"],

                                  f"{tag}_{benchmark}_by_agent.{fmt}",

                                  ylim_max=1.05)

            model_tool_data = {}

            for model in MODELS:

                agent_td = {}

                for a in agents:

                    td = {}

                    for t in TOOL_COUNTS:

                        ag = agg_metric(all_data, model, benchmark, a, metric_key, t)

                        if ag:

                            td[t] = ag

                    if td:

                        agent_td[a] = td

                if agent_td:

                    model_tool_data[model] = agent_td

            scaling_subplots(agents, model_tool_data, metric_label,

                             f"{bname} -- {metric_label} (Architekturvergleich)",

                             DIRS["5_1_skal"],

                             f"scaling_{tag}_{benchmark}.{fmt}",

                             ylim=(0, 1.05))

            scaling_model_subplots(agents, model_tool_data, metric_label,

                                    f"{bname} -- {metric_label} (Modellvergleich)",

                                    DIRS["5_1_skal"],

                                    f"scaling_{tag}_{benchmark}_by_model.{fmt}",

                                    ylim=(0, 1.05))
def plot_5_2(all_data, fmt):

    print("\n=== 5.2 Kosten & Tokens ===")

    for benchmark in BENCHMARKS:

        agents = available_agents_for_benchmark(all_data, benchmark)

        bname = BENCH_NAMES[benchmark]

        n_agents = len(agents)

        n_models = len(MODELS)

        bar_width = 0.7 / n_models

        fig, ax = plt.subplots(figsize=(max(10, n_agents * 2.2), 6))

        x = np.arange(n_agents)

        has_data = False

        for j, model in enumerate(MODELS):

            prompt_m, comp_m = [], []

            for a in agents:

                td = agg_tokens(all_data, model, benchmark, a)

                if td is not None:

                    prompt_m.append(float(np.mean(td["prompt"])))

                    comp_m.append(float(np.mean(td["completion"])))

                else:

                    prompt_m.append(0)

                    comp_m.append(0)

            if any(p > 0 for p in prompt_m):

                has_data = True

                offset = (j - n_models / 2 + 0.5) * bar_width

                ax.bar(x + offset, prompt_m, bar_width * 0.9,

                       color=MODEL_COLORS[model], alpha=0.85,

                       edgecolor="black", linewidth=0.5,

                       hatch=MODEL_HATCHES.get(model, ""),

                       label=f"{MODEL_DISPLAY[model]} (Prompt)")

                ax.bar(x + offset, comp_m, bar_width * 0.9,

                       bottom=prompt_m, color=MODEL_COLORS[model], alpha=0.5,

                       edgecolor="black", linewidth=0.5,

                       hatch=MODEL_HATCHES.get(model, ""))

                for i, (p, c) in enumerate(zip(prompt_m, comp_m)):

                    total = p + c

                    if total > 0:

                        ax.text(x[i] + offset, total + total * 0.02,

                                f"{total/1000:.0f}k", ha="center", va="bottom",

                                fontsize=6, fontweight="bold")

        if has_data:

            ax.set_xticks(x)

            ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

            ax.set_ylabel("Tokens / Test Case")

            ax.set_title(f"{bname} -- Token-Verbrauch")

            ax.legend(loc="upper right", fontsize=8)

            ax.yaxis.set_major_formatter(mticker.FuncFormatter(

                lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))

            plt.tight_layout()

            _save(fig, DIRS["5_2_overall"], f"tokens_{benchmark}.{fmt}")

        else:

            plt.close(fig)

        model_data = {}

        for model in MODELS:

            agent_aggs = {}

            for a in agents:

                e = agg_efficiency(all_data, model, benchmark, a)

                if e is not None:

                    agent_aggs[a] = {"mean": e, "ci_lo": e, "ci_hi": e}

            if agent_aggs:

                model_data[model] = agent_aggs

        if model_data:

            grouped_bar_plot(agents, model_data, "Passed TCs / 1k Tokens",

                             f"{bname} -- Token-Effizienz (Modellvergleich)",

                             DIRS["5_2_overall"],

                             f"efficiency_{benchmark}.{fmt}", fmt_val=".4f")

            agent_comparison_plot(agents, model_data, "Passed TCs / 1k Tokens",

                                  f"{bname} -- Token-Effizienz (Architekturvergleich)",

                                  DIRS["5_2_overall"],

                                  f"efficiency_{benchmark}_by_agent.{fmt}", fmt_val=".4f")

        model_data = {}

        for model in MODELS:

            agent_aggs = {}

            for a in agents:

                ag = agg_token_overhead(all_data, model, benchmark, a)

                if ag:

                    agent_aggs[a] = ag

            if agent_aggs:

                model_data[model] = agent_aggs

        if model_data:

            grouped_bar_plot(agents, model_data, "Token Overhead Score",

                             f"{bname} -- Token Overhead (Modellvergleich)",

                             DIRS["5_2_overall"],

                             f"token_overhead_{benchmark}.{fmt}",

                             ylim_max=1.05)

            agent_comparison_plot(agents, model_data, "Token Overhead Score",

                                  f"{bname} -- Token Overhead (Architekturvergleich)",

                                  DIRS["5_2_overall"],

                                  f"token_overhead_{benchmark}_by_agent.{fmt}",

                                  ylim_max=1.05)

        model_tool_data = {}

        for model in MODELS:

            agent_td = {}

            for a in agents:

                td = {}

                for t in TOOL_COUNTS:

                    tok = agg_tokens(all_data, model, benchmark, a, t)

                    if tok is not None:

                        total = tok["prompt"] + tok["completion"]

                        mean = float(np.mean(total))

                        n = len(total)

                        se = float(np.std(total, ddof=1) / np.sqrt(n)) if n > 1 else 0

                        td[t] = {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

                                 "ci_hi": mean + 1.96 * se}

                if td:

                    agent_td[a] = td

            if agent_td:

                model_tool_data[model] = agent_td

        if model_tool_data:

            models_with_data = [m for m in MODELS if m in model_tool_data]

            n = len(models_with_data)

            fig, axes = plt.subplots(1, n, figsize=(6 * n, 5.5), sharey=False)

            if n == 1:

                axes = [axes]

            for ax, model in zip(axes, models_with_data):

                for agent in agents:

                    data = model_tool_data[model].get(agent, {})

                    if not data:

                        continue

                    tools = sorted(data.keys())

                    means = [data[t_]["mean"] for t_ in tools]

                    ci_lo = [data[t_]["ci_lo"] for t_ in tools]

                    ci_hi = [data[t_]["ci_hi"] for t_ in tools]

                    color = AGENT_COLORS.get(agent, "#95a5a6")

                    marker = AGENT_MARKERS.get(agent, "o")

                    ax.plot(tools, means, color=color, marker=marker, markersize=6,

                            linewidth=2, label=AGENT_NAMES.get(agent, agent))

                    ax.fill_between(tools, ci_lo, ci_hi, alpha=0.12, color=color)

                    for t_, m in zip(tools, means):

                        ax.annotate(f"{m/1000:.0f}k", xy=(t_, m), xytext=(0, 7),

                                    textcoords="offset points", ha="center", va="bottom",

                                    fontsize=7, color=color, fontweight="bold")

                ax.set_xlabel("Number of Tools")

                ax.set_title(MODEL_DISPLAY[model])

                ax.set_xticks(TOOL_COUNTS)

                ax.set_ylim(0)

                ax.yaxis.set_major_formatter(mticker.FuncFormatter(

                    lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))

            axes[0].set_ylabel("Total Tokens / TC")

            axes[0].legend(loc="upper left", framealpha=0.9, fontsize=8)

            fig.suptitle(f"{bname} -- Token-Skalierung (Architekturvergleich)", fontsize=14,

                         fontweight="bold")

            plt.tight_layout(rect=[0, 0, 1, 0.95])

            _save(fig, DIRS["5_2_skal"], f"scaling_tokens_{benchmark}.{fmt}")

            valid_agents = [a for a in agents if any(

                a in model_tool_data.get(m, {}) for m in MODELS)]

            if valid_agents:

                na = len(valid_agents)

                fig2, axes2 = plt.subplots(1, na, figsize=(5 * na, 5.5), sharey=False)

                if na == 1:

                    axes2 = [axes2]

                for ax2, agent in zip(axes2, valid_agents):

                    for model in MODELS:

                        data = model_tool_data.get(model, {}).get(agent, {})

                        if not data:

                            continue

                        tools = sorted(data.keys())

                        means = [data[t_]["mean"] for t_ in tools]

                        ci_lo = [data[t_]["ci_lo"] for t_ in tools]

                        ci_hi = [data[t_]["ci_hi"] for t_ in tools]

                        color = MODEL_COLORS[model]

                        ax2.plot(tools, means, color=color, marker="o", markersize=6,

                                 linewidth=2, label=MODEL_DISPLAY[model],

                                 linestyle="--" if "deepseek" in model else "-")

                        ax2.fill_between(tools, ci_lo, ci_hi, alpha=0.12, color=color)

                        for t_, m_ in zip(tools, means):

                            ax2.annotate(f"{m_/1000:.0f}k", xy=(t_, m_), xytext=(0, 7),

                                         textcoords="offset points", ha="center", va="bottom",

                                         fontsize=7, color=color, fontweight="bold")

                    ax2.set_xlabel("Number of Tools")

                    ax2.set_title(AGENT_NAMES.get(agent, agent))

                    ax2.set_xticks(TOOL_COUNTS)

                    ax2.set_ylim(0)

                    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(

                        lambda v, _: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}"))

                axes2[0].set_ylabel("Total Tokens / TC")

                axes2[0].legend(loc="upper left", framealpha=0.9, fontsize=8)

                fig2.suptitle(f"{bname} -- Token-Skalierung (Modellvergleich)",

                              fontsize=14, fontweight="bold")

                plt.tight_layout(rect=[0, 0, 1, 0.95])

                _save(fig2, DIRS["5_2_skal"], f"scaling_tokens_{benchmark}_by_model.{fmt}")

        model_tool_data = {}

        for model in MODELS:

            agent_td = {}

            for a in agents:

                td = {}

                for t in TOOL_COUNTS:

                    ag = agg_token_overhead(all_data, model, benchmark, a, t)

                    if ag:

                        td[t] = ag

                if td:

                    agent_td[a] = td

            if agent_td:

                model_tool_data[model] = agent_td

        if model_tool_data:

            scaling_subplots(agents, model_tool_data, "Token Overhead Score",

                             f"{bname} -- Token Overhead (Architekturvergleich)",

                             DIRS["5_2_skal"],

                             f"scaling_token_overhead_{benchmark}.{fmt}",

                             ylim=(0, 1.05))

            scaling_model_subplots(agents, model_tool_data, "Token Overhead Score",

                                    f"{bname} -- Token Overhead (Modellvergleich)",

                                    DIRS["5_2_skal"],

                                    f"scaling_token_overhead_{benchmark}_by_model.{fmt}",

                                    ylim=(0, 1.05))
def plot_5_3(all_data, fmt):

    print("\n=== 5.3 Latenz ===")

    for benchmark in BENCHMARKS:

        agents = available_agents_for_benchmark(all_data, benchmark)

        bname = BENCH_NAMES[benchmark]

        model_data = {}

        for model in MODELS:

            agent_aggs = {}

            for a in agents:

                ag = agg_latency(all_data, model, benchmark, a)

                if ag:

                    agent_aggs[a] = ag

            if agent_aggs:

                model_data[model] = agent_aggs

        if model_data:

            grouped_bar_plot(agents, model_data, "Avg. Latency / TC (s)",

                             f"{bname} -- Latenz (Modellvergleich)",

                             DIRS["5_3_overall"],

                             f"latency_{benchmark}.{fmt}",

                             fmt_val=".1f", suffix="s")

            agent_comparison_plot(agents, model_data, "Avg. Latency / TC (s)",

                                  f"{bname} -- Latenz (Architekturvergleich)",

                                  DIRS["5_3_overall"],

                                  f"latency_{benchmark}_by_agent.{fmt}",

                                  fmt_val=".1f", suffix="s")

        model_tool_data = {}

        for model in MODELS:

            agent_td = {}

            for a in agents:

                td = {}

                for t in TOOL_COUNTS:

                    ag = agg_latency(all_data, model, benchmark, a, t)

                    if ag:

                        td[t] = ag

                if td:

                    agent_td[a] = td

            if agent_td:

                model_tool_data[model] = agent_td

        if model_tool_data:

            scaling_subplots(agents, model_tool_data, "Avg. Latency / TC (s)",

                             f"{bname} -- Latenz (Architekturvergleich)",

                             DIRS["5_3_skal"],

                             f"scaling_latency_{benchmark}.{fmt}",

                             fmt_val=".1f", suffix="s")

            scaling_model_subplots(agents, model_tool_data, "Avg. Latency / TC (s)",

                                    f"{bname} -- Latenz (Modellvergleich)",

                                    DIRS["5_3_skal"],

                                    f"scaling_latency_{benchmark}_by_model.{fmt}",

                                    fmt_val=".1f", suffix="s")

        gpt_models = ["gpt-5.4-mini", "june-gpt-5-4-datazone"]

        gpt_data = {m: v for m, v in model_data.items() if m in gpt_models} if model_data else {}

        if len(gpt_data) == 2:

            grouped_bar_plot(agents, gpt_data, "Avg. Latency / TC (s)",

                             f"{bname} -- Latenz GPT-5.4 vs GPT-5.4-mini (Modellvergleich)",

                             DIRS["5_3_overall"],

                             f"latency_{benchmark}_gpt_only.{fmt}",

                             fmt_val=".1f", suffix="s")

            agent_comparison_plot(agents, gpt_data, "Avg. Latency / TC (s)",

                                  f"{bname} -- Latenz GPT-5.4 vs GPT-5.4-mini (Architekturvergleich)",

                                  DIRS["5_3_overall"],

                                  f"latency_{benchmark}_gpt_only_by_agent.{fmt}",

                                  fmt_val=".1f", suffix="s")

        gpt_tool_data = {m: v for m, v in model_tool_data.items() if m in gpt_models} if model_tool_data else {}

        if len(gpt_tool_data) == 2:

            scaling_subplots(agents, gpt_tool_data, "Avg. Latency / TC (s)",

                             f"{bname} -- Latenz GPT-5.4 vs GPT-5.4-mini (Skalierung)",

                             DIRS["5_3_skal"],

                             f"scaling_latency_{benchmark}_gpt_only.{fmt}",

                             fmt_val=".1f", suffix="s")
def plot_5_4(all_data, fmt):

    print("\n=== 5.4 Benchmark-spezifisch ===")

    agents = available_agents_for_benchmark(all_data, "mcpagentbench")

    model_data = {}

    for model in MODELS:

        agent_aggs = {}

        for a in agents:

            scores = []

            for r in _filter(all_data, model, "mcpagentbench", a):

                for tc in r.get("test_cases", []):

                    ee = tc.get("metrics", {}).get("Execution Efficiency", {})

                    s = ee.get("score")

                    if s is not None:

                        scores.append(float(s))

            if scores:

                arr = np.array(scores)

                n = len(arr)

                mean = float(np.mean(arr))

                se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

                agent_aggs[a] = {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

                                 "ci_hi": min(1, mean + 1.96 * se)}

        if agent_aggs:

            model_data[model] = agent_aggs

    if model_data:

        grouped_bar_plot(agents, model_data, "Execution Efficiency",

                         "MCPAgentBench -- Exec. Efficiency (Modellvergleich)",

                         DIRS["5_4_overall"],

                         f"exec_efficiency_mcpagentbench.{fmt}",

                         ylim_max=1.05)

        agent_comparison_plot(agents, model_data, "Execution Efficiency",

                              "MCPAgentBench -- Exec. Efficiency (Architekturvergleich)",

                              DIRS["5_4_overall"],

                              f"exec_efficiency_mcpagentbench_by_agent.{fmt}",

                              ylim_max=1.05)

    model_tool_data = {}

    for model in MODELS:

        agent_td = {}

        for a in agents:

            td = {}

            for t in TOOL_COUNTS:

                ag = agg_metric(all_data, model, "mcpagentbench", a, "Execution Efficiency", t)

                if ag:

                    td[t] = ag

            if td:

                agent_td[a] = td

        if agent_td:

            model_tool_data[model] = agent_td

    if model_tool_data:

        scaling_subplots(agents, model_tool_data, "Execution Efficiency",

                         "MCPAgentBench -- Exec. Efficiency (Architekturvergleich)",

                         DIRS["5_4_skal"],

                         f"scaling_exec_efficiency_mcpagentbench.{fmt}",

                         ylim=(0, 1.05))

        scaling_model_subplots(agents, model_tool_data, "Execution Efficiency",

                                "MCPAgentBench -- Exec. Efficiency (Modellvergleich)",

                                DIRS["5_4_skal"],

                                f"scaling_exec_efficiency_mcpagentbench_by_model.{fmt}",

                                ylim=(0, 1.05))

    agents_bfcl = available_agents_for_benchmark(all_data, "bfcl_multiturn")

    model_data = {}

    for model in MODELS:

        agent_aggs = {}

        for a in agents_bfcl:

            counts = []

            for r in _filter(all_data, model, "bfcl_multiturn", a):

                for tc in r.get("test_cases", []):

                    cnt = tc.get("metrics", {}).get("Tool Correctness", {}).get("cross_turn_redundant_count")

                    if cnt is not None:

                        counts.append(float(cnt))

            if counts:

                arr = np.array(counts)

                n = len(arr)

                mean = float(np.mean(arr))

                se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

                agent_aggs[a] = {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

                                 "ci_hi": mean + 1.96 * se}

        if agent_aggs:

            model_data[model] = agent_aggs

    if model_data:

        grouped_bar_plot(agents_bfcl, model_data, "Avg. Cross-Turn Redundant Calls / TC",

                         "BFCL Multiturn -- Cross-Turn Redundancy (Modellvergleich)",

                         DIRS["5_4_overall"],

                         f"cross_turn_redundancy_bfcl_multiturn.{fmt}")

        agent_comparison_plot(agents_bfcl, model_data, "Avg. Cross-Turn Redundant Calls / TC",

                              "BFCL Multiturn -- Cross-Turn Redundancy (Architekturvergleich)",

                              DIRS["5_4_overall"],

                              f"cross_turn_redundancy_bfcl_multiturn_by_agent.{fmt}")

    model_tool_data = {}

    for model in MODELS:

        agent_td = {}

        for a in agents_bfcl:

            td = {}

            for t in TOOL_COUNTS:

                counts = []

                for r in _filter(all_data, model, "bfcl_multiturn", a, t):

                    for tc in r.get("test_cases", []):

                        cnt = tc.get("metrics", {}).get("Tool Correctness", {}).get("cross_turn_redundant_count")

                        if cnt is not None:

                            counts.append(float(cnt))

                if counts:

                    arr = np.array(counts)

                    n = len(arr)

                    mean = float(np.mean(arr))

                    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

                    td[t] = {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

                             "ci_hi": mean + 1.96 * se}

            if td:

                agent_td[a] = td

        if agent_td:

            model_tool_data[model] = agent_td

    if model_tool_data:

        scaling_subplots(agents_bfcl, model_tool_data,

                         "Avg. Cross-Turn Redundant Calls / TC",

                         "BFCL -- Cross-Turn Redundancy (Architekturvergleich)",

                         DIRS["5_4_skal"],

                         f"scaling_cross_turn_redundancy_bfcl_multiturn.{fmt}")

        scaling_model_subplots(agents_bfcl, model_tool_data,

                                "Avg. Cross-Turn Redundant Calls / TC",

                                "BFCL -- Cross-Turn Redundancy (Modellvergleich)",

                                DIRS["5_4_skal"],

                                f"scaling_cross_turn_redundancy_bfcl_multiturn_by_model.{fmt}")

    fig, axes = plt.subplots(1, len(MODELS), figsize=(6 * len(MODELS), 5), sharey=True)

    has_any = False

    for ax, model in zip(axes, MODELS):

        for a in agents_bfcl:

            turn_scores = {}

            for r in _filter(all_data, model, "bfcl_multiturn", a):

                for tc in r.get("test_cases", []):

                    per_turn = tc.get("metrics", {}).get("Tool Correctness", {}).get("per_turn", [])

                    for entry in per_turn:

                        t_idx = entry.get("turn")

                        s = entry.get("score")

                        if t_idx is not None and s is not None:

                            turn_scores.setdefault(t_idx, []).append(float(s))

            if not turn_scores:

                continue

            has_any = True

            turns = sorted(turn_scores.keys())

            means = [float(np.mean(turn_scores[t])) for t in turns]

            color = AGENT_COLORS.get(a, "#95a5a6")

            marker = AGENT_MARKERS.get(a, "o")

            ax.plot(turns, means, color=color, marker=marker, markersize=6,

                    linewidth=2, label=AGENT_NAMES.get(a, a))

        ax.set_xlabel("Turn")

        ax.set_title(MODEL_DISPLAY[model])

        ax.set_ylim(0, 1.05)

    if has_any:

        axes[0].set_ylabel("Tool Correctness")

        axes[0].legend(loc="best", framealpha=0.9, fontsize=8)

        fig.suptitle("BFCL Multiturn -- TC per Turn", fontsize=14,

                     fontweight="bold", y=1.02)

        plt.tight_layout()

        _save(fig, DIRS["5_4_overall"], f"tc_per_turn_bfcl_multiturn.{fmt}")

    else:

        plt.close(fig)
def main():

    parser = argparse.ArgumentParser(description="Generate all thesis plots")

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    plot_5_1(all_data, args.format)

    plot_5_2(all_data, args.format)

    plot_5_3(all_data, args.format)

    plot_5_4(all_data, args.format)

    print("\nDone.")
if __name__ == "__main__":

    main()

