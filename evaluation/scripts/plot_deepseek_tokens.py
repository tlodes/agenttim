"""
Plot Deepseek Token Comparison: Single vs Orchestrator.
Usage:
    cd agenttim/evaluation
    python scripts/plot_deepseek_tokens.py
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results" / "deepseek" / "deepseek-v4-pro" / "mcpagentbench"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "plots"
def load_data(tool_count: str = "t10") -> dict:

    """Load results for a specific tool count."""

    results_dir = RESULTS_DIR / tool_count

    data = {}

    for f in results_dir.glob("*.json"):

        if "_errors" in f.name:

            continue

        j = json.loads(f.read_text(encoding="utf-8"))

        agent = j.get("agent_type", "?")

        mode = j.get("mode", "?")

        agg = j.get("aggregate", {})

        key = f"{agent}|{mode}"

        data[key] = {

            "agent": agent,

            "mode": mode,

            "total_tokens": agg.get("total_tokens", 0),

            "pass_rate": agg.get("pass_rate", 0),

            "avg_latency": agg.get("avg_latency", 0),

        }

    return data
def plot_token_comparison(tool_count: str = "t10"):

    """Create grouped bar chart comparing token usage."""

    data = load_data(tool_count)

    modes = [

        "sturn-1t-daytasks",

        "sturn-1t-protasks",

        "sturn-mt-daytasks-parallel",

        "sturn-mt-daytasks-sequential",

        "sturn-mt-daytasks-3tools",

        "sturn-mt-protasks-parallel",

        "sturn-mt-protasks-sequential",

        "sturn-mt-protasks-3tools",

    ]

    labels = [

        "1T-Day", "1T-Pro",

        "MT-Day-Par", "MT-Day-Seq", "MT-Day-3T",

        "MT-Pro-Par", "MT-Pro-Seq", "MT-Pro-3T",

    ]

    single_tokens = []

    orch_fine_tokens = []

    orch_coarse_tokens = []

    for mode in modes:

        single_tokens.append(data.get(f"single|{mode}", {}).get("total_tokens", 0) / 1000)

        orch_fine_tokens.append(data.get(f"orchestrator_fine|{mode}", {}).get("total_tokens", 0) / 1000)

        orch_coarse_tokens.append(data.get(f"orchestrator_coarse|{mode}", {}).get("total_tokens", 0) / 1000)

    fig, ax = plt.subplots(figsize=(14, 6))

    x = np.arange(len(labels))

    width = 0.25

    bars1 = ax.bar(x - width, single_tokens, width, label="Single Agent",

                   color="#2ecc71", edgecolor="black", linewidth=0.5)

    bars2 = ax.bar(x, orch_fine_tokens, width, label="Orchestrator (Fine)",

                   color="#3498db", edgecolor="black", linewidth=0.5)

    bars3 = ax.bar(x + width, orch_coarse_tokens, width, label="Orchestrator (Coarse)",

                   color="#9b59b6", edgecolor="black", linewidth=0.5)

    ax.set_xlabel("Task Mode")

    ax.set_ylabel("Total Tokens (thousands)")

    ax.set_title(f"Deepseek V4 Pro: Token Usage Comparison ({tool_count})\nSingle Agent vs Orchestrator")

    ax.set_xticks(x)

    ax.set_xticklabels(labels, rotation=30, ha="right")

    ax.legend(loc="upper left")

    ax.grid(axis="y", alpha=0.3)

    for i, (s, of, oc) in enumerate(zip(single_tokens, orch_fine_tokens, orch_coarse_tokens)):

        if s > 0 and of > 0:

            overhead = ((of - s) / s * 100)

            color = "red" if overhead > 0 else "green"

            ax.annotate(f"{overhead:+.0f}%", xy=(x[i], of), xytext=(0, 5),

                       textcoords="offset points", ha="center", fontsize=8, color=color,

                       fontweight="bold")

    plt.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"deepseek_token_comparison_{tool_count}.png"

    plt.savefig(output_path, dpi=150)

    print(f"Plot saved to: {output_path}")

    plt.close()

    return output_path
def print_summary(tool_count: str = "t10"):

    """Print summary table."""

    data = load_data(tool_count)

    modes = sorted(set(d["mode"] for d in data.values()))

    print(f"\n{'='*100}")

    print(f"Deepseek V4 Pro Token Usage Summary ({tool_count})")

    print(f"{'='*100}")

    print(f"{'Mode':<35} | {'Single':>12} | {'Orch Fine':>12} | {'Orch Coarse':>12} | {'Overhead':>10}")

    print("-" * 100)

    for mode in modes:

        single = data.get(f"single|{mode}", {})

        orch_fine = data.get(f"orchestrator_fine|{mode}", {})

        orch_coarse = data.get(f"orchestrator_coarse|{mode}", {})

        s_tok = single.get("total_tokens", 0)

        of_tok = orch_fine.get("total_tokens", 0)

        oc_tok = orch_coarse.get("total_tokens", 0)

        overhead = ((of_tok - s_tok) / s_tok * 100) if s_tok > 0 and of_tok > 0 else 0

        print(f"{mode:<35} | {s_tok:>12,} | {of_tok:>12,} | {oc_tok:>12,} | {overhead:>+9.1f}%")
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Plot Deepseek token comparison")

    parser.add_argument("--tools", "-t", default="t10", help="Tool count folder (t10, t20, t40)")

    args = parser.parse_args()

    print_summary(args.tools)

    plot_token_comparison(args.tools)

