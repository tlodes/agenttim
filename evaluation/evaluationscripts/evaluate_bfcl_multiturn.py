"""
BFCL Multi-Turn Evaluation (Execution-Based).
Evaluates agents against BFCL multi-turn test cases (128 tools, 8 domains).
Tools are served via MCP servers (same architecture as MCPAgentBench).
State management uses admin MCP tools for scenario loading and state export.
Ground truth execution runs in-process against separate class instances
for state comparison after all turns.
Architectures:
    --agent single              Single agent with all 128 tools
    --agent orchestrator_fine   8 domain subagents (1 per API class)
    --agent swarm               Collaborative discussion
Modes:
    --mode base                 multi_turn_base (200 cases)
    --mode long_context         multi_turn_long_context (200 cases)
Prerequisites:
    1. Run convert_bfcl.py to generate test case JSON files
    2. Start BFCL MCP server: cd mcpservers/mcpbfcl && uvicorn main:app --port 9100
    3. VPN connected (for Azure OpenAI)
Run:
    cd agenttim/evaluation
    python evaluationscripts/evaluate_bfcl_multiturn.py --agent single --mode base --limit 5
    python evaluationscripts/evaluate_bfcl_multiturn.py --agent orchestrator_fine --mode base --limit 5 --verbose
    python evaluationscripts/evaluate_bfcl_multiturn.py --agent single --mode base --verbose
"""
import argparse
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
if sys.platform == "win32":

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_eval_dir = Path(__file__).resolve().parent
_python_services_dir = _eval_dir.parent.parent.parent
if str(_python_services_dir) not in sys.path:

    sys.path.insert(0, str(_python_services_dir))
from deepeval.test_case import LLMTestCase, ToolCall
from agenttim.config.settings import get_settings
from agenttim.multiagents.bfclOrchestrator.mcpclients import BFCLMCPClient
from agenttim.bfcl.domain_config import ALL_DOMAINS
from agenttim.bfcl.tool_factory import BFCLToolFactory
from agenttim.evaluation.eval_utils import (

    ToolTracker,

    TokenTracker,

    sanitize_args,

    SubsetToolCorrectnessMetric,
)
from agenttim.evaluation.eval_utils.base_evaluator import BaseEvaluator
from agenttim.evaluation.eval_utils.bfcl_checker import BFCLMultiTurnChecker
from agenttim.evaluation.eval_utils.argument_correctness import ReferenceArgumentCorrectnessMetric
from agenttim.evaluation.eval_utils.multi_agent_tool_tracker import MultiAgentToolTracker
from agenttim.evaluation.eval_utils.multi_agent_metrics import (

    MultiAgentTestCase,

    AgentTokenUsage,

    MultiAgentEvaluator,
)
from agenttim.evaluation.eval_utils.test_case_models import TestCaseResult
from agenttim.services.llm_service import create_llm
from agenttim.services.deepeval_model import LangChainDeepEvalModel
from agenttim.evaluation.test_cases.bfcl_loader import (

    BFCL_MT_MT_BASE,

    BFCL_MT_MT_LONG_CONTEXT,
)
TEST_CASE_MODES: dict[str, list] = {

    "base": BFCL_MT_MT_BASE,

    "long_context": BFCL_MT_MT_LONG_CONTEXT,
}
MULTI_AGENT_TYPES = {

    "orchestrator_fine", "swarm", "router",
}
AGENT_LABELS = {

    "single": "Single Agent (all 128 MCP tools)",

    "orchestrator_fine": "Orchestrator Fine (8 domain agents)",

    "swarm": "Swarm (role-based collaborative decision making)",

    "router": "Router (upfront classification, parallel execution)",
}
async def load_mcp_tools(settings) -> list:

    """Load all 128 tools from BFCL MCP server (excluding admin tools)."""

    client = BFCLMCPClient(settings=settings, domains=ALL_DOMAINS)

    tools = await client.get_tools()

    print(f"Loaded {len(tools)} tools from BFCL MCP server")

    return tools
async def reset_mcp_state(

    settings, initial_config: dict, long_context: bool = False,
) -> None:

    """Reset state on all BFCL MCP servers via per-domain clients.

    Creates a separate MCP client per domain so each admin_load_scenario
    call targets the correct server (avoids name collision when all 8
    domains expose identically-named admin tools).
    """

    from agenttim.bfcl.domain_config import CLASS_TO_DOMAIN

    import json as _json

    for class_name, config in initial_config.items():

        domain = CLASS_TO_DOMAIN.get(class_name)

        if not domain:

            continue

        client = BFCLMCPClient(settings=settings, domain=domain)

        all_tools = await client.get_all_tools()

        for tool in all_tools:

            if tool.name == "admin_load_scenario":

                await tool.ainvoke({

                    "config_json": _json.dumps(config, default=str),

                    "long_context": long_context,

                })

                break
async def read_mcp_state(settings) -> dict:

    """Read state from all BFCL MCP servers via per-domain clients."""

    import json as _json

    states = {}

    for domain in ALL_DOMAINS:

        client = BFCLMCPClient(settings=settings, domain=domain)

        all_tools = await client.get_all_tools()

        for tool in all_tools:

            if tool.name == "admin_get_state":

                result = await tool.ainvoke({})

                if isinstance(result, str):

                    states[domain] = _json.loads(result)

                else:

                    states[domain] = result

                break

    return states
async def create_agent(agent_type: str, settings):

    """Create and initialize the appropriate agent."""

    if agent_type == "single":

        from agenttim.singleagent.bfcl.single_agent import BFCLSingleAgent

        agent = BFCLSingleAgent(settings=settings)

        await agent.initialize()

        print("Single Agent initialized.\n")

        return agent

    if agent_type == "orchestrator_fine":

        from agenttim.multiagents.bfclOrchestrator.orchestrator.orchestrator_agent import BFCLOrchestratorAgent

        agent = BFCLOrchestratorAgent(settings=settings, granularity="fine")

        await agent.initialize()

        subs = agent.get_available_subagents()

        print(f"Orchestrator (fine) ready with {len(subs)} subagents.\n")

        return agent

    if agent_type == "swarm":

        from agenttim.multiagents.bfclSwarm.swarm.swarm_coordinator import BFCLSwarmAgent

        agent = BFCLSwarmAgent(settings=settings)

        await agent.initialize()

        print(f"Swarm Agent initialized.\n")

        return agent

    if agent_type == "router":

        from agenttim.multiagents.bfclRouter.router.router_agent import BFCLRouterAgent

        agent = BFCLRouterAgent(settings=settings)

        await agent.initialize()

        subs = agent.get_available_subagents()

        print(f"Router Agent ready with {len(subs)} domain agents.\n")

        return agent

    raise ValueError(f"Unknown agent type: {agent_type}")
def _replay_calls_on_instances(

    instances: dict, calls: list[dict], label: str = "",
) -> list[dict]:

    """Replay tool calls against in-process class instances.

    Each call is {"name": "cd", "arguments": {"folder": "document"}}.
    Returns list of replay results for debugging.
    """

    import logging

    _logger = logging.getLogger("bfcl_replay")

    from agenttim.bfcl.domain_config import CLASS_TO_DOMAIN, DOMAIN_TOOLS

    domain_to_class = {d: c for c, d in CLASS_TO_DOMAIN.items()}

    tool_to_class: dict[str, str] = {}

    for domain, tools in DOMAIN_TOOLS.items():

        cls = domain_to_class.get(domain)

        if cls:

            for t in tools:

                tool_to_class[t] = cls

    results = []

    for call in calls:

        name = call.get("name", "")

        args = call.get("arguments", {})

        cls_name = tool_to_class.get(name)

        if not cls_name or cls_name not in instances:

            results.append({"tool": name, "status": "skipped", "reason": "no instance"})

            continue

        instance = instances[cls_name]

        method = getattr(instance, name, None)

        if method is None:

            results.append({"tool": name, "status": "skipped", "reason": "no method"})

            continue

        try:

            result = method(**args)

            results.append({"tool": name, "status": "ok", "result": str(result)[:200]})

        except Exception as e:

            _logger.debug("[%s] Replay %s(%s) failed: %s", label, name, args, e)

            results.append({"tool": name, "status": "error", "error": str(e)[:200]})

    return results
def _compare_instances(

    model_instances: dict, gt_instances: dict,
) -> dict:

    """Compare public attributes of model vs GT class instances.

    Uses JSON serialization for comparison to handle type differences
    (e.g., int keys vs str keys) and custom __eq__ on BFCL objects.
    """

    import json as _json

    per_class: dict[str, dict] = {}

    all_match = True

    for cls_name in gt_instances:

        if cls_name not in model_instances:

            per_class[cls_name] = {"match": False, "diffs": ["missing from model"]}

            all_match = False

            continue

        m_inst = model_instances[cls_name]

        g_inst = gt_instances[cls_name]

        diffs = []

        for attr in vars(g_inst):

            if attr.startswith("_"):

                continue

            g_val = getattr(g_inst, attr)

            m_val = getattr(m_inst, attr, None)

            try:

                g_str = _json.dumps(g_val, sort_keys=True, default=str)

                m_str = _json.dumps(m_val, sort_keys=True, default=str)

                is_equal = g_str == m_str

            except (TypeError, ValueError):

                is_equal = str(g_val) == str(m_val)

            if not is_equal:

                diffs.append({

                    "attribute": attr,

                    "expected": str(g_val),

                    "actual": str(m_val),

                })

        match = len(diffs) == 0

        if not match:

            all_match = False

        per_class[cls_name] = {"match": match, "diffs": diffs}

    return {"match": all_match, "per_class": per_class}
def _build_state_reason(state_match: dict) -> str:

    """Build human-readable reason for state match result."""

    if state_match.get("match") is None:

        return "State comparison not performed"

    if state_match.get("match"):

        return "Final state matches ground truth"

    mismatched = [

        cls for cls, info in state_match.get("per_class", {}).items()

        if not info.get("match")

    ]

    return f"State mismatch in: {mismatched}"
def _compute_argument_score(

    result_turns: list, tc_turns: list,
) -> tuple[float, list]:

    """Compute argument correctness score across turns.

    Returns:
        (score, per_turn_details) where details show each argument comparison.
    """

    total_args = 0

    correct_args = 0

    per_turn_details = []

    for turn_idx, (result_turn, tc_turn) in enumerate(zip(result_turns, tc_turns)):

        expected_calls = tc_turn.get("expected_tool_calls", [])

        actual_calls = result_turn.get("tools_called", [])

        actual_by_name: dict[str, list[dict]] = {}

        for c in actual_calls:

            name = c.get("name", "")

            if name:

                actual_by_name.setdefault(name, []).append(c.get("args", {}))

        turn_details = []

        for exp in expected_calls:

            exp_name = exp.get("name", "")

            exp_args = exp.get("arguments", {})

            all_actual = actual_by_name.get(exp_name, [{}])

            best_match = {}

            best_count = -1

            for candidate in all_actual:

                match_count = sum(

                    1 for k, v in exp_args.items()

                    if str(candidate.get(k)) == str(v)

                )

                if match_count > best_count:

                    best_count = match_count

                    best_match = candidate

            for key, exp_val in exp_args.items():

                total_args += 1

                actual_val = best_match.get(key)

                is_match = str(actual_val) == str(exp_val)

                if is_match:

                    correct_args += 1

                else:

                    turn_details.append({

                        "tool": exp_name,

                        "param": key,

                        "expected": str(exp_val),

                        "actual": str(actual_val),

                        "match": False,

                    })

        if turn_details:

            per_turn_details.append({

                "turn": turn_idx,

                "mismatches": turn_details,

            })

    score = correct_args / total_args if total_args > 0 else 1.0

    return score, per_turn_details
class BFCLEvaluator(BaseEvaluator):

    """BFCL multi-turn evaluation using BaseEvaluator framework.

    Runs multi-turn test cases with MCP-based tools, replays ground truth
    on in-process instances, and compares final state.
    """

    def __init__(

        self,

        agent_type: str,

        mode: str,

        settings: Any,

        limit: int | None = None,

        verbose: bool = False,

        num_tools: int | None = None,

    ):

        super().__init__(

            agent_type=agent_type,

            mode=mode,

            settings=settings,

            limit=limit,

            verbose=verbose,

            num_tools=num_tools,

        )

        self.is_multi_agent = agent_type in MULTI_AGENT_TYPES

        self._agent = None

        self._mcp_tools: list = []

        self._gt_factory: BFCLToolFactory | None = None

        self._checker: BFCLMultiTurnChecker | None = None

        self._arg_metric: ReferenceArgumentCorrectnessMetric | None = None

    def get_benchmark_name(self) -> str:

        return "bfcl_multiturn"

    def get_agent_label(self) -> str:

        return AGENT_LABELS.get(self.agent_type, self.agent_type)

    async def load_test_cases(self) -> list[dict[str, Any]]:

        return list(TEST_CASE_MODES[self.mode])

    async def setup(self) -> None:

        self._agent = await create_agent(self.agent_type, self.settings)

        self._mcp_tools = await load_mcp_tools(self.settings)

        self._gt_factory = BFCLToolFactory()

        self._checker = BFCLMultiTurnChecker()

        from agenttim.services.llm_service import EVAL_JUDGE_MODEL

        eval_llm = create_llm(self.settings, model_override=EVAL_JUDGE_MODEL)

        eval_model = LangChainDeepEvalModel(eval_llm)

        self._arg_metric = ReferenceArgumentCorrectnessMetric(

            model=eval_model, threshold=1.0, include_reason=True,

        )

        self._eval_model = eval_model

    async def run_test_case(

        self,

        test_case: dict[str, Any],

        tracker: ToolTracker | MultiAgentToolTracker,

        token_tracker: TokenTracker,

    ) -> TestCaseResult:

        """Run a full multi-turn BFCL test case.

        Handles MCP state reset, per-turn agent invocation, GT replay,
        and state comparison. Returns a TestCaseResult with per-turn data.
        """

        initial_config = test_case.get("initial_config", {})

        long_context = test_case.get("long_context", False)

        await reset_mcp_state(self.settings, initial_config, long_context=long_context)

        gt_instances = self._gt_factory.create_instances(test_case, all_classes=False)

        model_replay_instances = self._gt_factory.create_instances(test_case, all_classes=False)

        if self.num_tools:

            from agenttim.evaluation.eval_utils.tool_sampler import (

                sample_tools, get_expected_tool_names,

            )

            expected = get_expected_tool_names(test_case)

            case_tools = sample_tools(self._mcp_tools, expected, self.num_tools)

        else:

            case_tools = self._mcp_tools

        self._agent.setup_for_test_case(case_tools)

        case_tracker = tracker

        turns = test_case.get("turns", [])

        turn_results = []

        all_tool_calls = []

        calls_before = 0

        for turn_idx, turn in enumerate(turns):

            turn_start = time.perf_counter()

            callbacks = [case_tracker, token_tracker]

            try:

                response = await self._agent.run_turn(

                    turn["input"], callbacks=callbacks, verbose=False,

                )

            except Exception as e:

                response = f"Error: {type(e).__name__}: {e}"

            turn_latency = time.perf_counter() - turn_start

            if self.is_multi_agent:

                all_calls_so_far = case_tracker.get_mcp_calls()

            else:

                all_calls_so_far = case_tracker.calls.copy()

            turn_calls = all_calls_so_far[calls_before:]

            calls_before = len(all_calls_so_far)

            expected = turn.get("expected_tool_calls", [])

            gt_replay = _replay_calls_on_instances(gt_instances, expected, label="GT")

            model_calls_for_replay = [

                {"name": c.get("name"), "arguments": c.get("args", {})}

                for c in turn_calls

            ]

            model_replay = _replay_calls_on_instances(

                model_replay_instances, model_calls_for_replay, label="MODEL",

            )

            turn_results.append({

                "turn_index": turn_idx,

                "input": turn["input"],

                "response": response,

                "tools_called": turn_calls,

                "expected_tool_calls": expected,

                "latency": turn_latency,

                "gt_replay": gt_replay,

                "model_replay": model_replay,

            })

            all_tool_calls.extend(turn_calls)

        total_latency = sum(t["latency"] for t in turn_results)

        state_match = _compare_instances(model_replay_instances, gt_instances)

        check = self._checker.check_test_case(

            turn_results=turn_results,

            state_match=state_match,

        )

        arg_judge_result = await self._run_arg_judge(test_case, turn_results, all_tool_calls)

        expected_tools_flat = []

        for t in test_case.get("turns", []):

            for call in t.get("expected_tool_calls", []):

                expected_tools_flat.append({

                    "name": call["name"],

                    "input_parameters": call.get("arguments", {}),

                })

        tools_called_flat = [

            {

                "name": c.get("name", ""),

                "input_parameters": sanitize_args(c.get("args", {})),

                "start_time": c.get("start_time", 0),

                "latency": c.get("latency", 0),

            }

            for c in all_tool_calls

        ]

        per_turn_checks = check.get("per_turn", [])

        return TestCaseResult(

            test_id=test_case["id"],

            actual_output=turn_results[-1]["response"] if turn_results else "",

            latency=total_latency,

            tools_called=tools_called_flat,

            expected_tools=expected_tools_flat,

            messages=case_tracker.messages.copy() if self.is_multi_agent else [],

            total_agent_turns=case_tracker.total_turns if self.is_multi_agent else len(turns),

            per_turn=per_turn_checks,

            domain_data={

                "state_match": state_match,

                "checker_result": check,

                "arg_judge": arg_judge_result,

                "turn_results": turn_results,

                "num_tools_available": len(case_tools),

            },

        )

    async def compute_domain_metrics(

        self, test_case: dict, result: TestCaseResult,

        shared_metrics: dict[str, dict] | None = None,

    ) -> dict[str, dict]:

        """Compute BFCL-specific metrics: State Match + per-turn tool correctness."""

        metrics: dict[str, dict] = {}

        state_match = result.domain_data.get("state_match", {})

        arg_judge = result.domain_data.get("arg_judge", {})

        turn_results = result.domain_data.get("turn_results", [])

        metrics["State Match"] = {

            "score": 1.0 if state_match.get("match") else 0.0,

            "threshold": 1.0,

            "success": state_match.get("match", False),

            "reason": _build_state_reason(state_match),

            "comparison": state_match.get("per_class", {}),

        }

        per_turn_tool_results = self._compute_per_turn_tool_correctness(

            test_case, turn_results,

        )

        turn_scores = [t["score"] for t in per_turn_tool_results]

        tool_correctness_score = sum(turn_scores) / len(turn_scores) if turn_scores else 1.0

        tool_correctness_success = all(t["success"] for t in per_turn_tool_results)

        total_cross_turn_redundant = sum(

            len(t["cross_turn_redundant"]) for t in per_turn_tool_results

        )

        tool_correctness_reason = (

            f"Per-turn avg: {tool_correctness_score:.2f} "

            f"({len(turn_scores)} turns). "

            f"Cross-turn redundant calls: {total_cross_turn_redundant}."

        )

        metrics["Tool Correctness"] = {

            "score": tool_correctness_score,

            "threshold": 1.0,

            "success": tool_correctness_success,

            "reason": tool_correctness_reason,

            "cross_turn_redundant_count": total_cross_turn_redundant,

            "per_turn": per_turn_tool_results,

        }

        arg_score_llm = arg_judge.get("score")

        arg_fallback, arg_details = _compute_argument_score(

            turn_results, test_case.get("turns", []),

        )

        metrics["Argument Correctness [Reference]"] = {

            "score": arg_score_llm if arg_score_llm is not None else arg_fallback,

            "threshold": 1.0,

            "success": (arg_score_llm or 0) >= 1.0 if arg_score_llm is not None else arg_fallback >= 1.0,

            "reason": arg_judge.get("reason", f"String-based fallback: {arg_fallback:.2f}"),

            "evaluation_model": "LLM-as-Judge" if arg_score_llm is not None else None,

            "per_turn_mismatches": arg_details,

        }

        if self.is_multi_agent and result.messages:

            turns = test_case.get("turns", [])

            ma_test_case = MultiAgentTestCase(

                input=" | ".join(t["input"][:80] for t in turns),

                actual_output=result.actual_output,

                architecture=self.agent_type,

                tool_calls=[],

                messages=result.messages,

                agent_tokens=self._build_agent_tokens(result.token_tracker),

                expected_tools=[

                    c["name"] for t in turns

                    for c in t.get("expected_tool_calls", [])

                ],

                total_turns=result.total_agent_turns,

            )

            ma_evaluator = MultiAgentEvaluator()

            ma_metrics = ma_evaluator.evaluate(ma_test_case)

            for name, m in ma_metrics.items():

                if name != "Message Density":

                    metrics[name] = m

        return metrics

    def get_domain_summary_lines(self, all_results: list[TestCaseResult]) -> list[str]:

        """Return BFCL-specific summary lines."""

        lines = []

        state_matches = sum(

            1 for r in all_results

            if r.domain_data.get("state_match", {}).get("match", False)

        )

        total = len(all_results)

        if total:

            lines.append(f"State Match: {state_matches}/{total} ({100*state_matches/total:.1f}%)")

        return lines

    async def teardown(self) -> None:

        pass

    def _compute_per_turn_tool_correctness(

        self, test_case: dict, turn_results: list[dict],

    ) -> list[dict]:

        """Compute per-turn tool correctness with cross-turn redundancy detection."""

        per_turn_tool_results = []

        seen_call_signatures: set[str] = set()

        for turn_idx, (tc_turn, result_turn) in enumerate(

            zip(test_case.get("turns", []), turn_results)

        ):

            turn_expected = [

                ToolCall(

                    name=call["name"],

                    input_parameters=call.get("arguments", {}),

                )

                for call in tc_turn.get("expected_tool_calls", [])

            ]

            turn_actual = [

                ToolCall(

                    name=c.get("name", ""),

                    input_parameters=sanitize_args(c.get("args", {})),

                )

                for c in result_turn.get("tools_called", [])

            ]

            expected_names_this_turn = {t.name for t in turn_expected}

            cross_turn_redundant = []

            for tc_call in turn_actual:

                sig = f"{tc_call.name}:{sorted(tc_call.input_parameters.items())}"

                if (

                    sig in seen_call_signatures

                    and tc_call.name not in expected_names_this_turn

                ):

                    cross_turn_redundant.append(tc_call.name)

            for tc_call in turn_actual:

                sig = f"{tc_call.name}:{sorted(tc_call.input_parameters.items())}"

                seen_call_signatures.add(sig)

            turn_metric = SubsetToolCorrectnessMetric(threshold=1.0, include_reason=True)

            turn_test_case = LLMTestCase(

                input=tc_turn.get("input", "")[:200],

                actual_output=result_turn.get("response", ""),

                expected_tools=turn_expected,

                tools_called=turn_actual,

            )

            turn_metric.measure(turn_test_case)

            per_turn_tool_results.append({

                "turn": turn_idx,

                "score": turn_metric.score or 0.0,

                "success": turn_metric.is_successful(),

                "reason": turn_metric.reason or "",

                "expected": [t.name for t in turn_expected],

                "actual": [t.name for t in turn_actual],

                "missing": sorted(turn_metric.get_missing_tools()),

                "extra": sorted(turn_metric.get_extra_tools()),

                "duplicate_count": turn_metric.get_duplicate_count(),

                "cross_turn_redundant": cross_turn_redundant,

            })

        return per_turn_tool_results

    async def _run_arg_judge(

        self, tc: dict, turn_results: list[dict], all_tool_calls: list[dict],

    ) -> dict:

        """Run LLM-as-judge argument correctness on overlapping tools only.

        Only evaluates arguments for tools that appear in BOTH expected and actual.
        Missing/extra tools are handled by Tool Correctness, not here.
        """

        expected_tools = []

        for turn in tc.get("turns", []):

            for call in turn.get("expected_tool_calls", []):

                expected_tools.append(ToolCall(

                    name=call["name"],

                    input_parameters=call.get("arguments", {}),

                ))

        tools_called = []

        for c in all_tool_calls:

            tools_called.append(ToolCall(

                name=c.get("name", ""),

                input_parameters=c.get("args", {}),

            ))

        expected_names = {t.name for t in expected_tools}

        actual_names = {t.name for t in tools_called}

        overlap = expected_names & actual_names

        if not overlap:

            return {"score": 0.0, "success": False, "reason": "No overlapping tools to evaluate."}

        overlap_expected = [t for t in expected_tools if t.name in overlap]

        overlap_actual = [t for t in tools_called if t.name in overlap]

        judge_case = LLMTestCase(

            input=tc.get("turns", [{}])[0].get("input", ""),

            actual_output=turn_results[-1].get("response", "") if turn_results else "",

            expected_tools=overlap_expected,

            tools_called=overlap_actual,

        )

        try:

            score = await self._arg_metric.a_measure(judge_case)

            return {

                "score": score,

                "success": self._arg_metric.is_successful(),

                "reason": self._arg_metric.reason or "",

            }

        except Exception as e:

            return {"score": 0.0, "success": False, "reason": f"Judge error: {e}"}
def main() -> None:

    parser = argparse.ArgumentParser(

        description="BFCL Multi-Turn evaluation (execution-based, MCP tools)"

    )

    ALL_AGENTS = [

        "single", "orchestrator_fine",

        "swarm", "router",

    ]

    parser.add_argument(

        "--agent", "-a", nargs="+",

        choices=ALL_AGENTS + ["all"],

        default=["single"],

        help="Agent architecture(s). Use 'all' to run every agent.",

    )

    parser.add_argument(

        "--mode", "-m", nargs="+",

        choices=list(TEST_CASE_MODES.keys()) + ["all"],

        default=["base"],

        help="Test mode(s). Use 'all' to run every mode.",

    )

    parser.add_argument(

        "--limit", "-l", type=int,

        help="Max test cases per mode (default: all)",

    )

    parser.add_argument(

        "--num-tools", "-n", nargs="+", type=int,

        help="Tool counts per test case. Pass multiple to compare: --num-tools 10 20 40 80",

    )

    parser.add_argument(

        "--verbose", "-v", action="store_true",

        help="Show detailed output per turn",

    )

    parser.add_argument(

        "--model", type=str, default=None,

        help="Override LLM model (e.g. deepseek/deepseek-v4-pro, gpt-5.4-mini)",

    )

    args = parser.parse_args()

    if args.model:

        os.environ["AZURE_OPENAI_MODEL"] = args.model

    agents = ALL_AGENTS if "all" in args.agent else args.agent

    modes = list(TEST_CASE_MODES.keys()) if "all" in args.mode else args.mode

    num_tools_list = args.num_tools or [None]

    combos = [(a, m, nt) for a in agents for m in modes for nt in num_tools_list]

    if len(combos) == 1:

        settings = get_settings()

        evaluator = BFCLEvaluator(

            agent_type=combos[0][0],

            mode=combos[0][1],

            settings=settings,

            limit=args.limit,

            verbose=args.verbose,

            num_tools=combos[0][2],

        )

        asyncio.run(evaluator.run_evaluation())

    else:

        script = str(Path(__file__).resolve())

        for agent, mode, nt in combos:

            cmd = [sys.executable, script, "--agent", agent, "--mode", mode]

            if args.limit:

                cmd += ["--limit", str(args.limit)]

            if nt is not None:

                cmd += ["--num-tools", str(nt)]

            if args.verbose:

                cmd.append("--verbose")

            if args.model:

                cmd += ["--model", args.model]

            tools_label = f" / t{nt}" if nt else ""

            print(f"\n{'='*70}")

            print(f">>> Spawning: {agent} / {mode}{tools_label}")

            print(f"{'='*70}")

            result = subprocess.run(cmd)

            if result.returncode != 0:

                print(f"WARNING: {agent}/{mode} exited with code {result.returncode}")
if __name__ == "__main__":

    main()

