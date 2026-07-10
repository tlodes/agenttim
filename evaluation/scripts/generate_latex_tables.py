"""
Generate LaTeX tables for core comparison results.
Produces one table per (model x benchmark) with TC, AC, 95% CI, n,
and significance stars vs Single Agent.
Usage:
    cd agenttim/evaluation
    python scripts/generate_latex_tables.py
"""
import json
import sys
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results_enriched"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "results"
MODELS = ["gpt-5.4-mini", "june-gpt-5-4-datazone", "deepseek/deepseek-v4-pro"]
MODEL_DISPLAY = {

    "gpt-5.4-mini": "GPT-5.4-mini",

    "deepseek/deepseek-v4-pro": "Deepseek V4 Pro",

    "june-gpt-5-4-datazone": "GPT-5.4",
}
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_DISPLAY = {

    "mcpagentbench": "MCPAgentBench",

    "bfcl_multiturn": "BFCL Multiturn",
}
AGENTS = [

    "single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm",
]
AGENT_DISPLAY = {

    "single": "Single Agent",

    "orchestrator_fine": "Orch.\\ (Fine)",

    "orchestrator_coarse": "Orch.\\ (Coarse)",

    "router": "Router",

    "swarm": "Swarm",
}
METRICS = ["Tool Correctness", "Argument Correctness [Reference]"]
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
def aggregate_scores(all_data, model, benchmark, agent, metric):

    scores = []

    for r in all_data:

        if (r.get("model") != model

                or r.get("benchmark") != benchmark

                or r.get("agent_type") != agent):

            continue

        for tc in r.get("test_cases", []):

            m = tc.get("metrics", {}).get(metric, {})

            s = m.get("score")

            if s is not None:

                scores.append(float(s))

    if not scores:

        return None, None, None, 0

    arr = np.array(scores)

    n = len(arr)

    mean = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0

    return mean, max(0.0, mean - 1.96 * se), min(1.0, mean + 1.96 * se), n
def compute_significance(all_data, model, benchmark, metric, arch_a, arch_b):

    runs_a, runs_b = {}, {}

    for r in all_data:

        if r.get("model") != model or r.get("benchmark") != benchmark:

            continue

        key = (r.get("mode", ""), r.get("num_tools"))

        if r.get("agent_type") == arch_a:

            runs_a[key] = r

        elif r.get("agent_type") == arch_b:

            runs_b[key] = r

    sa, sb = [], []

    for key in runs_a:

        if key not in runs_b:

            continue

        rb_by_id = {}

        for tc in runs_b[key].get("test_cases", []):

            tid = tc.get("id", "")

            m = tc.get("metrics", {}).get(metric, {})

            s = m.get("score")

            if s is not None and tid:

                rb_by_id[tid] = float(s)

        for tc in runs_a[key].get("test_cases", []):

            tid = tc.get("id", "")

            m = tc.get("metrics", {}).get(metric, {})

            s = m.get("score")

            if s is not None and tid in rb_by_id:

                sa.append(float(s))

                sb.append(rb_by_id[tid])

    if len(sa) < 5:

        return 1.0

    diffs = np.array(sa) - np.array(sb)

    nz = diffs[diffs != 0]

    if len(nz) == 0:

        return 1.0

    _, p = wilcoxon(nz)

    return p
def sig_stars(p):

    if p < 0.001:

        return "***"

    if p < 0.01:

        return "**"

    if p < 0.05:

        return "*"

    return ""
def generate_tables(all_data):

    tables = []

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents_with_data = [

                a for a in AGENTS

                if aggregate_scores(all_data, model, benchmark, a, METRICS[0])[0] is not None

            ]

            if not agents_with_data:

                continue

            model_name = MODEL_DISPLAY[model]

            bench_name = BENCH_DISPLAY[benchmark]

            safe_model = model.replace("/", "-").replace(".", "")

            label = f"tab:{safe_model}-{benchmark}"

            lines = []

            lines.append(r"\begin{table}[htbp]")

            lines.append(r"  \centering")

            lines.append(

                f"  \\caption{ {model_name} -- {bench_name}: "

                f"Tool Correctness (TC) und Argument Correctness (AC), "

                f"aggregiert über alle Tool-Stufen.} "

            )

            lines.append(f"  \\label{ {label}} ")

            lines.append(r"  \begin{tabular}{l r r r r r}")

            lines.append(r"    \toprule")

            lines.append(

                r"    Architecture & $n$ & TC $\bar{x}$ & TC 95\% CI "

                r"& AC $\bar{x}$ & AC 95\% CI \\"

            )

            lines.append(r"    \midrule")

            for agent in agents_with_data:

                tc_mean, tc_lo, tc_hi, tc_n = aggregate_scores(

                    all_data, model, benchmark, agent, METRICS[0],

                )

                ac_mean, ac_lo, ac_hi, ac_n = aggregate_scores(

                    all_data, model, benchmark, agent, METRICS[1],

                )

                tc_sig = ""

                ac_sig = ""

                if agent != "single":

                    tc_p = compute_significance(

                        all_data, model, benchmark, METRICS[0], "single", agent,

                    )

                    ac_p = compute_significance(

                        all_data, model, benchmark, METRICS[1], "single", agent,

                    )

                    tc_sig = sig_stars(tc_p)

                    ac_sig = sig_stars(ac_p)

                name = AGENT_DISPLAY[agent]

                n_str = str(tc_n or ac_n)

                if tc_mean is not None:

                    tc_val = f"${tc_mean:.3f}^{ {tc_sig}} $" if tc_sig else f"${tc_mean:.3f}$"

                    tc_ci = f"$[{tc_lo:.3f},\\, {tc_hi:.3f}]$"

                else:

                    tc_val = "--"

                    tc_ci = "--"

                if ac_mean is not None:

                    ac_val = f"${ac_mean:.3f}^{ {ac_sig}} $" if ac_sig else f"${ac_mean:.3f}$"

                    ac_ci = f"$[{ac_lo:.3f},\\, {ac_hi:.3f}]$"

                else:

                    ac_val = "--"

                    ac_ci = "--"

                lines.append(

                    f"    {name} & {n_str} & {tc_val} & {tc_ci} "

                    f"& {ac_val} & {ac_ci} \\\\"

                )

            lines.append(r"    \bottomrule")

            lines.append(r"  \end{tabular}")

            lines.append(r"  \vspace{2pt}")

            lines.append(

                r"  \par\footnotesize{Signifikanz vs.\ Single Agent "

                r"(Wilcoxon Signed-Rank): "

                r"$^{*}$\,$p<0.05$, $^{**}$\,$p<0.01$, $^{***}$\,$p<0.001$}"

            )

            lines.append(r"\end{table}")

            table_str = "\n".join(lines)

            tables.append((model, benchmark, table_str))

    return tables
def main():

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    print("\nGenerating LaTeX tables...")

    tables = generate_tables(all_data)

    output_path = OUTPUT_DIR / "core_comparison_tables.tex"

    with open(output_path, "w", encoding="utf-8") as f:

        f.write("% Auto-generated core comparison tables\n")

        f.write("% Generated by scripts/generate_latex_tables.py\n\n")

        for model, benchmark, table in tables:

            model_name = MODEL_DISPLAY[model]

            bench_name = BENCH_DISPLAY[benchmark]

            f.write(f"% === {model_name} x {bench_name} ===\n")

            f.write(table)

            f.write("\n\n")

    print(f"  Saved: {output_path}")

    print(f"  {len(tables)} tables generated")

    for _, _, table in tables:

        print()

        print(table)

        print()
if __name__ == "__main__":

    main()

