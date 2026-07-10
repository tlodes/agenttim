"""
Task type / mode breakdown plots and LaTeX tables.
Shows Tool Correctness per task type (mode) for each benchmark,
grouped by agent architecture, aggregated across all models and tool counts.
Output:
  plots/5_4_benchmark_spezifisch/overall/task_types_mcpagentbench.png
  plots/5_4_benchmark_spezifisch/overall/task_types_bfcl_multiturn.png
  results/5_4_task_types_tables.tex
Usage:
    cd agenttim/evaluation
    python scripts/plot_task_types.py
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({

    "font.size": 11, "font.family": "serif", "axes.titlesize": 13,

    "axes.labelsize": 12, "xtick.labelsize": 10, "ytick.labelsize": 10,

    "legend.fontsize": 9, "figure.dpi": 150, "savefig.dpi": 300,

    "savefig.bbox": "tight", "savefig.pad_inches": 0.1,
})
BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_enriched"
PLOT_DIR = BASE / "plots" / "5_4_benchmark_spezifisch" / "overall"
OUTPUT_DIR = BASE / "results"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent", "orchestrator_fine": "Orch. (Fine)",

    "orchestrator_coarse": "Orch. (Coarse)", "router": "Router", "swarm": "Swarm",
}
AGENT_NAMES_TEX = {

    "single": "Single Agent", "orchestrator_fine": "Orch.\\ (Fine)",

    "orchestrator_coarse": "Orch.\\ (Coarse)", "router": "Router", "swarm": "Swarm",
}
AGENT_COLORS = {

    "single": "#2ecc71", "orchestrator_fine": "#3498db",

    "orchestrator_coarse": "#9b59b6", "router": "#e74c3c", "swarm": "#f39c12",
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
MCP_MODE_DISPLAY = {

    "sturn-1t-daytasks": "1T Day",

    "sturn-1t-protasks": "1T Pro",

    "sturn-mt-daytasks-sequential": "MT Day Seq",

    "sturn-mt-daytasks-parallel": "MT Day Par",

    "sturn-mt-daytasks-3tools": "MT Day 3T",

    "sturn-mt-protasks-sequential": "MT Pro Seq",

    "sturn-mt-protasks-parallel": "MT Pro Par",

    "sturn-mt-protasks-3tools": "MT Pro 3T",
}
MCP_MODE_ORDER = [

    "sturn-1t-daytasks", "sturn-1t-protasks",

    "sturn-mt-daytasks-sequential", "sturn-mt-daytasks-parallel", "sturn-mt-daytasks-3tools",

    "sturn-mt-protasks-sequential", "sturn-mt-protasks-parallel", "sturn-mt-protasks-3tools",
]
BFCL_MODE_DISPLAY = {"base": "Base", "long_context": "Long Context"}
BFCL_MODE_ORDER = ["base", "long_context"]
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
def get_scores_by_mode(all_data, benchmark, agent, metric_key, mode):

    """Get metric scores for a specific mode, aggregated across all models and tool counts."""

    scores = []

    for r in all_data:

        if (r.get("benchmark") != benchmark or r.get("agent_type") != agent

                or r.get("mode") != mode):

            continue

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric_key, {}).get("score")

            if s is not None:

                scores.append(float(s))

    return scores
def get_scores_by_mode_model(all_data, model, benchmark, agent, metric_key, mode):

    """Get metric scores for a specific mode and model."""

    scores = []

    for r in all_data:

        if (r.get("model") != model or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent or r.get("mode") != mode):

            continue

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric_key, {}).get("score")

            if s is not None:

                scores.append(float(s))

    return scores
def agg(scores):

    if not scores:

        return None

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return {"mean": mean, "ci_lo": max(0, mean - 1.96 * se),

            "ci_hi": min(1, mean + 1.96 * se), "n": n}
def _save(fig, path):

    path.parent.mkdir(parents=True, exist_ok=True)

    fig.savefig(path)

    plt.close(fig)

    print(f"  Saved: {path.relative_to(BASE)}")
def _best_idx(values, higher_is_better=True):

    valid = [(i, v) for i, v in enumerate(values) if v is not None]

    if not valid:

        return set()

    best = max(v for _, v in valid) if higher_is_better else min(v for _, v in valid)

    return {i for i, v in valid if abs(v - best) < 1e-9}
def plot_task_types(all_data, fmt):

    """Grouped bar: modes on x-axis, bars per agent architecture."""

    for benchmark, mode_order, mode_display in [

        ("mcpagentbench", MCP_MODE_ORDER, MCP_MODE_DISPLAY),

        ("bfcl_multiturn", BFCL_MODE_ORDER, BFCL_MODE_DISPLAY),

    ]:

        available_modes = [m for m in mode_order if any(

            r.get("benchmark") == benchmark and r.get("mode") == m for r in all_data)]

        agents = [a for a in AGENT_ORDER if any(

            r.get("benchmark") == benchmark and r.get("agent_type") == a for r in all_data)]

        if not available_modes or not agents:

            continue

        n_modes = len(available_modes)

        n_agents = len(agents)

        bar_width = 0.8 / n_agents

        x = np.arange(n_modes)

        fig, ax = plt.subplots(figsize=(max(12, n_modes * 1.8), 6.5))

        for j, agent in enumerate(agents):

            means, ci_lows, ci_highs = [], [], []

            for mode in available_modes:

                scores = get_scores_by_mode(all_data, benchmark, agent, "Tool Correctness", mode)

                st = agg(scores)

                if st:

                    means.append(st["mean"])

                    ci_lows.append(st["mean"] - st["ci_lo"])

                    ci_highs.append(st["ci_hi"] - st["mean"])

                else:

                    means.append(0)

                    ci_lows.append(0)

                    ci_highs.append(0)

            offset = (j - n_agents / 2 + 0.5) * bar_width

            bars = ax.bar(x + offset, means, bar_width * 0.9,

                          yerr=[ci_lows, ci_highs], capsize=2,

                          color=AGENT_COLORS.get(agent, "#95a5a6"), alpha=0.85,

                          edgecolor="black", linewidth=0.4,

                          error_kw={"elinewidth": 0.7, "capthick": 0.7},

                          label=AGENT_NAMES.get(agent, agent))

            for bar, val in zip(bars, means):

                if val > 0:

                    ax.text(bar.get_x() + bar.get_width() / 2,

                            bar.get_height() + 0.02,

                            f"{val:.2f}", ha="center", va="bottom",

                            fontsize=6, fontweight="bold", rotation=90)

        ax.set_xticks(x)

        ax.set_xticklabels([mode_display.get(m, m) for m in available_modes],

                           rotation=30, ha="right")

        ax.set_ylabel("Tool Correctness")

        bname = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}[benchmark]

        ax.set_title(f"{bname} -- Tool Correctness nach Aufgabentyp")

        ax.set_ylim(0, 1.15)

        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),

                  ncol=min(n_agents, 3), framealpha=0.9, fontsize=8)

        plt.tight_layout()

        _save(fig, PLOT_DIR / f"task_types_{benchmark}.{fmt}")

    for model in MODELS:

        available_modes = [m for m in MCP_MODE_ORDER if any(

            r.get("benchmark") == "mcpagentbench" and r.get("mode") == m

            and r.get("model") == model for r in all_data)]

        agents = [a for a in AGENT_ORDER if any(

            r.get("benchmark") == "mcpagentbench" and r.get("agent_type") == a

            and r.get("model") == model for r in all_data)]

        if not available_modes or not agents:

            continue

        n_modes = len(available_modes)

        n_agents = len(agents)

        bar_width = 0.8 / n_agents

        x = np.arange(n_modes)

        fig, ax = plt.subplots(figsize=(max(12, n_modes * 1.8), 6.5))

        for j, agent in enumerate(agents):

            means, ci_lows, ci_highs = [], [], []

            for mode in available_modes:

                scores = get_scores_by_mode_model(all_data, model, "mcpagentbench", agent,

                                                   "Tool Correctness", mode)

                st = agg(scores)

                if st:

                    means.append(st["mean"])

                    ci_lows.append(st["mean"] - st["ci_lo"])

                    ci_highs.append(st["ci_hi"] - st["mean"])

                else:

                    means.append(0)

                    ci_lows.append(0)

                    ci_highs.append(0)

            offset = (j - n_agents / 2 + 0.5) * bar_width

            ax.bar(x + offset, means, bar_width * 0.9,

                   yerr=[ci_lows, ci_highs], capsize=2,

                   color=AGENT_COLORS.get(agent, "#95a5a6"), alpha=0.85,

                   edgecolor="black", linewidth=0.4,

                   error_kw={"elinewidth": 0.7, "capthick": 0.7},

                   label=AGENT_NAMES.get(agent, agent))

        ax.set_xticks(x)

        ax.set_xticklabels([MCP_MODE_DISPLAY.get(m, m) for m in available_modes],

                           rotation=30, ha="right")

        ax.set_ylabel("Tool Correctness")

        mdisp = MODEL_DISPLAY[model]

        ax.set_title(f"{mdisp} -- MCPAgentBench: TC nach Aufgabentyp")

        ax.set_ylim(0, 1.15)

        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),

                  ncol=min(n_agents, 3), framealpha=0.9, fontsize=8)

        plt.tight_layout()

        mfk = MODEL_FK[model]

        _save(fig, PLOT_DIR / f"task_types_{mfk}_mcpagentbench.{fmt}")
def gen_tables(all_data):

    lines = ["% Auto-generated: Task Type Breakdown Tables", ""]

    for benchmark, mode_order, mode_display, bname in [

        ("mcpagentbench", MCP_MODE_ORDER, MCP_MODE_DISPLAY, "MCPAgentBench"),

        ("bfcl_multiturn", BFCL_MODE_ORDER, BFCL_MODE_DISPLAY, "BFCL Multiturn"),

    ]:

        agents = [a for a in AGENT_ORDER if any(

            r.get("benchmark") == benchmark and r.get("agent_type") == a for r in all_data)]

        available_modes = [m for m in mode_order if any(

            r.get("benchmark") == benchmark and r.get("mode") == m for r in all_data)]

        if not available_modes or not agents:

            continue

        lines.append(f"% === {bname}: TC nach Aufgabentyp (aggregiert) ===")

        lines.append("\\begin{table}[htbp]")

        lines.append("  \\centering")

        lines.append(f"  \\caption{ {bname}: Tool Correctness nach Aufgabentyp, aggregiert ueber alle Modelle und Tool-Stufen.} ")

        lines.append(f"  \\label{ tab:task-types-{benchmark}} ")

        agent_cols = " ".join(["r"] * len(agents))

        lines.append(f"  \\begin{ tabular} { l r {agent_cols}} ")

        lines.append("    \\toprule")

        agent_headers = " & ".join([AGENT_NAMES_TEX[a] for a in agents])

        lines.append(f"    Aufgabentyp & $n$ & {agent_headers} \\\\")

        lines.append("    \\midrule")

        for mode in available_modes:

            agent_means = []

            first_n = 0

            for a in agents:

                scores = get_scores_by_mode(all_data, benchmark, a, "Tool Correctness", mode)

                st = agg(scores)

                if st:

                    agent_means.append(st["mean"])

                    if first_n == 0:

                        first_n = st["n"]

                else:

                    agent_means.append(None)

            best = _best_idx(agent_means, higher_is_better=True)

            mdisp = mode_display.get(mode, mode)

            parts = [mdisp, str(first_n)]

            for i, v in enumerate(agent_means):

                if v is not None:

                    val = f"{v:.3f}"

                    if i in best:

                        val = f"\\textbf{ {val}} "

                    parts.append(f"${val}$")

                else:

                    parts.append("--")

            lines.append(f"    {' & '.join(parts)} \\\\")

        lines.append("    \\bottomrule")

        lines.append("  \\end{tabular}")

        lines.append("  \\par\\footnotesize{\\textbf{Fett} = bester Wert pro Aufgabentyp.}")

        lines.append("\\end{table}")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            mfk = MODEL_FK[model]

            model_agents = [a for a in AGENT_ORDER if any(

                r.get("benchmark") == benchmark and r.get("agent_type") == a

                and r.get("model") == model for r in all_data)]

            model_modes = [m for m in mode_order if any(

                r.get("benchmark") == benchmark and r.get("mode") == m

                and r.get("model") == model for r in all_data)]

            if not model_agents or not model_modes:

                continue

            lines.append(f"% === {mdisp} x {bname}: TC nach Aufgabentyp ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Tool Correctness nach Aufgabentyp.} ")

            lines.append(f"  \\label{ tab:task-types-{mfk}-{benchmark}} ")

            agent_cols = " ".join(["r"] * len(model_agents))

            lines.append(f"  \\begin{ tabular} { l r {agent_cols}} ")

            lines.append("    \\toprule")

            agent_headers = " & ".join([AGENT_NAMES_TEX[a] for a in model_agents])

            lines.append(f"    Aufgabentyp & $n$ & {agent_headers} \\\\")

            lines.append("    \\midrule")

            for mode in model_modes:

                agent_means = []

                first_n = 0

                for a in model_agents:

                    scores = get_scores_by_mode_model(all_data, model, benchmark, a,

                                                       "Tool Correctness", mode)

                    st = agg(scores)

                    if st:

                        agent_means.append(st["mean"])

                        if first_n == 0:

                            first_n = st["n"]

                    else:

                        agent_means.append(None)

                best = _best_idx(agent_means, higher_is_better=True)

                md = mode_display.get(mode, mode)

                parts = [md, str(first_n)]

                for i, v in enumerate(agent_means):

                    if v is not None:

                        val = f"{v:.3f}"

                        if i in best:

                            val = f"\\textbf{ {val}} "

                        parts.append(f"${val}$")

                    else:

                        parts.append("--")

                lines.append(f"    {' & '.join(parts)} \\\\")

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\par\\footnotesize{\\textbf{Fett} = bester Wert pro Aufgabentyp.}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--format", "-f", default="png", choices=["png", "pdf", "svg"])

    args = parser.parse_args()

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\n--- Task Type Plots ---")

    plot_task_types(all_data, args.format)

    print("\n--- Task Type Tables ---")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tex = gen_tables(all_data)

    out_path = OUTPUT_DIR / "5_4_task_types_tables.tex"

    out_path.write_text(tex, encoding="utf-8")

    print(f"  Saved: {out_path.relative_to(BASE)}")

    import shutil

    plot_tex = BASE / "plots" / "5_4_benchmark_spezifisch" / "5_4_task_types_tables.tex"

    shutil.copy2(out_path, plot_tex)

    print(f"  Copied to: {plot_tex.relative_to(BASE)}")

    print("\nDone.")
if __name__ == "__main__":

    main()

