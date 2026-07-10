"""
Streamlit Evaluation Dashboard for AgentTim.
Visualizes evaluation results from evaluation script runs.
Organized by domain (MCPAgentBench, BFCL) with comparison
across agent types (single vs multi/orchestrator).
Run with: cd agenttim/evaluation && .venv/Scripts/streamlit run dashboard/streamlit_eval.py
"""
import json
import io
from datetime import datetime
from pathlib import Path
from typing import Any
import altair as alt
import pandas as pd
import streamlit as st
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
TEST_CASES_DIR = Path(__file__).resolve().parent.parent / "test_cases"
DOMAIN_DISPLAY_NAMES = {

    "mcpagentbench": "MCPAgentBench",

    "bfcl": "BFCL",

    "bfcl_multiturn": "BFCL Multi-Turn",
}
TEST_CASE_DIRS = {

    "mcpagentbench": "mcpagentbench_data",

    "bfcl": "bfcl_data",

    "bfcl_multiturn": "bfcl_data",
}
def _discover_domains() -> dict[str, str]:

    """Discover domains dynamically from results/ subdirectories.

    Supports both flat (results/benchmark/*.json) and nested
    (results/model/benchmark/tools/*.json) structures.
    """

    domains: dict[str, str] = {}

    if not RESULTS_DIR.exists():

        return domains

    for json_file in RESULTS_DIR.rglob("*.json"):

        if "_errors" in json_file.name:

            continue

        try:

            data = json.loads(json_file.read_text(encoding="utf-8"))

            benchmark = data.get("benchmark")

            if benchmark and benchmark not in domains:

                domains[benchmark] = DOMAIN_DISPLAY_NAMES.get(

                    benchmark, benchmark.replace("_", " ").title()

                )

        except (json.JSONDecodeError, OSError):

            continue

    return dict(sorted(domains.items()))
METRIC_NAMES = [

    "Tool Correctness",

    "Argument Correctness [Reference]",

    "State Match",

    "Correctness",

    "Clarification Quality",

    "Execution Efficiency",

    "Coordination Token Overhead",
]
st.set_page_config(page_title="AgentTim Evaluation", layout="wide")
def _normalize_result(data: dict[str, Any]) -> dict[str, Any]:

    """Normalize alternate result formats to the standard dashboard schema.

    Handles the 'summary/per_case' format (e.g. bfcl_multiturn evaluator)
    by mapping it to the 'aggregate/test_cases' format the dashboard expects.
    """

    if "test_cases" in data:

        return data

    if "per_case" not in data:

        return data

    summary = data.get("summary", {})

    per_case = data.get("per_case", [])

    total_prompt = sum(tc.get("tokens", {}).get("prompt", 0) for tc in per_case)

    total_completion = sum(tc.get("tokens", {}).get("completion", 0) for tc in per_case)

    total_latency = summary.get("total_latency_s", sum(tc.get("latency_s", 0) for tc in per_case))

    data["aggregate"] = {

        "total_prompt_tokens": total_prompt,

        "total_completion_tokens": total_completion,

        "total_tokens": total_prompt + total_completion,

        "total_llm_calls": sum(tc.get("tools_called", 0) for tc in per_case),

        "total_cost": 0,

        "total_latency": round(total_latency, 3),

        "avg_latency": round(summary.get("avg_latency_s", total_latency / max(len(per_case), 1)), 3),

    }

    data["num_test_cases"] = summary.get("total", len(per_case))

    test_cases = []

    for tc in per_case:

        passed = tc.get("pass", False)

        tokens = tc.get("tokens", {})

        prompt_tokens = tokens.get("prompt", 0)

        completion_tokens = tokens.get("completion", 0)

        metrics = {}

        metrics["Pass/Fail"] = {

            "score": 1.0 if passed else 0.0,

            "threshold": 1.0,

            "success": passed,

            "reason": tc.get("state_match") or ("Passed" if passed else "Failed"),

            "error": None,

            "strict_mode": False,

            "evaluation_model": None,

            "evaluation_cost": None,

            "verbose_logs": None,

            "comparison": {},

        }

        test_cases.append({

            "id": tc.get("id", ""),

            "dimension": data.get("mode", ""),

            "category": data.get("mode", ""),

            "description": "",

            "input": tc.get("id", ""),

            "expected_output": "",

            "actual_output": f"{'PASS' if passed else 'FAIL'} ({tc.get('tools_called', 0)} tools, {tc.get('turns', 0)} turns)",

            "expected_tools": [],

            "tools_called": [],

            "all_tools_called": [],

            "metrics": metrics,

            "tokens": {

                "prompt_tokens": prompt_tokens,

                "completion_tokens": completion_tokens,

                "total_tokens": prompt_tokens + completion_tokens,

                "llm_calls": tc.get("turns", 0),

                "cost": 0,

            },

            "latency": {

                "total": round(tc.get("latency_s", 0), 3),

                "llm_latencies": [],

            },

        })

    data["test_cases"] = test_cases

    return data
@st.cache_data(ttl=60)
def load_domain_results(domain_key: str) -> list[dict[str, Any]]:

    """Load all JSON result files for a domain, sorted newest first.

    Searches recursively through results/ to support both flat and nested structures.
    """

    results = []

    if not RESULTS_DIR.exists():

        return results

    for f in sorted(RESULTS_DIR.rglob("*.json"), reverse=True):

        if "_errors" in f.name:

            continue

        try:

            data = json.loads(f.read_text(encoding="utf-8"))

            if not isinstance(data, dict):

                continue

            if data.get("benchmark") != domain_key:

                continue

            data["_filename"] = f.name

            data = _normalize_result(data)

            results.append(data)

        except (json.JSONDecodeError, KeyError, OSError):

            continue

    return results
def get_test_case_files(domain_key: str) -> list[Path]:

    """Get all test case files for a domain."""

    tc_dir = TEST_CASES_DIR / TEST_CASE_DIRS.get(domain_key, domain_key)

    if not tc_dir.exists():

        return []

    py_files = sorted(tc_dir.glob("*.py"))

    json_files = sorted(tc_dir.glob("*.json"))

    py_files = [f for f in py_files if f.name != "__init__.py"]

    json_files = [f for f in json_files if f.name != "tool_schemas.json"]

    return py_files + json_files
@st.cache_data(ttl=300)
def load_test_cases_from_file(filepath: str) -> list[dict]:

    """Load test cases from a .py or .json file.

    Note: filepath is str (not Path) for st.cache_data hashability.
    """

    filepath = Path(filepath)

    if filepath.suffix == ".json":

        try:

            data = json.loads(filepath.read_text(encoding="utf-8"))

            return data if isinstance(data, list) else [data]

        except (json.JSONDecodeError, KeyError):

            return []

    return []
def format_timestamp(ts: str) -> str:

    try:

        dt = datetime.fromisoformat(ts)

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except (ValueError, TypeError):

        return ts
def _get_run_mode(run: dict) -> str:

    """Extract mode/dimension from run metadata."""

    mode = run.get("mode", "")

    if mode:

        return mode

    for tc in run.get("test_cases", []):

        dim = tc.get("dimension", "")

        if dim:

            return dim

    return "unknown"
def _get_run_agent_type(run: dict) -> str:

    return run.get("agent_type", "unknown")
def _get_run_num_tools(run: dict) -> int | None:

    """Extract num_tools from run metadata (None = all tools)."""

    return run.get("num_tools")
def _get_run_model(run: dict) -> str:

    return run.get("model", "unknown")
def _get_run_key(run: dict) -> str:

    """Unique key: agent_type + mode."""

    return f"{_get_run_agent_type(run)}_{_get_run_mode(run)}"
def get_mode_label(mode: str) -> str:

    return mode.replace("-", " ").replace("_", " ").title()
def get_models(results: list[dict]) -> list[str]:

    """Get unique model names from results."""

    return sorted(set(_get_run_model(r) for r in results))
def _compute_run_metrics(run: dict) -> dict[str, Any]:

    """Compute aggregate metric scores for a single run."""

    test_cases = run.get("test_cases", [])

    if not test_cases:

        return {}

    metric_scores: dict[str, list[float]] = {}

    total_metrics = 0

    passed_metrics = 0

    for tc in test_cases:

        for metric_name, metric_data in tc.get("metrics", {}).items():

            score = metric_data.get("score")

            if score is None:

                continue

            total_metrics += 1

            if metric_data.get("success"):

                passed_metrics += 1

            metric_scores.setdefault(metric_name, []).append(score)

    pass_rate = (passed_metrics / total_metrics) if total_metrics > 0 else 0

    result = {

        "pass_rate": pass_rate,

        "num_cases": len(test_cases),

    }

    for name, scores in metric_scores.items():

        result[f"avg_{name}"] = sum(scores) / len(scores) if scores else 0

    agg = run.get("aggregate", {})

    result["avg_latency"] = agg.get("avg_latency", 0)

    result["total_tokens"] = agg.get("total_tokens", 0)

    result["total_cost"] = agg.get("total_cost", 0)

    result["total_llm_calls"] = agg.get("total_llm_calls", 0)

    return result
def group_results_by_mode(results: list[dict]) -> dict[str, list[dict]]:

    """Group results by mode, each list sorted newest first."""

    grouped: dict[str, list[dict]] = {}

    for r in results:

        mode = _get_run_mode(r)

        grouped.setdefault(mode, []).append(r)

    return grouped
def get_agent_types(results: list[dict]) -> list[str]:

    """Get unique agent types from results."""

    types = set()

    for r in results:

        types.add(_get_run_agent_type(r))

    return sorted(types)
def get_latest_by_agent(runs: list[dict]) -> dict[str, dict]:

    """From a list of runs, get the latest run per agent type."""

    latest: dict[str, dict] = {}

    for r in runs:

        agent = _get_run_agent_type(r)

        if agent not in latest:

            latest[agent] = r

    return latest
def render_overview_tab(results: list[dict]):

    """Render overview with comparison across agent types per mode."""

    st.subheader("Overview - Agent Comparison per Dimension")

    if not results:

        st.info("No evaluation results found.")

        return

    grouped = group_results_by_mode(results)

    agent_types = get_agent_types(results)

    rows = []

    for mode in sorted(grouped.keys()):

        latest_by_agent = get_latest_by_agent(grouped[mode])

        for agent in agent_types:

            run = latest_by_agent.get(agent)

            if not run:

                continue

            metrics = _compute_run_metrics(run)

            tool_score = metrics.get("avg_Tool Correctness", 0)

            rows.append({

                "Mode": mode,

                "Agent": agent,

                "Cases": metrics.get("num_cases", 0),

                "Pass Rate": f"{metrics.get('pass_rate', 0) * 100:.0f}%",

                "Tool Correct.": f"{tool_score:.2f}",

                "Arg Correct.": f"{metrics.get('avg_Argument Correctness [Reference]', 0):.2f}",

                "Exec Efficiency": f"{metrics.get('avg_Execution Efficiency', 0):.2f}",

                "Avg Latency": f"{metrics.get('avg_latency', 0):.1f}s",

                "Tokens": f"{metrics.get('total_tokens', 0):,}",

                "Cost": f"${metrics.get('total_cost', 0):.4f}",

            })

    if rows:

        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True, hide_index=True)

    if len(agent_types) > 1:

        st.markdown("#### Agent Comparison")

        chart_rows = []

        for mode in sorted(grouped.keys()):

            latest_by_agent = get_latest_by_agent(grouped[mode])

            for agent in agent_types:

                run = latest_by_agent.get(agent)

                if not run:

                    continue

                metrics = _compute_run_metrics(run)

                chart_rows.append({

                    "Mode": get_mode_label(mode),

                    "Agent": agent,

                    "Tool Correctness": metrics.get("avg_Tool Correctness", 0),

                    "Arg Correctness": metrics.get("avg_Argument Correctness [Reference]", 0),

                    "Pass Rate": metrics.get("pass_rate", 0),

                    "Avg Latency (s)": metrics.get("avg_latency", 0),

                })

        if chart_rows:

            chart_df = pd.DataFrame(chart_rows)

            score_df = chart_df.melt(

                id_vars=["Mode", "Agent"],

                value_vars=["Tool Correctness", "Arg Correctness"],

                var_name="Metric",

                value_name="Score",

            )

            score_chart = (

                alt.Chart(score_df)

                .mark_bar()

                .encode(

                    x=alt.X("Agent:N", title=None),

                    y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 1])),

                    color="Agent:N",

                    column=alt.Column("Mode:N", title=None),

                    row=alt.Row("Metric:N", title=None),

                    tooltip=["Mode", "Agent", "Metric", "Score"],

                )

                .properties(width=120, height=150)

            )

            st.altair_chart(score_chart)

            latency_chart = (

                alt.Chart(chart_df)

                .mark_bar()

                .encode(

                    x=alt.X("Agent:N", title=None),

                    y=alt.Y("Avg Latency (s):Q"),

                    color="Agent:N",

                    column=alt.Column("Mode:N", title=None),

                    tooltip=["Mode", "Agent", "Avg Latency (s)"],

                )

                .properties(width=120, height=200)

            )

            st.markdown("#### Latency Comparison")

            st.altair_chart(latency_chart)
def render_dimension_tab(results: list[dict], mode_key: str):

    """Render test case details for a specific dimension with agent selector."""

    matching = [r for r in results if _get_run_mode(r) == mode_key]

    if not matching:

        st.info(f"No results for: {mode_key}")

        return

    agent_types = sorted(set(_get_run_agent_type(r) for r in matching))

    if len(agent_types) > 1:

        selected_agent = st.radio(

            "Agent Type",

            options=agent_types,

            horizontal=True,

            key=f"agent_{mode_key}",

        )

        run = next((r for r in matching if _get_run_agent_type(r) == selected_agent), matching[0])

    else:

        run = matching[0]

    agg = run.get("aggregate", {})

    test_cases = run.get("test_cases", [])

    st.caption(

        f"Run: {format_timestamp(run.get('timestamp', ''))} | "

        f"Agent: {_get_run_agent_type(run)} | "

        f"Model: {run.get('model', '')} | "

        f"Cases: {len(test_cases)}"

    )

    metrics = _compute_run_metrics(run)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Pass Rate", f"{metrics.get('pass_rate', 0) * 100:.0f}%")

    col2.metric("Tokens", f"{agg.get('total_tokens', 0):,}")

    col3.metric("Cost", f"${agg.get('total_cost', 0):.4f}")

    col4.metric("Avg Latency", f"{agg.get('avg_latency', 0):.2f}s")

    col5.metric("LLM Calls", agg.get("total_llm_calls", 0))

    st.divider()

    total_tc = len(test_cases)

    TC_PAGE_SIZE = 25

    if total_tc > TC_PAGE_SIZE:

        num_pages = (total_tc + TC_PAGE_SIZE - 1) // TC_PAGE_SIZE

        tc_page = st.number_input(

            "Page", min_value=1, max_value=num_pages, value=1,

            key=f"dim_tc_page_{mode_key}",

        )

        tc_start = (tc_page - 1) * TC_PAGE_SIZE

        tc_end = min(tc_start + TC_PAGE_SIZE, total_tc)

        test_cases_page = test_cases[tc_start:tc_end]

        st.caption(f"Showing test cases {tc_start + 1}-{tc_end} of {total_tc}")

    else:

        test_cases_page = test_cases

        tc_start = 0

    for i, tc in enumerate(test_cases_page, tc_start + 1):

        tokens = tc.get("tokens", {})

        latency = tc.get("latency", {})

        all_metrics_ok = all(

            m.get("success", False)

            for m in tc.get("metrics", {}).values()

            if m.get("score") is not None

        )

        status_icon = "\u2705" if all_metrics_ok else "\u274c"

        tc_id = tc.get("id", f"#{i}")

        with st.expander(

            f"{status_icon} [{tc_id}] {tc.get('input', '')[:100]}",

            expanded=False,

        ):

            st.markdown(f"**Input:** {tc.get('input', '')}")

            if tc.get("actual_output"):

                st.markdown(f"**Output:** {tc['actual_output'][:500]}")

            st.divider()

            for metric_name, metric_data in tc.get("metrics", {}).items():

                is_ok = metric_data.get("success", False)

                raw_score = metric_data.get("score")

                threshold = metric_data.get("threshold", 0)

                if raw_score is None:

                    metric_icon, metric_label = "\u26aa", "N/A"

                elif is_ok:

                    metric_icon, metric_label = "\u2705", "PASS"

                else:

                    metric_icon, metric_label = "\u274c", "FAIL"

                score_display = "N/A" if raw_score is None else f"{raw_score:.2f}"

                header = f"{metric_icon} {metric_name} — {metric_label} (Score: {score_display})"

                with st.expander(header, expanded=False):

                    comparison = metric_data.get("comparison", {})

                    if comparison:

                        expected = comparison.get("expected")

                        actual = comparison.get("actual")

                        if isinstance(expected, list) and isinstance(actual, list):

                            col_a, col_b = st.columns(2)

                            with col_a:

                                st.markdown("**Expected:**")

                                for item in expected:

                                    if isinstance(item, dict):

                                        params = item.get("input_parameters") or item.get("arguments", {})

                                        st.code(f"{item.get('name', item)}({params})", language="python")

                                    else:

                                        st.code(str(item), language="python")

                            with col_b:

                                st.markdown("**Actual:**")

                                for item in actual:

                                    if isinstance(item, dict):

                                        params = item.get("input_parameters") or item.get("arguments", {})

                                        st.code(f"{item.get('name', item)}({params})", language="python")

                                    else:

                                        st.code(str(item), language="python")

                    if metric_name == "Tool Correctness":

                        per_turn_data = metric_data.get("per_turn", tc.get("per_turn", []))

                        if per_turn_data and isinstance(per_turn_data[0], dict):

                            cross_turn_total = metric_data.get("cross_turn_redundant_count", 0)

                            if cross_turn_total:

                                st.warning(f"Cross-turn redundant calls: {cross_turn_total}")

                            st.markdown("**Per-Turn Tool Calls:**")

                            for turn_info in per_turn_data:

                                turn_idx = turn_info.get("turn", 0)

                                turn_ok = turn_info.get("success", turn_info.get("tool_match", False))

                                expected_t = turn_info.get("expected", [])

                                actual_t = turn_info.get("actual", [])

                                redundant = turn_info.get("cross_turn_redundant", [])

                                turn_icon = "\u2705" if turn_ok else "\u274c"

                                with st.container():

                                    score_str = f" ({turn_info['score']:.2f})" if "score" in turn_info else ""

                                    st.markdown(f"{turn_icon} **Turn {turn_idx}**{score_str}")

                                    col_exp, col_act = st.columns(2)

                                    with col_exp:

                                        st.markdown("Expected:")

                                        if expected_t:

                                            st.code(", ".join(expected_t), language="text")

                                        else:

                                            st.caption("(no tools expected)")

                                    with col_act:

                                        st.markdown("Actual:")

                                        if actual_t:

                                            st.code(", ".join(actual_t), language="text")

                                        else:

                                            st.caption("(no tools called)")

                                    if redundant:

                                        st.caption(f"Cross-turn redundant: {', '.join(redundant)}")

                    if metric_name == "State Match" and comparison:

                        for cls_name, cls_info in comparison.items():

                            cls_match = cls_info.get("match", True)

                            cls_icon = "\u2705" if cls_match else "\u274c"

                            diffs = cls_info.get("diffs", [])

                            st.markdown(f"{cls_icon} **{cls_name}**")

                            if diffs and isinstance(diffs, list):

                                for diff in diffs:

                                    if isinstance(diff, dict):

                                        attr = diff.get("attribute", "?")

                                        exp = diff.get("expected", "")

                                        act = diff.get("actual", "")

                                        st.markdown(f"- `{attr}`:")

                                        col_e, col_a = st.columns(2)

                                        col_e.code(f"Expected: {exp}", language="text")

                                        col_a.code(f"Actual:   {act}", language="text")

                                    else:

                                        st.text(str(diff))

                    if "Argument Correctness" in metric_name:

                        per_turn_mismatches = metric_data.get("per_turn_mismatches", [])

                        if per_turn_mismatches:

                            st.markdown("**Per-Turn Argument Mismatches:**")

                            for turn_mismatch in per_turn_mismatches:

                                turn_idx = turn_mismatch.get("turn", 0)

                                mismatches = turn_mismatch.get("mismatches", [])

                                st.markdown(f"\u274c **Turn {turn_idx}** ({len(mismatches)} mismatch{'es' if len(mismatches) != 1 else ''})")

                                for mm in mismatches:

                                    tool_name = mm.get("tool", "")

                                    param = mm.get("param", "")

                                    exp_val = mm.get("expected", "")

                                    act_val = mm.get("actual", "")

                                    col_p, col_e, col_a = st.columns([1, 2, 2])

                                    col_p.code(f"{tool_name}.{param}", language="text")

                                    col_e.code(f"Expected: {exp_val}", language="text")

                                    col_a.code(f"Actual: {act_val}", language="text")

                    if metric_name == "Execution Efficiency" and comparison:

                        expected_steps = comparison.get("expected_steps", [])

                        checks = comparison.get("checks", [])

                        if expected_steps:

                            st.markdown("**Expected Execution Steps:**")

                            is_multi_step = len(expected_steps) > 1

                            for s_idx, step in enumerate(expected_steps, 1):

                                mode = "parallel" if len(step) > 1 else ("sequential" if is_multi_step else "single")

                                st.code(f"Step {s_idx} ({mode}): {', '.join(step)}", language="text")

                        if checks:

                            st.markdown("**Checks:**")

                            for check in checks:

                                icon = "\u2705" if check["result"] == "pass" else "\u274c"

                                st.markdown(

                                    f"{icon} **{check['type'].title()}** (Step {check['step']}): "

                                    f"`{' + '.join(check['tools'])}` — {check['detail']}"

                                )

                    m1, m2, m3 = st.columns(3)

                    m1.metric("Score", "N/A" if raw_score is None else f"{raw_score:.2f}")

                    m2.metric("Threshold", f"{threshold:.2f}")

                    chip_color = "#4caf50" if is_ok else ("#9e9e9e" if raw_score is None else "#f44336")

                    m3.markdown(

                        f'<span style="background-color:{chip_color};color:white;padding:4px 16px;'

                        f'border-radius:16px;font-weight:bold;font-size:14px;">{metric_label}</span>',

                        unsafe_allow_html=True,

                    )

                    if metric_data.get("reason"):

                        st.info(metric_data["reason"])

            st.divider()

            lc1, lc2, lc3 = st.columns(3)

            lc1.metric("Tokens", f"{tokens.get('total_tokens', 0):,}")

            lc2.metric("Latency", f"{latency.get('total', 0):.2f}s")

            lc3.metric("LLM Calls", tokens.get("llm_calls", 0))

            all_tools = tc.get("all_tools_called", [])

            if all_tools and any("start_time" in t for t in all_tools):

                st.markdown("**Tool Timeline:**")

                timeline_rows = []

                for idx, t in enumerate(all_tools):

                    start = t.get("start_time", 0)

                    dur = t.get("latency", 0)

                    timeline_rows.append({

                        "Tool": f"{idx + 1}. {t['name']}",

                        "Start": start,

                        "End": round(start + dur, 3),

                        "Label": f"{dur:.2f}s",

                    })

                tl_df = pd.DataFrame(timeline_rows)

                bars = alt.Chart(tl_df).mark_bar(cornerRadiusEnd=4).encode(

                    x=alt.X("Start:Q", title="Time (s)"),

                    x2="End:Q",

                    y=alt.Y("Tool:N", sort=None, title=None),

                    color=alt.Color("Tool:N", legend=None),

                    tooltip=["Tool", "Start", "End", "Label"],

                )

                text = alt.Chart(tl_df).mark_text(align="left", dx=4, fontSize=12).encode(

                    x="End:Q", y=alt.Y("Tool:N", sort=None), text="Label:N",

                )

                chart = (bars + text).properties(height=max(len(all_tools) * 35, 80))

                st.altair_chart(chart, use_container_width=True)
def render_test_cases_tab(domain_key: str):

    st.subheader("Test Case Definitions")

    tc_files = get_test_case_files(domain_key)

    if not tc_files:

        st.info(f"No test case files found for {DOMAINS.get(domain_key, domain_key)}.")

        return

    selected_file = st.selectbox(

        "Test Case File", options=tc_files,

        format_func=lambda f: f.stem, key=f"tc_file_{domain_key}",

    )

    cases = load_test_cases_from_file(str(selected_file))

    total_cases = len(cases)

    st.caption(f"{total_cases} test cases in {selected_file.name}")

    PAGE_SIZE = 20

    if total_cases > PAGE_SIZE:

        num_pages = (total_cases + PAGE_SIZE - 1) // PAGE_SIZE

        page = st.number_input(

            "Page", min_value=1, max_value=num_pages, value=1,

            key=f"tc_page_{domain_key}",

        )

        start_idx = (page - 1) * PAGE_SIZE

        end_idx = min(start_idx + PAGE_SIZE, total_cases)

        cases_page = cases[start_idx:end_idx]

        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_cases}")

    else:

        cases_page = cases

        start_idx = 0

    for i, tc in enumerate(cases_page, start_idx + 1):

        tc_id = tc.get("id", f"#{i}")

        tc_input = tc.get("input", tc.get("description", ""))[:100]

        turns = tc.get("turns", [])

        turn_label = f" ({len(turns)} turns)" if turns else ""

        with st.expander(f"[{tc_id}]{turn_label} {tc_input}", expanded=False):

            if turns:

                st.markdown("**Multi-Turn Conversation:**")

                for turn_idx, turn in enumerate(turns):

                    turn_input = turn.get("input", "")[:150]

                    expected_calls = turn.get("expected_tool_calls", [])

                    st.markdown(f"**Turn {turn_idx}:** {turn_input}")

                    if expected_calls:

                        st.markdown("Expected Tool Calls:")

                        for tool in expected_calls:

                            if isinstance(tool, dict):

                                name = tool.get("name", "")

                                args = tool.get("arguments", tool.get("input_parameters", {}))

                                st.code(f"{name}({json.dumps(args, ensure_ascii=False)})", language="python")

                    else:

                        st.caption("(no tools expected)")

                    st.divider()

            else:

                expected = tc.get("expected_tool_calls", tc.get("expected_tools", []))

                if expected:

                    st.markdown("**Expected Tool Calls:**")

                    for tool in expected:

                        if isinstance(tool, dict):

                            name = tool.get("name", "")

                            args = tool.get("arguments", tool.get("input_parameters", {}))

                            st.code(f"{name}({json.dumps(args, ensure_ascii=False)})", language="python")

            exec_pattern = tc.get("expected_execution", [])

            if exec_pattern:

                st.markdown("**Execution Pattern:**")

                for step_idx, step in enumerate(exec_pattern, 1):

                    mode = "parallel" if len(step) > 1 else ("sequential" if len(exec_pattern) > 1 else "single")

                    st.code(f"Step {step_idx} ({mode}): {', '.join(step)}", language="text")

            with st.expander("Raw JSON", expanded=False):

                st.json(tc)
def _get_tool_count_label(num_tools: int | None) -> str:

    """Human-readable label for a tool count value."""

    if num_tools is None:

        return "all"

    return str(num_tools)
def render_tool_count_tab(results: list[dict]):

    """Compare performance across different tool counts (num_tools)."""

    st.subheader("Tool Count Comparison")

    tool_counts: set[int | None] = set()

    for r in results:

        tool_counts.add(_get_run_num_tools(r))

    if len(tool_counts) <= 1:

        st.info(

            "Only one tool count found in results. "

            "Run evaluations with different `--num-tools` values to compare."

        )

        return

    seen: dict[str, dict] = {}

    for r in results:

        key = f"{_get_run_agent_type(r)}|{_get_run_num_tools(r)}|{_get_run_mode(r)}"

        if key not in seen:

            seen[key] = r

    runs = list(seen.values())

    agg_data: dict[str, dict] = {}

    for r in runs:

        agent = _get_run_agent_type(r)

        nt = _get_run_num_tools(r)

        agg_key = f"{agent}|{nt}"

        if agg_key not in agg_data:

            agg_data[agg_key] = {

                "agent": agent,

                "num_tools": nt,

                "tool_scores": [],

                "arg_scores": [],

                "final_scores": [],

                "latencies": [],

                "tokens": 0,

                "cost": 0.0,

                "cases": 0,

                "llm_calls": 0,

            }

        d = agg_data[agg_key]

        agg = r.get("aggregate", {})

        tcs = r.get("test_cases", [])

        d["cases"] += len(tcs)

        d["tokens"] += agg.get("total_tokens", 0)

        d["cost"] += agg.get("total_cost", 0)

        d["llm_calls"] += agg.get("total_llm_calls", 0)

        for tc in tcs:

            for metric_key, bucket in [

                ("Tool Correctness", "tool_scores"),

                ("Argument Correctness [Reference]", "arg_scores"),

                ("Final State (Derived)", "final_scores"),

            ]:

                s = tc.get("metrics", {}).get(metric_key, {}).get("score")

                if s is not None:

                    d[bucket].append(s)

            lat = tc.get("latency", {}).get("total")

            if lat is not None:

                d["latencies"].append(lat)

    def safe_avg(lst: list) -> float | None:

        return round(sum(lst) / len(lst), 4) if lst else None

    table_rows = []

    for d in sorted(agg_data.values(), key=lambda x: (x["agent"], x["num_tools"] or 9999)):

        n = d["cases"]

        table_rows.append({

            "Agent": d["agent"],

            "Tools": _get_tool_count_label(d["num_tools"]),

            "Cases": n,

            "Tool Corr.": f"{safe_avg(d['tool_scores']) or 0:.2f}",

            "Arg Corr.": f"{safe_avg(d['arg_scores']) or 0:.2f}",

            "Final State": f"{safe_avg(d['final_scores']) or 0:.2f}",

            "Avg Latency": f"{safe_avg(d['latencies']) or 0:.1f}s",

            "Tokens/Case": f"{d['tokens'] // n:,}" if n else "-",

            "Cost/Case": f"${d['cost'] / n:.4f}" if n else "-",

        })

    if table_rows:

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    chart_rows = []

    for d in agg_data.values():

        chart_rows.append({

            "Agent": d["agent"],

            "Tools": _get_tool_count_label(d["num_tools"]),

            "num_tools_sort": d["num_tools"] or 9999,

            "Tool Correctness": safe_avg(d["tool_scores"]) or 0,

            "Arg Correctness": safe_avg(d["arg_scores"]) or 0,

            "Final State": safe_avg(d["final_scores"]) or 0,

            "Avg Latency (s)": safe_avg(d["latencies"]) or 0,

            "Tokens/Case": d["tokens"] / d["cases"] if d["cases"] else 0,

        })

    if not chart_rows:

        return

    chart_df = pd.DataFrame(chart_rows)

    st.markdown("#### Accuracy by Tool Count")

    score_df = chart_df.melt(

        id_vars=["Agent", "Tools", "num_tools_sort"],

        value_vars=["Tool Correctness", "Arg Correctness", "Final State"],

        var_name="Metric",

        value_name="Score",

    )

    score_chart = (

        alt.Chart(score_df)

        .mark_bar()

        .encode(

            x=alt.X("Tools:N", sort=alt.EncodingSortField(field="num_tools_sort"), title="Tool Count"),

            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 1]), title="Score"),

            color="Agent:N",

            xOffset="Agent:N",

            row=alt.Row("Metric:N", title=None),

            tooltip=["Agent", "Tools", "Metric", alt.Tooltip("Score:Q", format=".2f")],

        )

        .properties(width=500, height=180)

    )

    st.altair_chart(score_chart)

    st.markdown("#### Latency by Tool Count")

    latency_chart = (

        alt.Chart(chart_df)

        .mark_bar()

        .encode(

            x=alt.X("Tools:N", sort=alt.EncodingSortField(field="num_tools_sort"), title="Tool Count"),

            y=alt.Y("Avg Latency (s):Q", title="Avg Latency (s)"),

            color="Agent:N",

            xOffset="Agent:N",

            tooltip=["Agent", "Tools", alt.Tooltip("Avg Latency (s):Q", format=".1f")],

        )

        .properties(width=500, height=250)

    )

    st.altair_chart(latency_chart)

    st.markdown("#### Token Usage by Tool Count")

    token_chart = (

        alt.Chart(chart_df)

        .mark_bar()

        .encode(

            x=alt.X("Tools:N", sort=alt.EncodingSortField(field="num_tools_sort"), title="Tool Count"),

            y=alt.Y("Tokens/Case:Q", title="Tokens per Case"),

            color="Agent:N",

            xOffset="Agent:N",

            tooltip=["Agent", "Tools", alt.Tooltip("Tokens/Case:Q", format=",.0f")],

        )

        .properties(width=500, height=250)

    )

    st.altair_chart(token_chart)

    st.markdown("#### Per-Mode Breakdown")

    mode_rows = []

    for r in runs:

        metrics = _compute_run_metrics(r)

        mode_rows.append({

            "Agent": _get_run_agent_type(r),

            "Tools": _get_tool_count_label(_get_run_num_tools(r)),

            "Mode": _get_run_mode(r),

            "Cases": metrics.get("num_cases", 0),

            "Tool Corr.": f"{metrics.get('avg_Tool Correctness', 0):.2f}",

            "Arg Corr.": f"{metrics.get('avg_Argument Correctness [Reference]', 0):.2f}",

            "Final State": f"{metrics.get('avg_Final State (Derived)', 0):.2f}",

            "Avg Latency": f"{metrics.get('avg_latency', 0):.1f}s",

        })

    if mode_rows:

        mode_df = pd.DataFrame(mode_rows).sort_values(["Mode", "Agent", "Tools"])

        st.dataframe(mode_df, use_container_width=True, hide_index=True)
def render_model_comparison_tab(results: list[dict]):

    """Compare performance across different LLM models."""

    st.subheader("Model Comparison")

    models = get_models(results)

    if len(models) <= 1:

        st.info(

            f"Only one model found ({models[0] if models else 'none'}). "

            "Run evaluations with `--model` to compare different models."

        )

        return

    agg: dict[str, dict] = {}

    for r in results:

        model = _get_run_model(r)

        agent = _get_run_agent_type(r)

        key = f"{model}|{agent}"

        if key not in agg:

            agg[key] = {

                "model": model, "agent": agent,

                "tool_scores": [], "arg_scores": [], "final_scores": [],

                "state_scores": [], "latencies": [],

                "tokens": 0, "cost": 0.0, "cases": 0, "llm_calls": 0,

            }

        d = agg[key]

        a = r.get("aggregate", {})

        tcs = r.get("test_cases", [])

        d["cases"] += len(tcs)

        d["tokens"] += a.get("total_tokens", 0)

        d["cost"] += a.get("total_cost", 0)

        d["llm_calls"] += a.get("total_llm_calls", 0)

        for tc in tcs:

            for mk, bk in [

                ("Tool Correctness", "tool_scores"),

                ("Argument Correctness [Reference]", "arg_scores"),

                ("Final State (Derived)", "final_scores"),

                ("State Match", "state_scores"),

            ]:

                s = tc.get("metrics", {}).get(mk, {}).get("score")

                if s is not None:

                    d[bk].append(s)

            lat = tc.get("latency", {}).get("total")

            if lat is not None:

                d["latencies"].append(lat)

    def safe_avg(lst):

        return round(sum(lst) / len(lst), 4) if lst else None

    table_rows = []

    for d in sorted(agg.values(), key=lambda x: (x["model"], x["agent"])):

        n = d["cases"]

        table_rows.append({

            "Model": d["model"],

            "Agent": d["agent"],

            "Cases": n,

            "Tool Corr.": f"{safe_avg(d['tool_scores']) or 0:.2f}",

            "Arg Corr.": f"{safe_avg(d['arg_scores']) or 0:.2f}",

            "Final State": f"{safe_avg(d['final_scores']) or 0:.2f}" if d["final_scores"] else "-",

            "State Match": f"{safe_avg(d['state_scores']) or 0:.2f}" if d["state_scores"] else "-",

            "Avg Latency": f"{safe_avg(d['latencies']) or 0:.1f}s",

            "Tokens/Case": f"{d['tokens'] // n:,}" if n else "-",

            "Cost/Case": f"${d['cost'] / n:.4f}" if n else "-",

        })

    if table_rows:

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    chart_rows = []

    for d in agg.values():

        chart_rows.append({

            "Model": d["model"],

            "Agent": d["agent"],

            "Tool Correctness": safe_avg(d["tool_scores"]) or 0,

            "Arg Correctness": safe_avg(d["arg_scores"]) or 0,

            "Final State": safe_avg(d["final_scores"]) or 0,

            "Avg Latency (s)": safe_avg(d["latencies"]) or 0,

            "Tokens/Case": d["tokens"] / d["cases"] if d["cases"] else 0,

        })

    if not chart_rows:

        return

    chart_df = pd.DataFrame(chart_rows)

    st.markdown("#### Accuracy by Model")

    score_df = chart_df.melt(

        id_vars=["Model", "Agent"],

        value_vars=["Tool Correctness", "Arg Correctness"],

        var_name="Metric",

        value_name="Score",

    )

    score_chart = (

        alt.Chart(score_df)

        .mark_bar()

        .encode(

            x=alt.X("Agent:N", title=None),

            y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 1]), title="Score"),

            color="Agent:N",

            xOffset="Agent:N",

            column=alt.Column("Model:N", title=None),

            row=alt.Row("Metric:N", title=None),

            tooltip=["Model", "Agent", "Metric", alt.Tooltip("Score:Q", format=".2f")],

        )

        .properties(width=200, height=150)

    )

    st.altair_chart(score_chart)

    st.markdown("#### Latency by Model")

    lat_chart = (

        alt.Chart(chart_df)

        .mark_bar()

        .encode(

            x=alt.X("Agent:N", title=None),

            y=alt.Y("Avg Latency (s):Q", title="Avg Latency (s)"),

            color="Agent:N",

            xOffset="Agent:N",

            column=alt.Column("Model:N", title=None),

            tooltip=["Model", "Agent", alt.Tooltip("Avg Latency (s):Q", format=".1f")],

        )

        .properties(width=200, height=200)

    )

    st.altair_chart(lat_chart)

    st.markdown("#### Token Cost by Model")

    cost_chart = (

        alt.Chart(chart_df)

        .mark_bar()

        .encode(

            x=alt.X("Agent:N", title=None),

            y=alt.Y("Tokens/Case:Q", title="Tokens per Case"),

            color="Agent:N",

            xOffset="Agent:N",

            column=alt.Column("Model:N", title=None),

            tooltip=["Model", "Agent", alt.Tooltip("Tokens/Case:Q", format=",.0f")],

        )

        .properties(width=200, height=200)

    )

    st.altair_chart(cost_chart)

    st.markdown("#### Per-Mode Breakdown")

    mode_rows = []

    for r in results:

        metrics = _compute_run_metrics(r)

        mode_rows.append({

            "Model": _get_run_model(r),

            "Agent": _get_run_agent_type(r),

            "Mode": _get_run_mode(r),

            "Tools": _get_tool_count_label(_get_run_num_tools(r)),

            "Cases": metrics.get("num_cases", 0),

            "Tool Corr.": f"{metrics.get('avg_Tool Correctness', 0):.2f}",

            "Arg Corr.": f"{metrics.get('avg_Argument Correctness [Reference]', 0):.2f}",

            "Avg Latency": f"{metrics.get('avg_latency', 0):.1f}s",

        })

    if mode_rows:

        mode_df = pd.DataFrame(mode_rows).sort_values(["Model", "Mode", "Agent"])

        st.dataframe(mode_df, use_container_width=True, hide_index=True)
def render_export_tab(results: list[dict], domain_key: str):

    if not results:

        st.info("No results to export.")

        return

    labels = [

        f"{format_timestamp(r['timestamp'])} — {_get_run_agent_type(r)} / {_get_run_mode(r)} ({r.get('num_test_cases', '?')} cases)"

        for r in results

    ]

    selected_label = st.selectbox("Select Run", options=labels, key=f"export_{domain_key}")

    selected_run = results[labels.index(selected_label)]

    col_json, col_excel = st.columns(2)

    with col_json:

        json_bytes = json.dumps(selected_run, indent=2, ensure_ascii=False).encode("utf-8")

        st.download_button(

            "Download JSON", data=json_bytes,

            file_name=f"eval_{selected_run.get('_filename', 'result.json')}",

            mime="application/json", key=f"dl_json_{domain_key}",

        )

    with col_excel:

        excel_bytes = to_excel(selected_run)

        ts = selected_run.get("_filename", "result").replace(".json", "")

        st.download_button(

            "Download Excel", data=excel_bytes,

            file_name=f"eval_{ts}.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key=f"dl_excel_{domain_key}",

        )

    st.divider()

    st.subheader("Raw JSON")

    st.json(selected_run)
@st.cache_data(ttl=300)
def to_excel(run_data: dict) -> bytes:

    output = io.BytesIO()

    agg = run_data.get("aggregate", {})

    summary_df = pd.DataFrame({

        "Metric": [

            "Timestamp", "Model", "Mode", "Agent Type", "Test Cases",

            "Total Tokens", "Total Cost", "Total Latency", "Avg Latency", "Total LLM Calls",

        ],

        "Value": [

            run_data.get("timestamp", ""), run_data.get("model", ""),

            run_data.get("mode", ""), run_data.get("agent_type", ""),

            run_data.get("num_test_cases", 0), agg.get("total_tokens", 0),

            f"${agg.get('total_cost', 0):.6f}", f"{agg.get('total_latency', 0):.2f}s",

            f"{agg.get('avg_latency', 0):.2f}s", agg.get("total_llm_calls", 0),

        ],

    })

    tc_rows = []

    for i, tc in enumerate(run_data.get("test_cases", []), 1):

        tokens = tc.get("tokens", {})

        latency = tc.get("latency", {})

        row = {

            "ID": tc.get("id", f"#{i}"),

            "Input": tc.get("input", ""),

            "Tools Called": ", ".join(t["name"] for t in tc.get("tools_called", [])),

            "Tokens": tokens.get("total_tokens", 0),

            "Cost": f"${tokens.get('cost', 0):.6f}",

            "Latency": f"{latency.get('total', 0):.2f}s",

        }

        for metric_name, metric_data in tc.get("metrics", {}).items():

            row[metric_name] = metric_data.get("score", "N/A")

        tc_rows.append(row)

    tc_df = pd.DataFrame(tc_rows)

    tool_rows = []

    for i, tc in enumerate(run_data.get("test_cases", []), 1):

        for t in tc.get("tools_called", []):

            tool_rows.append({

                "Test Case": tc.get("id", f"#{i}"),

                "Tool": t["name"],

                "Parameters": json.dumps(t.get("input_parameters", {}), ensure_ascii=False),

                "Latency": t.get("latency", 0),

            })

    tool_df = pd.DataFrame(tool_rows) if tool_rows else pd.DataFrame()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        tc_df.to_excel(writer, sheet_name="Test Cases", index=False)

        if not tool_df.empty:

            tool_df.to_excel(writer, sheet_name="Tool Calls", index=False)

    return output.getvalue()
st.title("AgentTim - Evaluation Dashboard")
DOMAINS = _discover_domains()
with st.sidebar:

    st.header("Domain")

    if not DOMAINS:

        st.warning("No evaluation results found in `results/`.")

        st.stop()

    selected_domain = st.radio(

        "Select Domain",

        options=list(DOMAINS.keys()),

        format_func=lambda k: DOMAINS[k],

        label_visibility="collapsed",

    )

    st.divider()

    cache_key = f"domain_results_{selected_domain}"

    if cache_key not in st.session_state:

        st.session_state[cache_key] = load_domain_results(selected_domain)

    domain_results = st.session_state[cache_key]

    if st.button("🔄 Refresh", key="refresh_data"):

        st.session_state[cache_key] = load_domain_results(selected_domain)

        domain_results = st.session_state[cache_key]

        st.rerun()

    tc_files = get_test_case_files(selected_domain)

    all_models = get_models(domain_results)

    agent_types = get_agent_types(domain_results)

    if len(all_models) > 1:

        st.divider()

        st.header("Model Filter")

        selected_model = st.selectbox(

            "Filter by Model",

            options=["All Models"] + all_models,

            key="model_filter",

        )

        if selected_model != "All Models":

            domain_results = [

                r for r in domain_results

                if _get_run_model(r) == selected_model

            ]

        st.divider()

    st.metric("Result Runs", len(domain_results))

    st.metric("Models", ", ".join(all_models) if all_models else "-")

    st.metric("Agent Types", ", ".join(agent_types) if agent_types else "-")

    st.metric("Test Case Files", len(tc_files))

    if domain_results:

        total_cases = sum(r.get("num_test_cases", 0) for r in domain_results)

        st.metric("Total Evaluated Cases", total_cases)
domain_label = DOMAINS[selected_domain]
st.header(domain_label)
if not domain_results and not tc_files:

    tc_dir_key = TEST_CASE_DIRS.get(selected_domain, selected_domain)

    st.warning(

        f"No data found for **{domain_label}**.\n\n"

        f"- Results expected in: `results/{selected_domain}/`\n"

        f"- Test cases expected in: `test_cases/{tc_dir_key}/`"

    )

    st.stop()
grouped_results = group_results_by_mode(domain_results)
mode_keys = sorted(grouped_results.keys()) if grouped_results else []
tab_names = ["Overview", "Models", "Tool Count"]
tab_names += [get_mode_label(m) for m in mode_keys]
tab_names += ["Test Cases", "Export"]
tabs = st.tabs(tab_names)
with tabs[0]:

    render_overview_tab(domain_results)
with tabs[1]:

    all_domain_results = st.session_state.get(

        f"domain_results_{selected_domain}", domain_results,

    )

    render_model_comparison_tab(all_domain_results)
with tabs[2]:

    render_tool_count_tab(domain_results)
for i, mode_key in enumerate(mode_keys):

    with tabs[3 + i]:

        render_dimension_tab(domain_results, mode_key)
with tabs[-2]:

    render_test_cases_tab(selected_domain)
with tabs[-1]:

    render_export_tab(domain_results, selected_domain)

