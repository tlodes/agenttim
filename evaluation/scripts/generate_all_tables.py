"""
Generate ALL LaTeX tables for thesis chapters 5.1-5.4.
Best values per column are marked with \\textbf{}.
Output files in results/:
  5_1_core_comparison_tables.tex, 5_1_scaling_tables.tex,
  5_2_kosten_tokens_tables.tex, 5_2_token_scaling_tables.tex,
  5_3_latenz_tables.tex, 5_3_latenz_scaling_tables.tex,
  5_4_benchmark_tables.tex
Usage:
    cd agenttim/evaluation
    python scripts/generate_all_tables.py
"""
import json
from pathlib import Path
import numpy as np
from scipy import stats
BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_enriched"
OUTPUT_DIR = BASE / "results"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES_TEX = {

    "single": "Single Agent", "orchestrator_fine": "Orch.\\ (Fine)",

    "orchestrator_coarse": "Orch.\\ (Coarse)", "router": "Router", "swarm": "Swarm",
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
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
TOOL_COUNTS = [10, 20, 40, 80]
SIG_FOOTNOTE = (

    "\\par\\footnotesize{Signifikanz vs.\\ Single Agent "

    "(Wilcoxon Signed-Rank): $^{*}$\\,$p<0.05$, "

    "$^{**}$\\,$p<0.01$, $^{***}$\\,$p<0.001$. "

    "\\textbf{Fett} = bester Wert.}"
)
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
def available_agents(all_data, model, benchmark):

    found = set()

    for r in all_data:

        if r.get("model") == model and r.get("benchmark") == benchmark:

            found.add(r.get("agent_type"))

    return [a for a in AGENT_ORDER if a in found]
def get_metric_scores(all_data, model, benchmark, agent, metric_key, num_tools=None):

    scores = []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric_key, {}).get("score")

            if s is not None:

                scores.append(float(s))

    return scores
def get_token_data(all_data, model, benchmark, agent, num_tools=None):

    prompt, completion, costs = [], [], []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

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
def get_latency_values(all_data, model, benchmark, agent, num_tools=None):

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

            else:

                lats = [float(t["latency"]) for t in tools if t.get("latency") is not None]

                if lats:

                    vals.append(sum(lats))

    return vals
def get_redundancy_counts(all_data, model, agent, num_tools=None):

    counts = []

    for r in _filter(all_data, model, "bfcl_multiturn", agent, num_tools):

        for tc in r.get("test_cases", []):

            cnt = tc.get("metrics", {}).get("Tool Correctness", {}).get("cross_turn_redundant_count")

            if cnt is not None:

                counts.append(float(cnt))

    return counts
def get_efficiency(all_data, model, benchmark, agent, num_tools=None):

    total_tokens = 0

    passed = 0

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            tt = tc.get("tokens", {}).get("total_tokens", 0)

            total_tokens += tt

            if tc.get("metrics", {}).get("Tool Correctness", {}).get("success"):

                passed += 1

    if total_tokens == 0:

        return None

    return (passed / total_tokens) * 1000
def get_oh_scores(all_data, model, benchmark, agent):

    scores = []

    for r in _filter(all_data, model, benchmark, agent):

        for tc in r.get("test_cases", []):

            oh = tc.get("metrics", {}).get("Coordination Token Overhead", {})

            s = oh.get("score")

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

            "ci_hi": mean + 1.96 * se, "n": n}
def sig_stars(scores_a, scores_b):

    n = min(len(scores_a), len(scores_b))

    if n < 10:

        return ""

    a, b = np.array(scores_a[:n]), np.array(scores_b[:n])

    diff = a - b

    if np.all(diff == 0):

        return ""

    try:

        _, p = stats.wilcoxon(diff)

    except ValueError:

        return ""

    if p < 0.001:

        return "^{***}"

    elif p < 0.01:

        return "^{**}"

    elif p < 0.05:

        return "^{*}"

    return ""
def _bf(val_str, is_best):

    """Wrap in textbf if best."""

    return f"\\textbf{ {val_str}} " if is_best else val_str
def _best_idx(values, higher_is_better=True):

    """Find index of best value. Returns set of indices (handles ties)."""

    valid = [(i, v) for i, v in enumerate(values) if v is not None]

    if not valid:

        return set()

    if higher_is_better:

        best = max(v for _, v in valid)

    else:

        best = min(v for _, v in valid)

    return {i for i, v in valid if abs(v - best) < 1e-9}
def gen_5_1_overall(all_data):

    lines = ["% Auto-generated: 5.1 Core Comparison (Overall)", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            if benchmark == "mcpagentbench":

                metrics = [("Tool Correctness", "TC"),

                           ("Argument Correctness [Reference]", "AC"),

                           ("Final State (Derived)", "FS")]

            else:

                metrics = [("Tool Correctness", "TC"),

                           ("Argument Correctness [Reference]", "AC"),

                           ("State Match", "SM")]

            agent_data = {}

            single_scores = {}

            for mk, _ in metrics:

                single_scores[mk] = get_metric_scores(all_data, model, benchmark, "single", mk)

            for a in agents:

                row = {}

                for mk, _ in metrics:

                    scores = get_metric_scores(all_data, model, benchmark, a, mk)

                    st = agg(scores)

                    row[mk] = {"agg": st, "scores": scores}

                agent_data[a] = row

            best_per_metric = {}

            for mk, _ in metrics:

                means = [agent_data[a][mk]["agg"]["mean"] if agent_data[a][mk]["agg"] else None for a in agents]

                best_per_metric[mk] = _best_idx(means, higher_is_better=True)

            metric_headers = " & ".join([f"{abbr} $\\bar{ x} $ & {abbr} 95\\% CI" for _, abbr in metrics])

            col_spec = "l r " + " ".join(["r r"] * len(metrics))

            lines.append(f"% === {mdisp} x {bname} ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Aggregierte Metriken ueber alle Tool-Stufen.} ")

            lines.append(f"  \\label{ tab:core-{MODEL_FK[model]}-{benchmark}} ")

            lines.append(f"  \\begin{ tabular} { {col_spec}} ")

            lines.append("    \\toprule")

            lines.append(f"    Architecture & $n$ & {metric_headers} \\\\")

            lines.append("    \\midrule")

            for i, a in enumerate(agents):

                name = AGENT_NAMES_TEX[a]

                first_mk = metrics[0][0]

                n = len(agent_data[a][first_mk]["scores"])

                parts = [name, str(n)]

                for mk, _ in metrics:

                    st = agent_data[a][mk]["agg"]

                    if st is None:

                        parts.extend(["--", "--"])

                        continue

                    stars = ""

                    if a != "single":

                        stars = sig_stars(single_scores[mk], agent_data[a][mk]["scores"])

                    is_best = i in best_per_metric[mk]

                    val = f"{st['mean']:.3f}"

                    val_display = _bf(val, is_best)

                    parts.append(f"${val_display}{stars}$")

                    parts.append(f"$[{st['ci_lo']:.3f},\\, {st['ci_hi']:.3f}]$")

                lines.append(f"    {' & '.join(parts)} \\\\")

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\vspace{2pt}")

            lines.append(f"  {SIG_FOOTNOTE}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def gen_5_1_scaling(all_data):

    lines = ["% Auto-generated: 5.1 Core Comparison (Scaling)", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            if benchmark == "mcpagentbench":

                metrics = [("Tool Correctness", "TC"),

                           ("Argument Correctness [Reference]", "AC"),

                           ("Final State (Derived)", "FS")]

            else:

                metrics = [("Tool Correctness", "TC"),

                           ("Argument Correctness [Reference]", "AC"),

                           ("State Match", "SM")]

            for mk, abbr in metrics:

                agent_vals = {}

                for a in agents:

                    vals = []

                    for t in TOOL_COUNTS:

                        scores = get_metric_scores(all_data, model, benchmark, a, mk, t)

                        st = agg(scores)

                        vals.append(st["mean"] if st else None)

                    agent_vals[a] = vals

                best_per_col = {}

                for j in range(len(TOOL_COUNTS)):

                    col_vals = [agent_vals[a][j] for a in agents]

                    best_per_col[j] = _best_idx(col_vals, higher_is_better=True)

                lines.append(f"% === {mdisp} x {bname}: {abbr} Scaling ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- {bname}: {abbr} pro Tool-Stufe.} ")

                lines.append(f"  \\label{ tab:scaling-{abbr.lower()}-{MODEL_FK[model]}-{benchmark}} ")

                lines.append("  \\begin{tabular}{l r r r r r}")

                lines.append("    \\toprule")

                lines.append("    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ & $\\Delta$ \\\\")

                lines.append("    \\midrule")

                for i, a in enumerate(agents):

                    name = AGENT_NAMES_TEX[a]

                    parts = [name]

                    for j, v in enumerate(agent_vals[a]):

                        if v is not None:

                            is_best = i in best_per_col[j]

                            val = f"{v:.3f}"

                            parts.append(f"${_bf(val, is_best)}$")

                        else:

                            parts.append("--")

                    v0 = agent_vals[a][0]

                    vn = agent_vals[a][-1]

                    if v0 is not None and vn is not None:

                        delta = v0 - vn

                        sign = "+" if delta >= 0 else ""

                        parts.append(f"${sign}{delta:.3f}$")

                    else:

                        parts.append("--")

                    lines.append(f"    {' & '.join(parts)} \\\\")

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append(f"  \\par\\footnotesize{ $\\Delta = $ {abbr}($t{ =} 10$) $-$ {abbr}($t{ =} 80$); positive Werte zeigen Degradation. \\textbf{ Fett}  = bester Wert.} ")

                lines.append("\\end{table}")

                lines.append("")

    return "\n".join(lines)
def gen_5_2_overall(all_data):

    lines = ["% Auto-generated: 5.2 Kosten & Tokens (Overall)", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            rows = []

            for a in agents:

                prompt, completion, costs = get_token_data(all_data, model, benchmark, a)

                n = len(prompt)

                if n == 0:

                    continue

                pm = int(np.mean(prompt))

                cm = int(np.mean(completion))

                tm = pm + cm

                eff = get_efficiency(all_data, model, benchmark, a)

                oh = get_oh_scores(all_data, model, benchmark, a)

                oh_mean = float(np.mean(oh)) if oh else None

                rows.append({"agent": a, "n": n, "prompt": pm, "compl": cm,

                             "total": tm, "eff": eff, "oh": oh_mean})

            if not rows:

                continue

            best_total = _best_idx([r["total"] for r in rows], higher_is_better=False)

            best_eff = _best_idx([r["eff"] for r in rows], higher_is_better=True)

            best_oh = _best_idx([r["oh"] for r in rows], higher_is_better=True)

            lines.append(f"% === {mdisp} x {bname} ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Token-Verbrauch und Effizienz, aggregiert.} ")

            lines.append(f"  \\label{ tab:tokens-{MODEL_FK[model]}-{benchmark}} ")

            lines.append("  \\begin{tabular}{l r r r r r r}")

            lines.append("    \\toprule")

            lines.append("    Architecture & $n$ & Prompt/TC & Compl./TC & Total/TC & Succ./1k & OH Score \\\\")

            lines.append("    \\midrule")

            for i, r in enumerate(rows):

                name = AGENT_NAMES_TEX[r["agent"]]

                total_str = _bf(f"{r['total']:,}", i in best_total)

                eff_str = _bf(f"{r['eff']:.4f}", i in best_eff) if r['eff'] is not None else "--"

                oh_str = _bf(f"{r['oh']:.3f}", i in best_oh) if r['oh'] is not None else "--"

                lines.append(

                    f"    {name} & {r['n']:,} & {r['prompt']:,} & {r['compl']:,} "

                    f"& {total_str} & {eff_str} & {oh_str} \\\\"

                )

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\par\\footnotesize{Succ./1k = bestandene TCs pro 1.000 Tokens. OH Score = Coordination Token Overhead (1.0 = kein Overhead). \\textbf{Fett} = bester Wert.}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def gen_5_2_scaling(all_data):

    lines = ["% Auto-generated: 5.2 Token Scaling", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            agent_toks = {}

            for a in agents:

                vals = []

                for t in TOOL_COUNTS:

                    prompt, completion, _ = get_token_data(all_data, model, benchmark, a, t)

                    if prompt:

                        total = [p + c for p, c in zip(prompt, completion)]

                        vals.append(int(np.mean(total)))

                    else:

                        vals.append(None)

                agent_toks[a] = vals

            best_per_col = {}

            for j in range(len(TOOL_COUNTS)):

                col_vals = [agent_toks[a][j] for a in agents]

                best_per_col[j] = _best_idx(col_vals, higher_is_better=False)

            lines.append(f"% === {mdisp} x {bname}: Total Tokens Scaling ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Total Tokens/TC pro Tool-Stufe.} ")

            lines.append(f"  \\label{ tab:token-scaling-{MODEL_FK[model]}-{benchmark}} ")

            lines.append("  \\begin{tabular}{l r r r r r}")

            lines.append("    \\toprule")

            lines.append("    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ & Factor \\\\")

            lines.append("    \\midrule")

            for i, a in enumerate(agents):

                name = AGENT_NAMES_TEX[a]

                parts = [name]

                for j, v in enumerate(agent_toks[a]):

                    if v is not None:

                        is_best = i in best_per_col[j]

                        parts.append(_bf(f"{v:,}", is_best))

                    else:

                        parts.append("--")

                v0, vn = agent_toks[a][0], agent_toks[a][-1]

                if v0 and vn:

                    parts.append(f"{vn / v0:.1f}x")

                else:

                    parts.append("--")

                lines.append(f"    {' & '.join(parts)} \\\\")

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\par\\footnotesize{Factor = Total($t{=}80$) / Total($t{=}10$). \\textbf{Fett} = geringster Verbrauch.}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def gen_5_3_overall(all_data):

    lines = ["% Auto-generated: 5.3 Latenz (Overall)", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            single_lats = get_latency_values(all_data, model, benchmark, "single")

            rows = []

            for a in agents:

                vals = get_latency_values(all_data, model, benchmark, a)

                if not vals:

                    continue

                arr = np.array(vals)

                rows.append({

                    "agent": a, "vals": vals,

                    "n": len(arr), "mean": float(np.mean(arr)),

                    "median": float(np.median(arr)),

                    "ci_lo": max(0, float(np.mean(arr)) - 1.96 * float(np.std(arr, ddof=1) / np.sqrt(len(arr)))),

                    "ci_hi": float(np.mean(arr)) + 1.96 * float(np.std(arr, ddof=1) / np.sqrt(len(arr))),

                    "p95": float(np.percentile(arr, 95)),

                })

            if not rows:

                continue

            best_mean = _best_idx([r["mean"] for r in rows], higher_is_better=False)

            lines.append(f"% === {mdisp} x {bname} ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Durchschnittliche Latenz pro Test Case (Sekunden), aggregiert.} ")

            lines.append(f"  \\label{ tab:latency-{MODEL_FK[model]}-{benchmark}} ")

            lines.append("  \\begin{tabular}{l r r r r r}")

            lines.append("    \\toprule")

            lines.append("    Architecture & $n$ & $\\bar{x}$ (s) & Median (s) & 95\\% CI & p95 (s) \\\\")

            lines.append("    \\midrule")

            for i, r in enumerate(rows):

                name = AGENT_NAMES_TEX[r["agent"]]

                stars = ""

                if r["agent"] != "single" and single_lats:

                    stars = sig_stars(single_lats, r["vals"])

                mean_str = _bf(f"{r['mean']:.1f}", i in best_mean)

                lines.append(

                    f"    {name} & {r['n']} & ${mean_str}{stars}$ & {r['median']:.1f} "

                    f"& $[{r['ci_lo']:.1f},\\, {r['ci_hi']:.1f}]$ & {r['p95']:.1f} \\\\"

                )

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\vspace{2pt}")

            lines.append(f"  {SIG_FOOTNOTE}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def gen_5_3_scaling(all_data):

    lines = ["% Auto-generated: 5.3 Latenz (Scaling)", ""]

    for model in MODELS:

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if not agents:

                continue

            mdisp = MODEL_DISPLAY[model]

            bname = BENCH_NAMES[benchmark]

            agent_lats = {}

            for a in agents:

                vals = []

                for t in TOOL_COUNTS:

                    lv = get_latency_values(all_data, model, benchmark, a, t)

                    vals.append(float(np.mean(lv)) if lv else None)

                agent_lats[a] = vals

            best_per_col = {}

            for j in range(len(TOOL_COUNTS)):

                col_vals = [agent_lats[a][j] for a in agents]

                best_per_col[j] = _best_idx(col_vals, higher_is_better=False)

            lines.append(f"% === {mdisp} x {bname} ===")

            lines.append("\\begin{table}[htbp]")

            lines.append("  \\centering")

            lines.append(f"  \\caption{ {mdisp} -- {bname}: Avg. Latenz/TC (s) pro Tool-Stufe.} ")

            lines.append(f"  \\label{ tab:latency-scaling-{MODEL_FK[model]}-{benchmark}} ")

            lines.append("  \\begin{tabular}{l r r r r r}")

            lines.append("    \\toprule")

            lines.append("    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ & Factor \\\\")

            lines.append("    \\midrule")

            for i, a in enumerate(agents):

                name = AGENT_NAMES_TEX[a]

                parts = [name]

                for j, v in enumerate(agent_lats[a]):

                    if v is not None:

                        is_best = i in best_per_col[j]

                        parts.append(_bf(f"{v:.1f}", is_best))

                    else:

                        parts.append("--")

                v0, vn = agent_lats[a][0], agent_lats[a][-1]

                if v0 and vn:

                    parts.append(f"{vn / v0:.1f}x")

                else:

                    parts.append("--")

                lines.append(f"    {' & '.join(parts)} \\\\")

            lines.append("    \\bottomrule")

            lines.append("  \\end{tabular}")

            lines.append("  \\par\\footnotesize{Factor = Latenz($t{=}80$) / Latenz($t{=}10$). \\textbf{Fett} = geringste Latenz.}")

            lines.append("\\end{table}")

            lines.append("")

    return "\n".join(lines)
def gen_5_4(all_data):

    lines = ["% Auto-generated: 5.4 Benchmark-spezifische Metriken", ""]

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        mfk = MODEL_FK[model]

        agents_mcp = available_agents(all_data, model, "mcpagentbench")

        if agents_mcp:

            single_ee = get_metric_scores(all_data, model, "mcpagentbench", "single", "Execution Efficiency")

            rows = []

            for a in agents_mcp:

                scores = get_metric_scores(all_data, model, "mcpagentbench", a, "Execution Efficiency")

                st = agg(scores)

                if st:

                    rows.append({"agent": a, "agg": st, "scores": scores})

            if rows:

                best = _best_idx([r["agg"]["mean"] for r in rows], higher_is_better=True)

                lines.append(f"% === {mdisp}: Execution Efficiency ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- MCPAgentBench: Execution Efficiency (Parallel-Modi), aggregiert.} ")

                lines.append(f"  \\label{ tab:exec-eff-{mfk}} ")

                lines.append("  \\begin{tabular}{l r r r}")

                lines.append("    \\toprule")

                lines.append("    Architecture & $n$ & $\\bar{x}$ & 95\\% CI \\\\")

                lines.append("    \\midrule")

                for i, r in enumerate(rows):

                    name = AGENT_NAMES_TEX[r["agent"]]

                    stars = ""

                    if r["agent"] != "single" and single_ee:

                        stars = sig_stars(single_ee, r["scores"])

                    val = _bf(f"{r['agg']['mean']:.3f}", i in best)

                    lines.append(

                        f"    {name} & {r['agg']['n']} & ${val}{stars}$ "

                        f"& $[{r['agg']['ci_lo']:.3f},\\, {r['agg']['ci_hi']:.3f}]$ \\\\"

                    )

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\vspace{2pt}")

                lines.append(f"  {SIG_FOOTNOTE}")

                lines.append("\\end{table}")

                lines.append("")

            agent_ee = {}

            for a in agents_mcp:

                vals = []

                for t in TOOL_COUNTS:

                    scores = get_metric_scores(all_data, model, "mcpagentbench", a, "Execution Efficiency", t)

                    st = agg(scores)

                    vals.append(st["mean"] if st else None)

                if any(v is not None for v in vals):

                    agent_ee[a] = vals

            if agent_ee:

                ee_agents = [a for a in agents_mcp if a in agent_ee]

                best_per_col = {}

                for j in range(len(TOOL_COUNTS)):

                    col_vals = [agent_ee[a][j] if a in agent_ee else None for a in ee_agents]

                    best_per_col[j] = _best_idx(col_vals, higher_is_better=True)

                lines.append(f"% === {mdisp}: Execution Efficiency Scaling ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- MCPAgentBench: Execution Efficiency pro Tool-Stufe.} ")

                lines.append(f"  \\label{ tab:exec-eff-scaling-{mfk}} ")

                lines.append("  \\begin{tabular}{l r r r r r}")

                lines.append("    \\toprule")

                lines.append("    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ & $\\Delta$ \\\\")

                lines.append("    \\midrule")

                for i, a in enumerate(ee_agents):

                    name = AGENT_NAMES_TEX[a]

                    parts = [name]

                    for j, v in enumerate(agent_ee[a]):

                        if v is not None:

                            is_best = i in best_per_col[j]

                            parts.append(f"${_bf(f'{v:.3f}', is_best)}$")

                        else:

                            parts.append("--")

                    v0, vn = agent_ee[a][0], agent_ee[a][-1]

                    if v0 is not None and vn is not None:

                        delta = v0 - vn

                        sign = "+" if delta >= 0 else ""

                        parts.append(f"${sign}{delta:.3f}$")

                    else:

                        parts.append("--")

                    lines.append(f"    {' & '.join(parts)} \\\\")

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\par\\footnotesize{$\\Delta = $ EE($t{=}10$) $-$ EE($t{=}80$). \\textbf{Fett} = bester Wert.}")

                lines.append("\\end{table}")

                lines.append("")

        agents_bfcl = available_agents(all_data, model, "bfcl_multiturn")

        if agents_bfcl:

            rows = []

            for a in agents_bfcl:

                counts = get_redundancy_counts(all_data, model, a)

                st = agg(counts)

                if st:

                    rows.append({"agent": a, "agg": st})

            if rows:

                best = _best_idx([r["agg"]["mean"] for r in rows], higher_is_better=False)

                lines.append(f"% === {mdisp}: Cross-Turn Redundancy ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- BFCL Multiturn: Cross-Turn Redundancy (Avg. redundante Calls/TC), aggregiert.} ")

                lines.append(f"  \\label{ tab:redundancy-{mfk}} ")

                lines.append("  \\begin{tabular}{l r r r}")

                lines.append("    \\toprule")

                lines.append("    Architecture & $n$ & $\\bar{x}$ & 95\\% CI \\\\")

                lines.append("    \\midrule")

                for i, r in enumerate(rows):

                    name = AGENT_NAMES_TEX[r["agent"]]

                    val = _bf(f"{r['agg']['mean']:.2f}", i in best)

                    lines.append(

                        f"    {name} & {r['agg']['n']} & ${val}$ "

                        f"& $[{r['agg']['ci_lo']:.2f},\\, {r['agg']['ci_hi']:.2f}]$ \\\\"

                    )

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\par\\footnotesize{\\textbf{Fett} = geringste Redundanz.}")

                lines.append("\\end{table}")

                lines.append("")

            agent_red = {}

            for a in agents_bfcl:

                vals = []

                for t in TOOL_COUNTS:

                    counts = get_redundancy_counts(all_data, model, a, t)

                    vals.append(float(np.mean(counts)) if counts else None)

                if any(v is not None for v in vals):

                    agent_red[a] = vals

            if agent_red:

                red_agents = [a for a in agents_bfcl if a in agent_red]

                best_per_col = {}

                for j in range(len(TOOL_COUNTS)):

                    col_vals = [agent_red[a][j] if a in agent_red else None for a in red_agents]

                    best_per_col[j] = _best_idx(col_vals, higher_is_better=False)

                lines.append(f"% === {mdisp}: Cross-Turn Redundancy Scaling ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- BFCL Multiturn: Cross-Turn Redundancy pro Tool-Stufe.} ")

                lines.append(f"  \\label{ tab:redundancy-scaling-{mfk}} ")

                lines.append("  \\begin{tabular}{l r r r r}")

                lines.append("    \\toprule")

                lines.append("    Architecture & $t{=}10$ & $t{=}20$ & $t{=}40$ & $t{=}80$ \\\\")

                lines.append("    \\midrule")

                for i, a in enumerate(red_agents):

                    name = AGENT_NAMES_TEX[a]

                    parts = [name]

                    for j, v in enumerate(agent_red[a]):

                        if v is not None:

                            is_best = i in best_per_col[j]

                            parts.append(f"${_bf(f'{v:.2f}', is_best)}$")

                        else:

                            parts.append("--")

                    lines.append(f"    {' & '.join(parts)} \\\\")

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\par\\footnotesize{\\textbf{Fett} = geringste Redundanz.}")

                lines.append("\\end{table}")

                lines.append("")

            max_turns = 0

            agent_turns = {}

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

                if turn_scores:

                    agent_turns[a] = {t: float(np.mean(ss)) for t, ss in turn_scores.items()}

                    max_turns = max(max_turns, max(turn_scores.keys()) + 1)

            if agent_turns and max_turns > 0:

                n_turns = min(max_turns, 8)

                turn_agents = [a for a in agents_bfcl if a in agent_turns]

                best_per_turn = {}

                for j in range(n_turns):

                    col_vals = [agent_turns[a].get(j) if a in agent_turns else None for a in turn_agents]

                    best_per_turn[j] = _best_idx(col_vals, higher_is_better=True)

                lines.append(f"% === {mdisp}: TC per Turn ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- BFCL Multiturn: Tool Correctness pro Turn, aggregiert.} ")

                lines.append(f"  \\label{ tab:tc-per-turn-{mfk}} ")

                turn_cols = " ".join(["r"] * n_turns)

                lines.append(f"  \\begin{ tabular} { l {turn_cols}} ")

                lines.append("    \\toprule")

                turn_headers = " & ".join([f"Turn {i}" for i in range(n_turns)])

                lines.append(f"    Architecture & {turn_headers} \\\\")

                lines.append("    \\midrule")

                for i, a in enumerate(turn_agents):

                    name = AGENT_NAMES_TEX[a]

                    parts = [name]

                    for j in range(n_turns):

                        v = agent_turns[a].get(j)

                        if v is not None:

                            is_best = i in best_per_turn[j]

                            parts.append(f"${_bf(f'{v:.3f}', is_best)}$")

                        else:

                            parts.append("--")

                    lines.append(f"    {' & '.join(parts)} \\\\")

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\par\\footnotesize{\\textbf{Fett} = bester Wert pro Turn.}")

                lines.append("\\end{table}")

                lines.append("")

    return "\n".join(lines)
def _p_to_str(p):

    if p is None:

        return "--"

    if p < 0.001:

        return "$^{***}$"

    elif p < 0.01:

        return "$^{**}$"

    elif p < 0.05:

        return "$^{*}$"

    return "n.s."
def _cliff_delta(a, b):

    """Cliff's Delta effect size."""

    n1, n2 = len(a), len(b)

    if n1 == 0 or n2 == 0:

        return None

    more = sum(1 for x in a for y in b if x > y)

    less = sum(1 for x in a for y in b if x < y)

    return (more - less) / (n1 * n2)
def _cliff_label(d):

    if d is None:

        return "--"

    ad = abs(d)

    if ad < 0.147:

        return f"{d:+.2f} (negligible)"

    elif ad < 0.33:

        return f"{d:+.2f} (small)"

    elif ad < 0.474:

        return f"{d:+.2f} (medium)"

    return f"{d:+.2f} (large)"
def gen_pairwise_tables(all_data):

    """Pairwise Wilcoxon + Cliff's Delta for all 10 architecture pairs."""

    lines = ["% Auto-generated: Pairwise Significance (all 10 architecture pairs)", ""]

    core_metrics = {

        "mcpagentbench": [("Tool Correctness", "TC"), ("Argument Correctness [Reference]", "AC"),

                          ("Final State (Derived)", "FS")],

        "bfcl_multiturn": [("Tool Correctness", "TC"), ("Argument Correctness [Reference]", "AC"),

                           ("State Match", "SM")],

    }

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        mfk = MODEL_FK[model]

        for benchmark in BENCHMARKS:

            agents = available_agents(all_data, model, benchmark)

            if len(agents) < 2:

                continue

            bname = BENCH_NAMES[benchmark]

            for mk, abbr in core_metrics.get(benchmark, []):

                agent_scores = {}

                for a in agents:

                    scores = get_metric_scores(all_data, model, benchmark, a, mk)

                    if scores:

                        agent_scores[a] = scores

                valid_agents = [a for a in agents if a in agent_scores]

                if len(valid_agents) < 2:

                    continue

                pairs = []

                for i, a1 in enumerate(valid_agents):

                    for a2 in valid_agents[i + 1:]:

                        pairs.append((a1, a2))

                lines.append(f"% === {mdisp} x {bname}: {abbr} Pairwise ===")

                lines.append("\\begin{table}[htbp]")

                lines.append("  \\centering")

                lines.append(f"  \\caption{ {mdisp} -- {bname}: {abbr} paarweise Signifikanztests (Wilcoxon + Cliff's Delta).} ")

                lines.append(f"  \\label{ tab:pairwise-{abbr.lower()}-{mfk}-{benchmark}} ")

                lines.append("  \\begin{tabular}{l l r r r r}")

                lines.append("    \\toprule")

                lines.append("    Architektur A & Architektur B & $\\bar{x}_A$ & $\\bar{x}_B$ & Signifikanz & Cliff's $\\delta$ \\\\")

                lines.append("    \\midrule")

                for a1, a2 in pairs:

                    s1 = agent_scores[a1]

                    s2 = agent_scores[a2]

                    m1 = float(np.mean(s1))

                    m2 = float(np.mean(s2))

                    n = min(len(s1), len(s2))

                    if n >= 10:

                        diff = np.array(s1[:n]) - np.array(s2[:n])

                        if np.all(diff == 0):

                            p = 1.0

                        else:

                            try:

                                _, p = stats.wilcoxon(diff)

                            except ValueError:

                                p = None

                    else:

                        p = None

                    cd = _cliff_delta(s1, s2)

                    n1 = AGENT_NAMES_TEX[a1]

                    n2 = AGENT_NAMES_TEX[a2]

                    p_cell = _p_to_str(p)

                    cd_cell = _cliff_label(cd)

                    lines.append(f"    {n1} & {n2} & ${m1:.3f}$ & ${m2:.3f}$ & {p_cell} & {cd_cell} \\\\")

                lines.append("    \\bottomrule")

                lines.append("  \\end{tabular}")

                lines.append("  \\vspace{2pt}")

                lines.append("  \\par\\footnotesize{$^{*}$\\,$p<0.05$, $^{**}$\\,$p<0.01$, $^{***}$\\,$p<0.001$, n.s.\\,= nicht signifikant. "

                             "Cliff's $\\delta$: $<0.147$ negligible, $<0.33$ small, $<0.474$ medium, $\\geq 0.474$ large.}")

                lines.append("\\end{table}")

                lines.append("")

    return "\n".join(lines)
def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    files = {

        "5_1_core_comparison_tables.tex": gen_5_1_overall,

        "5_1_scaling_tables.tex": gen_5_1_scaling,

        "5_1_pairwise_tables.tex": gen_pairwise_tables,

        "5_2_kosten_tokens_tables.tex": gen_5_2_overall,

        "5_2_token_scaling_tables.tex": gen_5_2_scaling,

        "5_3_latenz_tables.tex": gen_5_3_overall,

        "5_3_latenz_scaling_tables.tex": gen_5_3_scaling,

        "5_4_benchmark_tables.tex": gen_5_4,

    }

    for fname, gen_fn in files.items():

        content = gen_fn(all_data)

        (OUTPUT_DIR / fname).write_text(content, encoding="utf-8")

        print(f"  Saved: results/{fname}")

    copy_map = {

        "5_1": "5_1_core_comparison",

        "5_2": "5_2_kosten_tokens",

        "5_3": "5_3_latenz",

        "5_4": "5_4_benchmark_spezifisch",

    }

    for fname in files:

        prefix = fname[:3]

        plot_dir = BASE / "plots" / copy_map.get(prefix, "")

        if plot_dir.exists():

            import shutil

            shutil.copy2(OUTPUT_DIR / fname, plot_dir / fname)

    print("\nDone.")
if __name__ == "__main__":

    main()

