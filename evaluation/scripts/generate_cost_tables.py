"""
Generate LaTeX tables for cost and efficiency analysis.
One table per (model x benchmark) showing tokens, cost, and efficiency.
Usage:
    cd agenttim/evaluation
    python scripts/generate_cost_tables.py
"""
import json
from pathlib import Path
import numpy as np
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"
MODELS = ["gpt-5.4-mini", "june-gpt-5-4-datazone", "deepseek/deepseek-v4-pro"]
MODEL_DISPLAY = {

    "gpt-5.4-mini": "GPT-5.4-mini",

    "deepseek/deepseek-v4-pro": "Deepseek V4 Pro",

    "june-gpt-5-4-datazone": "GPT-5.4",
}
MODEL_FK = {

    "gpt-5.4-mini": "gpt-54-mini",

    "deepseek/deepseek-v4-pro": "deepseek",

    "june-gpt-5-4-datazone": "gpt-54",
}
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_DISPLAY = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
AGENTS = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_DISPLAY = {

    "single": "Single Agent",

    "orchestrator_fine": "Orch.\\ (Fine)",

    "orchestrator_coarse": "Orch.\\ (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
TOOLS = [10, 20, 40, 80]
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
def get_data(all_data, model, benchmark, agent, num_tools=None):

    prompt, comp, costs, n_passed, n_total = [], [], [], 0, 0

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

                comp.append(float(ct))

            if cost is not None:

                costs.append(float(cost))

            n_total += 1

            tc_m = tc.get("metrics", {}).get("Tool Correctness", {})

            if tc_m.get("success"):

                n_passed += 1

    return prompt, comp, costs, n_passed, n_total
def fmt_tokens(v):

    if v >= 1000:

        return f"{v/1000:,.1f}k"

    return f"{v:,.0f}"
def generate_aggregated_tables(all_data):

    """One table per model x benchmark, aggregated over all tool counts."""

    tables = []

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents_here = [

                a for a in AGENTS

                if get_data(all_data, model, benchmark, a)[0]

            ]

            if not agents_here:

                continue

            mn = MODEL_DISPLAY[model]

            bn = BENCH_DISPLAY[benchmark]

            label = f"tab:cost-{MODEL_FK[model]}-{benchmark}"

            lines = []

            lines.append(r"\begin{table}[htbp]")

            lines.append(r"  \centering")

            lines.append(

                f"  \\caption{ {mn} -- {bn}: Token-Verbrauch, Kosten und "

                f"Effizienz pro Architektur, aggregiert ueber alle Tool-Stufen.} "

            )

            lines.append(f"  \\label{ {label}} ")

            lines.append(r"  \begin{tabular}{l r r r r r r}")

            lines.append(r"    \toprule")

            lines.append(

                r"    Architecture & $n$ & Prompt/TC & Compl./TC & Total/TC "

                r"& Cost/TC & Succ./1k \\"

            )

            lines.append(r"    \midrule")

            for agent in agents_here:

                prompt, comp, costs, n_passed, n_total = get_data(

                    all_data, model, benchmark, agent,

                )

                name = AGENT_DISPLAY[agent]

                n = len(prompt)

                pm = np.mean(prompt) if prompt else 0

                cm = np.mean(comp) if comp else 0

                tm = pm + cm

                cost_mean = np.mean(costs) * 1000 if costs else 0

                total_tokens = sum(p + c for p, c in zip(prompt, comp))

                s1k = (n_passed / total_tokens) * 1000 if total_tokens > 0 else 0

                lines.append(

                    f"    {name} & {n} & {pm:,.0f} & {cm:,.0f} & {tm:,.0f} "

                    f"& \\${cost_mean:.2f}m & {s1k:.4f} \\\\"

                )

            lines.append(r"    \bottomrule")

            lines.append(r"  \end{tabular}")

            lines.append(

                r"  \par\footnotesize{Cost/TC in Milli-USD. "

                r"Succ./1k = bestandene TCs pro 1.000 verbrauchte Tokens "

                r"(hoeher = effizienter).}"

            )

            lines.append(r"\end{table}")

            tables.append((model, benchmark, "\n".join(lines)))

    return tables
def generate_scaling_token_tables(all_data):

    """One table per model x benchmark, showing tokens per TC at each tool count."""

    tables = []

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents_here = [

                a for a in AGENTS

                if get_data(all_data, model, benchmark, a, 10)[0]

            ]

            if not agents_here:

                continue

            mn = MODEL_DISPLAY[model]

            bn = BENCH_DISPLAY[benchmark]

            label = f"tab:tokens-scaling-{MODEL_FK[model]}-{benchmark}"

            lines = []

            lines.append(r"\begin{table}[htbp]")

            lines.append(r"  \centering")

            lines.append(

                f"  \\caption{ {mn} -- {bn}: Mittlerer Token-Verbrauch (Total) "

                f"pro Test Case und Tool-Stufe.} "

            )

            lines.append(f"  \\label{ {label}} ")

            lines.append(r"  \begin{tabular}{l r r r r r}")

            lines.append(r"    \toprule")

            lines.append(

                r"    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ "

                r"& Factor \\"

            )

            lines.append(r"    \midrule")

            for agent in agents_here:

                name = AGENT_DISPLAY[agent]

                vals = []

                for t in TOOLS:

                    prompt, comp, _, _, _ = get_data(

                        all_data, model, benchmark, agent, t,

                    )

                    if prompt:

                        total_per_tc = np.mean(

                            [p + c for p, c in zip(prompt, comp)]

                        )

                        vals.append(total_per_tc)

                    else:

                        vals.append(None)

                cells = []

                for v in vals:

                    cells.append(f"{fmt_tokens(v)}" if v is not None else "--")

                if vals[0] is not None and vals[-1] is not None and vals[0] > 0:

                    factor = f"{vals[-1] / vals[0]:.1f}x"

                else:

                    factor = "--"

                lines.append(

                    f"    {name} & {' & '.join(cells)} & {factor} \\\\"

                )

            lines.append(r"    \bottomrule")

            lines.append(r"  \end{tabular}")

            lines.append(

                r"  \par\footnotesize{Factor = Total Tokens($t{=}80$) / "

                r"Total Tokens($t{=}10$); zeigt den Wachstumsfaktor "

                r"des Token-Verbrauchs.}"

            )

            lines.append(r"\end{table}")

            tables.append((model, benchmark, "\n".join(lines)))

    return tables
def main():

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\nGenerating aggregated cost tables...")

    agg_tables = generate_aggregated_tables(all_data)

    print("Generating token scaling tables...")

    scale_tables = generate_scaling_token_tables(all_data)

    output_path = OUTPUT_DIR / "cost_tables.tex"

    with open(output_path, "w", encoding="utf-8") as f:

        f.write("% Auto-generated cost and efficiency tables\n")

        f.write("% Generated by scripts/generate_cost_tables.py\n\n")

        for model, benchmark, table in agg_tables:

            mn = MODEL_DISPLAY[model]

            bn = BENCH_DISPLAY[benchmark]

            f.write(f"% === {mn} x {bn} ===\n")

            f.write(table)

            f.write("\n\n")

    print(f"  Saved: {output_path} ({len(agg_tables)} tables)")

    output_path2 = OUTPUT_DIR / "token_scaling_tables.tex"

    with open(output_path2, "w", encoding="utf-8") as f:

        f.write("% Auto-generated token scaling tables\n")

        f.write("% Generated by scripts/generate_cost_tables.py\n\n")

        for model, benchmark, table in scale_tables:

            mn = MODEL_DISPLAY[model]

            bn = BENCH_DISPLAY[benchmark]

            f.write(f"% === {mn} x {bn} ===\n")

            f.write(table)

            f.write("\n\n")

    print(f"  Saved: {output_path2} ({len(scale_tables)} tables)")

    for _, _, table in agg_tables + scale_tables:

        print()

        print(table)
if __name__ == "__main__":

    main()

