"""
Generate descriptive Markdown text for thesis Chapter 5 sections.
References concrete plot filenames and describes results from both perspectives:
- Modellvergleich (X=Architekturen, Balken=Modelle)
- Architekturvergleich (X=Modelle, Balken=Architekturen)
Output:
  results/5_1_core_comparison.md
  results/5_2_kosten_tokens.md
  results/5_3_latenz.md
  results/5_4_benchmark_spezifisch.md
Usage:
    cd agenttim/evaluation
    python scripts/generate_chapter_texts.py
"""
import json
from pathlib import Path
import numpy as np
from scipy import stats
BASE = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE / "results_enriched"
OUTPUT_DIR = BASE / "results"
AGENT_ORDER = ["single", "orchestrator_fine", "orchestrator_coarse", "router", "swarm"]
AGENT_NAMES = {

    "single": "Single Agent", "orchestrator_fine": "Orchestrator (Fine)",

    "orchestrator_coarse": "Orchestrator (Coarse)", "router": "Router", "swarm": "Swarm",
}
MODELS = ["gpt-5.4-mini", "deepseek/deepseek-v4-pro", "june-gpt-5-4-datazone"]
MODEL_DISPLAY = {

    "gpt-5.4-mini": "GPT-5.4-mini", "deepseek/deepseek-v4-pro": "Deepseek V4 Pro",

    "june-gpt-5-4-datazone": "GPT-5.4",
}
BENCHMARKS = ["mcpagentbench", "bfcl_multiturn"]
BENCH_NAMES = {"mcpagentbench": "MCPAgentBench", "bfcl_multiturn": "BFCL Multiturn"}
BENCH_FK = {"mcpagentbench": "mcpagentbench", "bfcl_multiturn": "bfcl_multiturn"}
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
def available_agents(all_data, model, benchmark):

    found = set()

    for r in all_data:

        if r.get("model") == model and r.get("benchmark") == benchmark:

            found.add(r.get("agent_type"))

    return [a for a in AGENT_ORDER if a in found]
def all_agents_for_benchmark(all_data, benchmark):

    found = set()

    for r in all_data:

        if r.get("benchmark") == benchmark:

            found.add(r.get("agent_type"))

    return [a for a in AGENT_ORDER if a in found]
def get_scores(all_data, model, benchmark, agent, metric_key, num_tools=None):

    scores = []

    for r in _filter(all_data, model, benchmark, agent, num_tools):

        for tc in r.get("test_cases", []):

            s = tc.get("metrics", {}).get(metric_key, {}).get("score")

            if s is not None:

                scores.append(float(s))

    return scores
def mean_ci(scores):

    if not scores:

        return None, None, None

    arr = np.array(scores)

    m = float(np.mean(arr))

    se = float(np.std(arr, ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0

    return m, max(0, m - 1.96 * se), m + 1.96 * se
def wilcoxon_p(a, b):

    n = min(len(a), len(b))

    if n < 10:

        return None

    diff = np.array(a[:n]) - np.array(b[:n])

    if np.all(diff == 0):

        return 1.0

    try:

        _, p = stats.wilcoxon(diff)

        return p

    except ValueError:

        return None
def p_str(p):

    if p is None:

        return "n/a"

    if p < 0.001:

        return "p<0.001"

    elif p < 0.01:

        return f"p={p:.3f}"

    elif p < 0.05:

        return f"p={p:.3f}"

    return f"p={p:.2f} (n.s.)"
def get_token_means(all_data, model, benchmark, agent, num_tools=None):

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

        return None, None, None

    return float(np.mean(prompt)), float(np.mean(completion)), float(np.mean(prompt)) + float(np.mean(completion))
def get_latency_vals(all_data, model, benchmark, agent, num_tools=None):

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

    return vals
def get_efficiency(all_data, model, benchmark, agent):

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
def gen_5_1(all_data):

    lines = ["# 5.1 Core Comparison: Tool Correctness, Argument Correctness, Final State / State Match", ""]

    for benchmark in BENCHMARKS:

        bname = BENCH_NAMES[benchmark]

        bfk = BENCH_FK[benchmark]

        agents = all_agents_for_benchmark(all_data, benchmark)

        if benchmark == "mcpagentbench":

            metrics = [("Tool Correctness", "Tool Correctness", "tool_correctness"),

                       ("Argument Correctness [Reference]", "Argument Correctness", "argument_correctness"),

                       ("Final State (Derived)", "Final State", "final_state")]

        else:

            metrics = [("Tool Correctness", "Tool Correctness", "tool_correctness"),

                       ("Argument Correctness [Reference]", "Argument Correctness", "argument_correctness"),

                       ("State Match", "State Match", "state_match")]

        lines.append(f"## {bname}")

        lines.append("")

        for mk, label, tag in metrics:

            lines.append(f"### {label}")

            lines.append("")

            lines.append(f"**Plots:** `overall/{tag}_{bfk}.png` (Modellvergleich), "

                         f"`overall/{tag}_{bfk}_by_agent.png` (Architekturvergleich), "

                         f"`skalierung/scaling_{tag}_{bfk}.png` (Tool-Skalierung)")

            lines.append("")

            lines.append("**Modellvergleich** (Abbildung: Modellvergleich):")

            lines.append("")

            for a in agents:

                model_results = []

                for model in MODELS:

                    scores = get_scores(all_data, model, benchmark, a, mk)

                    m, ci_lo, ci_hi = mean_ci(scores)

                    if m is not None:

                        model_results.append((model, m, ci_lo, ci_hi))

                if model_results:

                    best = max(model_results, key=lambda x: x[1])

                    worst = min(model_results, key=lambda x: x[1])

                    vals_str = ", ".join([f"{MODEL_DISPLAY[mo]}: {v:.3f}" for mo, v, _, _ in model_results])

                    lines.append(f"- **{AGENT_NAMES[a]}**: {vals_str}. "

                                 f"Bestes Modell: {MODEL_DISPLAY[best[0]]}.")

            lines.append("")

            lines.append("**Architekturvergleich** (Abbildung: Architekturvergleich):")

            lines.append("")

            for model in MODELS:

                mdisp = MODEL_DISPLAY[model]

                single_scores = get_scores(all_data, model, benchmark, "single", mk)

                single_m, _, _ = mean_ci(single_scores)

                arch_results = []

                for a in agents:

                    scores = get_scores(all_data, model, benchmark, a, mk)

                    m, ci_lo, ci_hi = mean_ci(scores)

                    if m is not None:

                        arch_results.append((a, m, scores))

                if not arch_results:

                    continue

                best = max(arch_results, key=lambda x: x[1])

                lines.append(f"- **{mdisp}**: Beste Architektur: {AGENT_NAMES[best[0]]} ({best[1]:.3f}).")

                if single_m is not None:

                    worse = [(a, m, s) for a, m, s in arch_results if a != "single" and m < single_m]

                    better = [(a, m, s) for a, m, s in arch_results if a != "single" and m > single_m]

                    if worse:

                        worst_mas = min(worse, key=lambda x: x[1])

                        p = wilcoxon_p(single_scores, worst_mas[2])

                        lines.append(f"  Schlechteste MAS: {AGENT_NAMES[worst_mas[0]]} "

                                     f"({worst_mas[1]:.3f}, {p_str(p)} vs. Single).")

                    if better:

                        best_mas = max(better, key=lambda x: x[1])

                        p = wilcoxon_p(single_scores, best_mas[2])

                        lines.append(f"  MAS uebertrifft Single: {AGENT_NAMES[best_mas[0]]} "

                                     f"({best_mas[1]:.3f}, {p_str(p)}).")

            lines.append("")

            lines.append("**Tool-Skalierung** (Abbildung: Skalierung):")

            lines.append("")

            for model in MODELS:

                mdisp = MODEL_DISPLAY[model]

                lines.append(f"*{mdisp}:*")

                for a in agents:

                    vals = []

                    for t in TOOL_COUNTS:

                        scores = get_scores(all_data, model, benchmark, a, mk, t)

                        m, _, _ = mean_ci(scores)

                        vals.append(m)

                    if vals[0] is not None and vals[-1] is not None:

                        delta = vals[0] - vals[-1]

                        s10 = get_scores(all_data, model, benchmark, a, mk, 10)

                        s80 = get_scores(all_data, model, benchmark, a, mk, 80)

                        p = wilcoxon_p(s10, s80)

                        direction = "sinkt" if delta > 0.01 else ("steigt" if delta < -0.01 else "stabil")

                        lines.append(f"  {AGENT_NAMES[a]}: t=10: {vals[0]:.3f} -> t=80: {vals[-1]:.3f} "

                                     f"(Delta={delta:+.3f}, {direction}, {p_str(p)})")

                lines.append("")

            lines.append("---")

            lines.append("")

    return "\n".join(lines)
def gen_5_2(all_data):

    lines = ["# 5.2 Kosten und Token-Verbrauch", ""]

    for benchmark in BENCHMARKS:

        bname = BENCH_NAMES[benchmark]

        bfk = BENCH_FK[benchmark]

        agents = all_agents_for_benchmark(all_data, benchmark)

        lines.append(f"## {bname}")

        lines.append("")

        lines.append("### Token-Verbrauch")

        lines.append("")

        lines.append(f"**Plot:** `overall/tokens_{bfk}.png` (Stacked Bars, gruppiert nach Modell)")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            token_data = []

            for a in agents:

                pm, cm, tm = get_token_means(all_data, model, benchmark, a)

                if tm is not None:

                    token_data.append((a, pm, cm, tm))

            if not token_data:

                continue

            cheapest = min(token_data, key=lambda x: x[3])

            costliest = max(token_data, key=lambda x: x[3])

            lines.append(f"**{mdisp}**: Geringster Verbrauch: {AGENT_NAMES[cheapest[0]]} "

                         f"({cheapest[3]:,.0f} Tokens/TC). "

                         f"Hoechster: {AGENT_NAMES[costliest[0]]} ({costliest[3]:,.0f} Tokens/TC, "

                         f"Faktor {costliest[3]/cheapest[3]:.1f}x).")

            lines.append("")

        lines.append("### Token-Effizienz (Success/1k Tokens)")

        lines.append("")

        lines.append(f"**Plots:** `overall/efficiency_{bfk}.png` (Modellvergleich), "

                     f"`overall/efficiency_{bfk}_by_agent.png` (Architekturvergleich)")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            eff_data = []

            for a in agents:

                e = get_efficiency(all_data, model, benchmark, a)

                if e is not None:

                    eff_data.append((a, e))

            if eff_data:

                best = max(eff_data, key=lambda x: x[1])

                lines.append(f"- **{mdisp}**: Effizienteste Architektur: "

                             f"{AGENT_NAMES[best[0]]} ({best[1]:.4f}).")

        lines.append("")

        lines.append("### Token Overhead")

        lines.append("")

        lines.append(f"**Plots:** `overall/token_overhead_{bfk}.png` (Modellvergleich), "

                     f"`overall/token_overhead_{bfk}_by_agent.png` (Architekturvergleich)")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            oh_data = []

            for a in agents:

                oh_scores = []

                for r in _filter(all_data, model, benchmark, a):

                    for tc in r.get("test_cases", []):

                        oh = tc.get("metrics", {}).get("Coordination Token Overhead", {})

                        s = oh.get("score")

                        if s is not None:

                            oh_scores.append(float(s))

                if oh_scores:

                    oh_data.append((a, float(np.mean(oh_scores))))

            if oh_data:

                worst = min(oh_data, key=lambda x: x[1])

                lines.append(f"- **{mdisp}**: Hoechster Overhead: "

                             f"{AGENT_NAMES[worst[0]]} (Score {worst[1]:.3f}).")

        lines.append("")

        lines.append("### Token-Skalierung")

        lines.append("")

        lines.append(f"**Plot:** `skalierung/scaling_tokens_{bfk}.png` (3 Subplots, ein Modell pro Panel)")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            lines.append(f"*{mdisp}:*")

            for a in agents:

                t_vals = []

                for t in TOOL_COUNTS:

                    _, _, tm = get_token_means(all_data, model, benchmark, a, t)

                    t_vals.append(tm)

                if t_vals[0] is not None and t_vals[-1] is not None:

                    factor = t_vals[-1] / t_vals[0]

                    lines.append(f"  {AGENT_NAMES[a]}: {t_vals[0]:,.0f} -> {t_vals[-1]:,.0f} "

                                 f"(Faktor {factor:.1f}x)")

            lines.append("")

        lines.append("---")

        lines.append("")

    return "\n".join(lines)
def gen_5_3(all_data):

    lines = [

        "# 5.3 Latenz",

        "",

        "> **Limitation**: Die Latenz-Werte sind zwischen Modellen nur eingeschraenkt vergleichbar, "

        "da unterschiedliche Hosting-Infrastrukturen verwendet werden (Azure OpenAI fuer GPT-Modelle, "

        "OpenRouter fuer Deepseek). Der Architekturvergleich innerhalb eines Modells ist valide.",

        "",

    ]

    for benchmark in BENCHMARKS:

        bname = BENCH_NAMES[benchmark]

        bfk = BENCH_FK[benchmark]

        agents = all_agents_for_benchmark(all_data, benchmark)

        lines.append(f"## {bname}")

        lines.append("")

        lines.append(f"**Plots:** `overall/latency_{bfk}.png` (Modellvergleich), "

                     f"`overall/latency_{bfk}_by_agent.png` (Architekturvergleich), "

                     f"`skalierung/scaling_latency_{bfk}.png` (Tool-Skalierung)")

        lines.append("")

        lines.append("### Architekturvergleich")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            lat_data = []

            for a in agents:

                vals = get_latency_vals(all_data, model, benchmark, a)

                if vals:

                    m = float(np.mean(vals))

                    med = float(np.median(vals))

                    p95 = float(np.percentile(vals, 95))

                    lat_data.append((a, m, med, p95, vals))

            if not lat_data:

                continue

            fastest = min(lat_data, key=lambda x: x[1])

            slowest = max(lat_data, key=lambda x: x[1])

            lines.append(f"**{mdisp}**: Schnellste Architektur: {AGENT_NAMES[fastest[0]]} "

                         f"({fastest[1]:.1f}s avg, {fastest[2]:.1f}s median). "

                         f"Langsamste: {AGENT_NAMES[slowest[0]]} ({slowest[1]:.1f}s, "

                         f"Faktor {slowest[1]/fastest[1]:.1f}x).")

            lines.append("")

            single_lats = get_latency_vals(all_data, model, benchmark, "single")

            for a, m, med, p95, vals in lat_data:

                p = wilcoxon_p(single_lats, vals) if a != "single" and single_lats else None

                sig = f", {p_str(p)} vs. Single" if p is not None else ""

                lines.append(f"- {AGENT_NAMES[a]}: {m:.1f}s avg, {med:.1f}s median, {p95:.1f}s p95{sig}")

            lines.append("")

        lines.append("### Latenz-Skalierung")

        lines.append("")

        for model in MODELS:

            mdisp = MODEL_DISPLAY[model]

            lines.append(f"*{mdisp}:*")

            for a in agents:

                l_vals = []

                for t in TOOL_COUNTS:

                    vals = get_latency_vals(all_data, model, benchmark, a, t)

                    l_vals.append(float(np.mean(vals)) if vals else None)

                if l_vals[0] is not None and l_vals[-1] is not None:

                    factor = l_vals[-1] / l_vals[0]

                    lines.append(f"  {AGENT_NAMES[a]}: {l_vals[0]:.1f}s -> {l_vals[-1]:.1f}s "

                                 f"(Faktor {factor:.1f}x)")

            lines.append("")

        lines.append("---")

        lines.append("")

    return "\n".join(lines)
def gen_5_4(all_data):

    lines = ["# 5.4 Benchmark-spezifische Metriken", ""]

    lines.append("## MCPAgentBench: Execution Efficiency")

    lines.append("")

    lines.append("Execution Efficiency misst, ob Agenten Tool-Calls korrekt parallelisieren "

                 "(nur fuer Parallel-Modi relevant).")

    lines.append("")

    lines.append("**Plots:** `overall/exec_efficiency_mcpagentbench.png` (Modellvergleich), "

                 "`overall/exec_efficiency_mcpagentbench_by_agent.png` (Architekturvergleich), "

                 "`skalierung/scaling_exec_efficiency_mcpagentbench.png` (Skalierung)")

    lines.append("")

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        agents = available_agents(all_data, model, "mcpagentbench")

        ee_data = []

        single_ee = get_scores(all_data, model, "mcpagentbench", "single", "Execution Efficiency")

        for a in agents:

            scores = get_scores(all_data, model, "mcpagentbench", a, "Execution Efficiency")

            m, ci_lo, ci_hi = mean_ci(scores)

            if m is not None:

                ee_data.append((a, m, ci_lo, ci_hi, scores))

        if ee_data:

            best = max(ee_data, key=lambda x: x[1])

            lines.append(f"**{mdisp}**: Beste Architektur: {AGENT_NAMES[best[0]]} ({best[1]:.3f}). ")

            for a, m, ci_lo, ci_hi, scores in ee_data:

                p = wilcoxon_p(single_ee, scores) if a != "single" and single_ee else None

                sig = f" ({p_str(p)} vs. Single)" if p is not None else ""

                lines.append(f"- {AGENT_NAMES[a]}: {m:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]{sig}")

            lines.append("")

    lines.append("### Skalierung")

    lines.append("")

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        agents = available_agents(all_data, model, "mcpagentbench")

        lines.append(f"*{mdisp}:*")

        for a in agents:

            vals = []

            for t in TOOL_COUNTS:

                scores = get_scores(all_data, model, "mcpagentbench", a, "Execution Efficiency", t)

                m, _, _ = mean_ci(scores)

                vals.append(m)

            if vals[0] is not None and vals[-1] is not None:

                delta = vals[0] - vals[-1]

                lines.append(f"  {AGENT_NAMES[a]}: t=10: {vals[0]:.3f} -> t=80: {vals[-1]:.3f} "

                             f"(Delta={delta:+.3f})")

        lines.append("")

    lines.append("---")

    lines.append("")

    lines.append("## BFCL Multiturn: Cross-Turn Redundancy")

    lines.append("")

    lines.append("Zaehlt wie viele Tool-Calls ueber Turns hinweg unnoetig wiederholt werden.")

    lines.append("")

    lines.append("**Plots:** `overall/cross_turn_redundancy_bfcl_multiturn.png` (Modellvergleich), "

                 "`overall/cross_turn_redundancy_bfcl_multiturn_by_agent.png` (Architekturvergleich), "

                 "`skalierung/scaling_cross_turn_redundancy_bfcl_multiturn.png` (Skalierung)")

    lines.append("")

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        agents = available_agents(all_data, model, "bfcl_multiturn")

        red_data = []

        for a in agents:

            counts = []

            for r in _filter(all_data, model, "bfcl_multiturn", a):

                for tc in r.get("test_cases", []):

                    cnt = tc.get("metrics", {}).get("Tool Correctness", {}).get("cross_turn_redundant_count")

                    if cnt is not None:

                        counts.append(float(cnt))

            if counts:

                m, ci_lo, ci_hi = mean_ci(counts)

                red_data.append((a, m, ci_lo, ci_hi))

        if red_data:

            best = min(red_data, key=lambda x: x[1])

            worst = max(red_data, key=lambda x: x[1])

            lines.append(f"**{mdisp}**: Geringste Redundanz: {AGENT_NAMES[best[0]]} ({best[1]:.2f}). "

                         f"Hoechste: {AGENT_NAMES[worst[0]]} ({worst[1]:.2f}).")

            for a, m, ci_lo, ci_hi in red_data:

                lines.append(f"- {AGENT_NAMES[a]}: {m:.2f} [{ci_lo:.2f}, {ci_hi:.2f}]")

            lines.append("")

    lines.append("---")

    lines.append("")

    lines.append("## BFCL Multiturn: Tool Correctness per Turn")

    lines.append("")

    lines.append("Zeigt wie sich die Tool Correctness ueber die Conversation-Turns entwickelt.")

    lines.append("")

    lines.append("**Plot:** `overall/tc_per_turn_bfcl_multiturn.png` (3 Subplots, ein Modell pro Panel)")

    lines.append("")

    for model in MODELS:

        mdisp = MODEL_DISPLAY[model]

        agents = available_agents(all_data, model, "bfcl_multiturn")

        lines.append(f"**{mdisp}:**")

        for a in agents:

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

                first = float(np.mean(turn_scores.get(0, [0])))

                last_key = max(turn_scores.keys())

                last = float(np.mean(turn_scores[last_key]))

                trend = "sinkend" if first - last > 0.02 else ("steigend" if last - first > 0.02 else "stabil")

                t_strs = [f"T{t}: {np.mean(ss):.3f}" for t, ss in sorted(turn_scores.items())]

                lines.append(f"- {AGENT_NAMES[a]}: {', '.join(t_strs)} (Trend: {trend})")

        lines.append("")

    return "\n".join(lines)
def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading results...")

    all_data = load_all()

    print(f"  Loaded {len(all_data)} result files")

    files = {

        "5_1_core_comparison.md": gen_5_1,

        "5_2_kosten_tokens.md": gen_5_2,

        "5_3_latenz.md": gen_5_3,

        "5_4_benchmark_spezifisch.md": gen_5_4,

    }

    for fname, gen_fn in files.items():

        content = gen_fn(all_data)

        path = OUTPUT_DIR / fname

        path.write_text(content, encoding="utf-8")

        print(f"  Saved: results/{fname}")

        chapter = fname.replace(".md", "").split("_", 2)

        plot_dir = BASE / "plots" / f"{'_'.join(chapter[:2])}_{chapter[2]}" if len(chapter) > 2 else None

        if plot_dir and plot_dir.exists():

            (plot_dir / fname).write_text(content, encoding="utf-8")

            print(f"  Copied to: plots/{plot_dir.name}/{fname}")

    print("\nDone.")
if __name__ == "__main__":

    main()

