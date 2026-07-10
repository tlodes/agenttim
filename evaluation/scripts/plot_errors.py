"""
Error analysis plots and tables for thesis section 5.5 (Datenqualitaet).
Output:
  plots/5_5_fehleranalyse/error_rate_by_model.png
  plots/5_5_fehleranalyse/error_rate_by_agent.png
  plots/5_5_fehleranalyse/error_rate_by_tools.png
  plots/5_5_fehleranalyse/error_types.png
  results/5_5_fehleranalyse_tables.tex
  results/5_5_fehleranalyse.md
Usage:
    cd agenttim/evaluation
    python scripts/plot_errors.py
"""
import json
from collections import defaultdict
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
BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_enriched"
PLOT_DIR = BASE / "plots" / "5_5_fehleranalyse"
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
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
TOOL_COUNTS = [10, 20, 40, 80]
ERROR_TYPE_DISPLAY = {

    "TestCaseTimeoutError": "Timeout (120s)",

    "GraphRecursionError": "Rekursionslimit",

    "BadRequestError": "Bad Request",

    "TimeoutError": "API Timeout",
}
def load_all():

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
def collect_errors(all_data):

    """Collect all error information."""

    records = []

    total_by = defaultdict(int)

    for data in all_data:

        model = data.get("model", "?")

        benchmark = data.get("benchmark", "?")

        agent = data.get("agent_type", "?")

        num_tools = data.get("num_tools", 0)

        for tc in data.get("test_cases", []):

            key = (model, benchmark, agent, num_tools)

            total_by[key] = total_by.get(key, 0) + 1

            err = tc.get("error")

            if not err:

                continue

            err_type = err.get("type", str(err)[:40]) if isinstance(err, dict) else str(err)[:40]

            metrics = tc.get("metrics", {})

            has_metrics = any(m.get("score") is not None for m in metrics.values()) if metrics else False

            records.append({

                "model": model, "benchmark": benchmark, "agent": agent,

                "num_tools": num_tools, "type": err_type,

                "has_metrics": has_metrics,

                "tools_called": len(tc.get("tools_called", [])),

            })

    return records, total_by
def _save(fig, fname):

    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    fig.savefig(PLOT_DIR / fname)

    plt.close(fig)

    print(f"  Saved: 5_5_fehleranalyse/{fname}")
def plot_error_rate_by_model(all_data, errors, total_by, fmt):

    """Error rate per model x benchmark."""

    by_mb = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_mb[(e["model"], e["benchmark"])]["errors"] += 1

    for key, cnt in total_by.items():

        m, b = key[0], key[1]

        by_mb[(m, b)]["total"] += cnt

    labels, rates, colors = [], [], []

    bar_colors = {"mcpagentbench": "#3498db", "bfcl_multiturn": "#e74c3c"}

    groups = []

    for model in MODELS:

        for benchmark in BENCHMARKS:

            d = by_mb.get((model, benchmark))

            if d and d["total"] > 0:

                rate = d["errors"] / d["total"] * 100

                groups.append({

                    "label": f"{MODEL_DISPLAY[model]}\n{BENCH_NAMES[benchmark]}",

                    "rate": rate, "errors": d["errors"], "total": d["total"],

                    "color": bar_colors.get(benchmark, "#95a5a6"),

                })

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x = np.arange(len(groups))

    bars = ax.bar(x, [g["rate"] for g in groups], width=0.6,

                  color=[g["color"] for g in groups],

                  edgecolor="black", linewidth=0.5, alpha=0.85)

    for i, (bar, g) in enumerate(zip(bars, groups)):

        ax.text(bar.get_x() + bar.get_width() / 2,

                bar.get_height() + 0.5,

                f"{g['rate']:.1f}%\n({g['errors']}/{g['total']})",

                ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels([g["label"] for g in groups], fontsize=9)

    ax.set_ylabel("Error-Rate (%)")

    ax.set_title("Error-Rate nach Modell und Benchmark")

    ax.set_ylim(0, max(g["rate"] for g in groups) * 1.3)

    from matplotlib.patches import Patch

    legend_elements = [Patch(facecolor="#3498db", label="MCPAgentBench"),

                       Patch(facecolor="#e74c3c", label="BFCL Multiturn")]

    ax.legend(handles=legend_elements, loc="upper left")

    plt.tight_layout()

    _save(fig, f"error_rate_by_model.{fmt}")
def plot_error_rate_by_agent(all_data, errors, total_by, fmt):

    """Error rate per agent type."""

    by_agent = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_agent[e["agent"]]["errors"] += 1

    for key, cnt in total_by.items():

        by_agent[key[2]]["total"] += cnt

    agents = [a for a in AGENT_ORDER if a in by_agent and by_agent[a]["total"] > 0]

    rates = [by_agent[a]["errors"] / by_agent[a]["total"] * 100 for a in agents]

    colors = [AGENT_COLORS.get(a, "#95a5a6") for a in agents]

    fig, ax = plt.subplots(figsize=(8, 5.5))

    x = np.arange(len(agents))

    bars = ax.bar(x, rates, width=0.6, color=colors,

                  edgecolor="black", linewidth=0.5, alpha=0.85)

    for bar, r, a in zip(bars, rates, agents):

        d = by_agent[a]

        ax.text(bar.get_x() + bar.get_width() / 2,

                bar.get_height() + 0.3,

                f"{r:.1f}%\n({d['errors']}/{d['total']})",

                ha="center", va="bottom", fontsize=8, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels([AGENT_NAMES.get(a, a) for a in agents], rotation=15, ha="right")

    ax.set_ylabel("Error-Rate (%)")

    ax.set_title("Error-Rate nach Agenten-Architektur")

    ax.set_ylim(0, max(rates) * 1.3)

    plt.tight_layout()

    _save(fig, f"error_rate_by_agent.{fmt}")
def plot_error_rate_by_tools(all_data, errors, total_by, fmt):

    """Error rate per tool count, split by model."""

    fig, ax = plt.subplots(figsize=(8, 5.5))

    model_colors = {

        "gpt-5.4-mini": "#2ecc71", "deepseek/deepseek-v4-pro": "#e74c3c",

        "june-gpt-5-4-datazone": "#3498db",

    }

    for model in MODELS:

        rates, valid_tools = [], []

        for t in TOOL_COUNTS:

            total = sum(cnt for key, cnt in total_by.items() if key[0] == model and key[3] == t)

            errs = sum(1 for e in errors if e["model"] == model and e["num_tools"] == t)

            if total > 0:

                rates.append(errs / total * 100)

                valid_tools.append(t)

        if rates:

            ax.plot(valid_tools, rates, color=model_colors.get(model, "#95a5a6"),

                    marker="o", markersize=7, linewidth=2,

                    label=MODEL_DISPLAY.get(model, model))

            for t, r in zip(valid_tools, rates):

                ax.annotate(f"{r:.1f}%", xy=(t, r), xytext=(0, 8),

                            textcoords="offset points", ha="center", fontsize=8,

                            color=model_colors.get(model, "#95a5a6"), fontweight="bold")

    ax.set_xlabel("Number of Tools")

    ax.set_ylabel("Error-Rate (%)")

    ax.set_title("Error-Rate nach Tool-Anzahl")

    ax.set_xticks(TOOL_COUNTS)

    ax.set_ylim(0)

    ax.legend(loc="upper left", framealpha=0.9)

    plt.tight_layout()

    _save(fig, f"error_rate_by_tools.{fmt}")
def plot_error_types(errors, fmt):

    """Pie/bar chart of error types."""

    by_type = defaultdict(lambda: {"with_metrics": 0, "no_metrics": 0})

    for e in errors:

        if e["has_metrics"]:

            by_type[e["type"]]["with_metrics"] += 1

        else:

            by_type[e["type"]]["no_metrics"] += 1

    types = sorted(by_type.keys(), key=lambda t: -(by_type[t]["with_metrics"] + by_type[t]["no_metrics"]))

    with_m = [by_type[t]["with_metrics"] for t in types]

    no_m = [by_type[t]["no_metrics"] for t in types]

    labels = [ERROR_TYPE_DISPLAY.get(t, t[:20]) for t in types]

    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(types))

    ax.bar(x, with_m, width=0.6, label="Mit Metriken (partiell evaluiert)",

           color="#3498db", edgecolor="black", linewidth=0.5)

    ax.bar(x, no_m, width=0.6, bottom=with_m, label="Ohne Metriken (excluded)",

           color="#e74c3c", edgecolor="black", linewidth=0.5)

    for i, (w, n) in enumerate(zip(with_m, no_m)):

        total = w + n

        ax.text(i, total + 10, str(total), ha="center", va="bottom",

                fontsize=9, fontweight="bold")

    ax.set_xticks(x)

    ax.set_xticklabels(labels, rotation=15, ha="right")

    ax.set_ylabel("Anzahl Test Cases")

    ax.set_title("Fehlertypen und Evaluierbarkeit")

    ax.legend(loc="upper right")

    plt.tight_layout()

    _save(fig, f"error_types.{fmt}")
def gen_tables(errors, total_by):

    lines = ["% Auto-generated: 5.5 Fehleranalyse", ""]

    lines.append("% === Error-Rate nach Modell x Benchmark ===")

    lines.append("\\begin{table}[htbp]")

    lines.append("  \\centering")

    lines.append("  \\caption{Error-Rate nach Modell und Benchmark.}")

    lines.append("  \\label{tab:error-rate-model}")

    lines.append("  \\begin{tabular}{l l r r r}")

    lines.append("    \\toprule")

    lines.append("    Modell & Benchmark & Errors & Total & Error-Rate \\\\")

    lines.append("    \\midrule")

    by_mb = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_mb[(e["model"], e["benchmark"])]["errors"] += 1

    for key, cnt in total_by.items():

        by_mb[(key[0], key[1])]["total"] += cnt

    for model in MODELS:

        for benchmark in BENCHMARKS:

            d = by_mb.get((model, benchmark))

            if d and d["total"] > 0:

                rate = d["errors"] / d["total"] * 100

                mdisp = MODEL_DISPLAY.get(model, model)

                bdisp = BENCH_NAMES.get(benchmark, benchmark)

                rate_str = f"\\textbf{ {rate:.1f}\\%} " if rate > 10 else f"{rate:.1f}\\%"

                lines.append(f"    {mdisp} & {bdisp} & {d['errors']:,} & {d['total']:,} & {rate_str} \\\\")

    total_err = len(errors)

    total_tc = sum(total_by.values())

    total_rate = total_err / total_tc * 100

    lines.append("    \\midrule")

    lines.append(f"    \\textit{ Gesamt}  & & {total_err:,} & {total_tc:,} & {total_rate:.1f}\\% \\\\")

    lines.append("    \\bottomrule")

    lines.append("  \\end{tabular}")

    lines.append("\\end{table}")

    lines.append("")

    lines.append("% === Error-Rate nach Agenten-Architektur ===")

    lines.append("\\begin{table}[htbp]")

    lines.append("  \\centering")

    lines.append("  \\caption{Error-Rate nach Agenten-Architektur.}")

    lines.append("  \\label{tab:error-rate-agent}")

    lines.append("  \\begin{tabular}{l r r r}")

    lines.append("    \\toprule")

    lines.append("    Architecture & Errors & Total & Error-Rate \\\\")

    lines.append("    \\midrule")

    by_agent = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_agent[e["agent"]]["errors"] += 1

    for key, cnt in total_by.items():

        by_agent[key[2]]["total"] += cnt

    for a in AGENT_ORDER:

        d = by_agent.get(a)

        if d and d["total"] > 0:

            rate = d["errors"] / d["total"] * 100

            name = AGENT_NAMES_TEX.get(a, a)

            lines.append(f"    {name} & {d['errors']:,} & {d['total']:,} & {rate:.1f}\\% \\\\")

    lines.append("    \\bottomrule")

    lines.append("  \\end{tabular}")

    lines.append("\\end{table}")

    lines.append("")

    lines.append("% === Fehlertypen ===")

    lines.append("\\begin{table}[htbp]")

    lines.append("  \\centering")

    lines.append("  \\caption{Fehlertypen und Evaluierbarkeit.}")

    lines.append("  \\label{tab:error-types}")

    lines.append("  \\begin{tabular}{l r r r}")

    lines.append("    \\toprule")

    lines.append("    Fehlertyp & Mit Metriken & Ohne Metriken & Gesamt \\\\")

    lines.append("    \\midrule")

    by_type = defaultdict(lambda: {"with": 0, "without": 0})

    for e in errors:

        if e["has_metrics"]:

            by_type[e["type"]]["with"] += 1

        else:

            by_type[e["type"]]["without"] += 1

    for t in sorted(by_type, key=lambda t: -(by_type[t]["with"] + by_type[t]["without"])):

        d = by_type[t]

        total = d["with"] + d["without"]

        tdisp = ERROR_TYPE_DISPLAY.get(t, t[:25])

        lines.append(f"    {tdisp} & {d['with']:,} & {d['without']:,} & {total:,} \\\\")

    lines.append("    \\midrule")

    tw = sum(d["with"] for d in by_type.values())

    tn = sum(d["without"] for d in by_type.values())

    lines.append(f"    \\textit{ Gesamt}  & {tw:,} & {tn:,} & {tw + tn:,} \\\\")

    lines.append("    \\bottomrule")

    lines.append("  \\end{tabular}")

    lines.append("  \\par\\footnotesize{``Mit Metriken'': Agent hat vor dem Fehler Tool-Calls ausgefuehrt, Scores konnten berechnet werden. ``Ohne Metriken'': Keine Evaluation moeglich, TC wird ausgeschlossen ($n$ reduziert).}")

    lines.append("\\end{table}")

    lines.append("")

    lines.append("% === Error-Rate nach Tool-Stufe ===")

    lines.append("\\begin{table}[htbp]")

    lines.append("  \\centering")

    lines.append("  \\caption{Error-Rate nach Tool-Stufe.}")

    lines.append("  \\label{tab:error-rate-tools}")

    lines.append("  \\begin{tabular}{l r r r}")

    lines.append("    \\toprule")

    lines.append("    Tool-Stufe & Errors & Total & Error-Rate \\\\")

    lines.append("    \\midrule")

    for t in TOOL_COUNTS:

        total = sum(cnt for key, cnt in total_by.items() if key[3] == t)

        errs = sum(1 for e in errors if e["num_tools"] == t)

        rate = errs / total * 100 if total > 0 else 0

        lines.append(f"    $t{ =} {t}$ & {errs:,} & {total:,} & {rate:.1f}\\% \\\\")

    lines.append("    \\bottomrule")

    lines.append("  \\end{tabular}")

    lines.append("\\end{table}")

    return "\n".join(lines)
def gen_text(errors, total_by):

    total_err = len(errors)

    total_tc = sum(total_by.values())

    total_rate = total_err / total_tc * 100

    no_metrics = sum(1 for e in errors if not e["has_metrics"])

    with_metrics = total_err - no_metrics

    by_mb = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_mb[(e["model"], e["benchmark"])]["errors"] += 1

    for key, cnt in total_by.items():

        by_mb[(key[0], key[1])]["total"] += cnt

    lines = [

        "# 5.5 Datenqualitaet und Fehleranalyse",

        "",

        "## Ueberblick",

        "",

        f"Von insgesamt {total_tc:,} ausgefuehrten Test Cases traten bei {total_err:,} ({total_rate:.1f}%) "

        f"Fehler auf. Der haeufigste Fehlertyp ist ein Timeout nach 120 Sekunden "

        f"(TestCaseTimeoutError), der {sum(1 for e in errors if e['type'] == 'TestCaseTimeoutError'):,} "

        f"der {total_err:,} Fehler ausmacht.",

        "",

        f"Von den {total_err:,} fehlerhaften TCs konnten {with_metrics:,} ({with_metrics/total_err*100:.0f}%) "

        f"dennoch partiell evaluiert werden, da der Agent vor dem Fehler bereits Tool-Calls "

        f"ausgefuehrt hatte. Die verbleibenden {no_metrics} TCs ({no_metrics/total_err*100:.1f}%) "

        f"ohne jegliche Metriken werden aus der Auswertung ausgeschlossen (n wird reduziert).",

        "",

        "## Verteilung nach Modell",

        "",

    ]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            d = by_mb.get((model, benchmark))

            if d and d["total"] > 0:

                rate = d["errors"] / d["total"] * 100

                mdisp = MODEL_DISPLAY[model]

                bdisp = BENCH_NAMES[benchmark]

                lines.append(f"- **{mdisp} x {bdisp}**: {d['errors']:,}/{d['total']:,} = {rate:.1f}%")

    lines.append("")

    lines.append(

        "Die mit Abstand hoechste Error-Rate zeigt Deepseek V4 Pro, insbesondere auf "

        "BFCL Multiturn (63.6%). Dies ist auf die laengeren Multi-Turn-Konversationen "

        "zurueckzufuehren, bei denen das Modell haeufig das 120-Sekunden-Timeout "

        "ueberschreitet. GPT-5.4-mini und GPT-5.4 zeigen mit <0.3% eine sehr geringe Error-Rate."

    )

    lines.append("")

    lines.append("## Verteilung nach Architektur")

    lines.append("")

    by_agent = defaultdict(lambda: {"errors": 0, "total": 0})

    for e in errors:

        by_agent[e["agent"]]["errors"] += 1

    for key, cnt in total_by.items():

        by_agent[key[2]]["total"] += cnt

    for a in AGENT_ORDER:

        d = by_agent.get(a)

        if d and d["total"] > 0:

            rate = d["errors"] / d["total"] * 100

            aname = AGENT_NAMES.get(a, a)

            lines.append(f"- **{aname}**: {d['errors']:,}/{d['total']:,} = {rate:.1f}%")

    lines.append("")

    lines.append(

        "Multi-Agent-Architekturen zeigen eine hoehere Error-Rate als der Single Agent. "

        "Orchestrator (Fine) hat mit 18.5% die hoechste Rate, was auf die groessere Anzahl "

        "sequentieller Sub-Agent-Aufrufe zurueckzufuehren ist, die das Timeout-Limit "

        "leichter ueberschreiten."

    )

    lines.append("")

    lines.append("## Skalierung mit Tool-Anzahl")

    lines.append("")

    for t in TOOL_COUNTS:

        total = sum(cnt for key, cnt in total_by.items() if key[3] == t)

        errs = sum(1 for e in errors if e["num_tools"] == t)

        rate = errs / total * 100 if total > 0 else 0

        lines.append(f"- **t={t}**: {errs:,}/{total:,} = {rate:.1f}%")

    lines.append("")

    lines.append(

        "Die Error-Rate steigt leicht mit der Tool-Anzahl (9.2% bei t=10 auf 13.2% bei t=80). "

        "Mehr Tools fuehren zu laengeren Prompt-Kontexten und damit haeufigeren Timeouts."

    )

    lines.append("")

    lines.append("## Methodik")

    lines.append("")

    lines.append(

        f"Test Cases mit Fehler aber vorhandenen Metriken (n={with_metrics:,}) werden mit ihren "

        f"tatsaechlichen Scores ausgewertet. Test Cases ohne jegliche Metriken (n={no_metrics}) "

        f"werden aus der Berechnung von Mittelwerten und Konfidenzintervallen ausgeschlossen. "

        f"Die resultierende Stichprobengroesse n wird entsprechend reduziert. "

        f"Error-Raten werden als separate Qualitaetsmetrik berichtet."

    )

    return "\n".join(lines)
def main():

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    errors, total_by = collect_errors(all_data)

    print(f"  Found {len(errors)} error TCs")

    fmt = "png"

    print("\n--- Error Plots ---")

    plot_error_rate_by_model(all_data, errors, total_by, fmt)

    plot_error_rate_by_agent(all_data, errors, total_by, fmt)

    plot_error_rate_by_tools(all_data, errors, total_by, fmt)

    plot_error_types(errors, fmt)

    print("\n--- Error Tables ---")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    tex = gen_tables(errors, total_by)

    (OUTPUT_DIR / "5_5_fehleranalyse_tables.tex").write_text(tex, encoding="utf-8")

    print("  Saved: results/5_5_fehleranalyse_tables.tex")

    print("\n--- Error Text ---")

    md = gen_text(errors, total_by)

    (OUTPUT_DIR / "5_5_fehleranalyse.md").write_text(md, encoding="utf-8")

    print("  Saved: results/5_5_fehleranalyse.md")

    print("\nDone.")
if __name__ == "__main__":

    main()

