"""
MCPAgentBench Evaluation (BaseEvaluator).
Evaluates agents against MCPAgentBench benchmark test cases (141 tools, 16 domains).
Supports both Single Agent (all tools in one context) and Multi-Agent (orchestrator
with 16 domain subagents).
Metrics (via BaseEvaluator):
- Tool Correctness: Did the agent call the right tool(s)?
- Argument Correctness: Did the agent pass the right arguments?
- Coordination Token Overhead (post-hoc): Multi-agent token cost vs single-agent baseline
Domain-specific metrics (compute_domain_metrics):
- Execution Efficiency: Did the agent parallelize when possible?
- Final State (Derived): Combines Tool + Argument + Efficiency correctness.
NO GEval: MCPAgentBench tools return deterministic mock data,
so response quality evaluation is not meaningful.
Test Dimensions:
- STurn-1T: Single-Turn, Single Tool (62 cases)
- STurn-MT: Single-Turn, Multi Tool - parallel, sequential, mixed (122 cases)
Prerequisites:
    1. MCPAgentBench MCP server running:
       uvicorn mcpservers.mcpagentbench.main:app --port 9000
    2. VPN connected (for Azure OpenAI)
Run:
    cd agenttim/evaluation
    python evaluationscripts/evaluate_mcpagentbench.py --agent orchestrator_fine --limit 5
    python evaluationscripts/evaluate_mcpagentbench.py --agent orchestrator_coarse --limit 5
    python evaluationscripts/evaluate_mcpagentbench.py --agent orchestrator_fine --mode sturn-1t-daytasks sturn-1t-protasks
    python evaluationscripts/evaluate_mcpagentbench.py --agent orchestrator_coarse --mode sturn-mt-daytasks-parallel --limit 10 --verbose
    python evaluationscripts/evaluate_mcpagentbench.py --agent single --num-tools 20 --limit 5
"""
import argparse
import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
if sys.platform == "win32":

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_eval_dir = Path(__file__).resolve().parent
_python_services_dir = _eval_dir.parent.parent.parent
_bench_orchestrator_dir = (

    _python_services_dir / "agenttim" / "multiagents" / "mcpagentbenchOrchestrator"
)
for _path in [str(_bench_orchestrator_dir), str(_python_services_dir)]:

    if _path not in sys.path:

        sys.path.insert(0, _path)
from deepeval.test_case import LLMTestCase, ToolCall
from agenttim.config.settings import get_settings
from agenttim.services.llm_service import create_llm
from agenttim.services.deepeval_model import LangChainDeepEvalModel
from agenttim.evaluation.eval_utils import (

    is_orchestrator_tool,

    sanitize_args,
)
from agenttim.evaluation.eval_utils.base_evaluator import BaseEvaluator
from agenttim.evaluation.eval_utils.token_tracker import TokenTracker
from agenttim.evaluation.eval_utils.tool_tracker import ToolTracker
from agenttim.evaluation.eval_utils.multi_agent_tool_tracker import MultiAgentToolTracker
from agenttim.evaluation.eval_utils.efficiency import calculate_efficiency
from agenttim.evaluation.eval_utils.test_case_models import TestCaseResult
from agenttim.evaluation.eval_utils.subset_tool_correctness import SubsetToolCorrectnessMetric
from agenttim.evaluation.eval_utils.tool_sampler import sample_tools, get_expected_tool_names
from agenttim.evaluation.test_cases.mcpagentbench_loader import (

    MCPAB_ST_1T_DAYTASKS,

    MCPAB_ST_1T_PROTASKS,

    MCPAB_ST_MT_DAYTASKS_PARALLEL,

    MCPAB_ST_MT_DAYTASKS_SEQUENTIAL,

    MCPAB_ST_MT_DAYTASKS_3TOOLS,

    MCPAB_ST_MT_PROTASKS_PARALLEL,

    MCPAB_ST_MT_PROTASKS_SEQUENTIAL,

    MCPAB_ST_MT_PROTASKS_3TOOLS,
)
from agenttim.singleagent.mcpagentbench.single_agent import DEFAULT_NUM_TOOLS
def _expected_tool_calls_to_deepeval(tc: Dict[str, Any]) -> list[ToolCall]:

    """Convert MCPAgentBench expected_tool_calls to DeepEval ToolCall objects."""

    return [

        ToolCall(

            name=call["name"],

            input_parameters=call.get("arguments", {}),

        )

        for call in tc.get("expected_tool_calls", [])

    ]
def _get_invokable(agent) -> Any:

    """Get the invokable graph/agent object from any architecture."""

    return getattr(agent, "_agent", None) or getattr(agent, "_graph", None)
TEST_CASE_MODES = {

    "sturn-1t-daytasks": MCPAB_ST_1T_DAYTASKS,

    "sturn-1t-protasks": MCPAB_ST_1T_PROTASKS,

    "sturn-mt-daytasks-parallel": MCPAB_ST_MT_DAYTASKS_PARALLEL,

    "sturn-mt-daytasks-sequential": MCPAB_ST_MT_DAYTASKS_SEQUENTIAL,

    "sturn-mt-daytasks-3tools": MCPAB_ST_MT_DAYTASKS_3TOOLS,

    "sturn-mt-protasks-parallel": MCPAB_ST_MT_PROTASKS_PARALLEL,

    "sturn-mt-protasks-sequential": MCPAB_ST_MT_PROTASKS_SEQUENTIAL,

    "sturn-mt-protasks-3tools": MCPAB_ST_MT_PROTASKS_3TOOLS,
}
MULTI_AGENT_TYPES = {

    "orchestrator_fine", "orchestrator_coarse", "swarm", "router",
}
AGENT_LABELS = {

    "single": "Single Agent ReAct (domain sampling)",

    "orchestrator_fine": "Multi-Agent Orchestrator Fine (16 domains)",

    "orchestrator_coarse": "Multi-Agent Orchestrator Coarse (3 broad agents)",

    "swarm": "Multi-Agent Swarm (collaborative discussion)",

    "router": "Router (upfront classification, parallel execution)",
}
async def create_agent(agent_type: str, settings, num_tools: int = DEFAULT_NUM_TOOLS):

    """Create and initialize the appropriate agent."""

    if agent_type == "orchestrator_fine":

        from agenttim.multiagents.mcpagentbenchOrchestrator.orchestrator.orchestrator_agent import MCPBenchOrchestratorAgent

        agent = MCPBenchOrchestratorAgent(settings=settings, granularity="fine")

        await agent.initialize()

        print(f"Orchestrator (fine) ready with {len(agent.get_available_subagents())} subagents.\n")

        return agent

    elif agent_type == "orchestrator_coarse":

        from agenttim.multiagents.mcpagentbenchOrchestrator.orchestrator.orchestrator_agent import MCPBenchOrchestratorAgent

        agent = MCPBenchOrchestratorAgent(settings=settings, granularity="coarse")

        await agent.initialize()

        print(f"Orchestrator (coarse) ready with {len(agent.get_available_subagents())} subagents.\n")

        return agent

    elif agent_type == "swarm":

        from agenttim.multiagents.mcpagentbenchSwarm.swarm.swarm_coordinator import MCPBenchSwarmAgent

        agent = MCPBenchSwarmAgent(settings=settings)

        await agent.initialize()

        print(f"Swarm Agent ready with {len(agent.get_available_subagents())} domain agents.\n")

        return agent

    elif agent_type == "router":

        from agenttim.multiagents.mcpagentbenchRouter.router.router_agent import MCPBenchRouterAgent

        agent = MCPBenchRouterAgent(settings=settings)

        await agent.initialize()

        print(f"Router Agent ready with {len(agent.get_available_subagents())} domain agents.\n")

        return agent

    else:

        from agenttim.singleagent.mcpagentbench.single_agent import MCPBenchSingleAgent

        agent = MCPBenchSingleAgent(settings=settings, num_tools=num_tools)

        await agent.initialize()

        print(f"Single Agent ready (pool: {agent.get_tool_count()}, sampling {num_tools} per case).\n")

        return agent
class MCPAgentBenchEvaluator(BaseEvaluator):

    """Evaluator for MCPAgentBench single-turn benchmarks.

    Uses BaseEvaluator for the main loop, shared metrics (Tool Correctness,
    Argument Correctness, Multi-Agent coordination), result saving, and
    summary printing.

    Adds domain-specific metrics:
    - Execution Efficiency (parallel/sequential correctness)
    - Final State (Derived) combining all component scores
    """

    def __init__(

        self,

        agent_type: str,

        mode: str,

        settings: Any,

        num_tools: int = DEFAULT_NUM_TOOLS,

        limit: int | None = None,

        verbose: bool = False,

    ):

        super().__init__(

            agent_type=agent_type,

            mode=mode,

            settings=settings,

            limit=limit,

            verbose=verbose,

            num_tools=num_tools,

        )

        self.num_tools = num_tools

        self._agent: Any = None

        self._all_multi_agent_tools: Optional[list] = None

    def get_benchmark_name(self) -> str:

        return "mcpagentbench"

    def get_agent_label(self) -> str:

        label = AGENT_LABELS.get(self.agent_type, self.agent_type)

        if self.agent_type == "single":

            label = f"{label} (~{self.num_tools} tools/case)"

        elif self.is_multi_agent and self.num_tools != DEFAULT_NUM_TOOLS:

            label = f"{label} (~{self.num_tools} tools/case)"

        return label

    async def load_test_cases(self) -> list[dict[str, Any]]:

        return list(TEST_CASE_MODES[self.mode])

    async def setup(self) -> None:

        self.is_multi_agent = self.agent_type in MULTI_AGENT_TYPES

        self._agent = await create_agent(

            self.agent_type, self.settings, num_tools=self.num_tools,

        )

        from agenttim.services.llm_service import EVAL_JUDGE_MODEL

        self._eval_model = LangChainDeepEvalModel(

            create_llm(self.settings, model_override=EVAL_JUDGE_MODEL)

        )

        if self.is_multi_agent:

            from agenttim.singleagent.mcpagentbench.combined_mcp_client import CombinedBenchMCPClient

            client = CombinedBenchMCPClient(self.settings)

            self._all_multi_agent_tools = await client.get_tools()

            print(f"Loaded {len(self._all_multi_agent_tools)} tools for multi-agent sampling.\n")

    async def run_test_case(

        self,

        test_case: dict[str, Any],

        tracker: ToolTracker | MultiAgentToolTracker,

        token_tracker: TokenTracker,

    ) -> TestCaseResult:

        """Run a single MCPAgentBench test case (single-turn)."""

        tc_id = test_case.get("id", "unknown")

        if self.is_multi_agent:

            result = await self._run_multi_agent(

                test_case, tracker, token_tracker,

            )

        else:

            result = await self._run_single_agent(

                test_case, tracker, token_tracker,

            )

        mcp_calls = [

            c for c in result["tools_called"]

            if not is_orchestrator_tool(c["name"])

        ]

        expected_tools = [

            {"name": call["name"], "arguments": call.get("arguments", {})}

            for call in test_case.get("expected_tool_calls", [])

        ]

        tools_called = [

            {

                "name": c["name"],

                "args": sanitize_args(c.get("args", {})),

                "output": c.get("output", ""),

                "start_time": c.get("start_time", 0),

                "latency": c.get("latency", 0),

                "agent_id": c.get("agent_id", ""),

            }

            for c in mcp_calls

        ]

        return TestCaseResult(

            test_id=tc_id,

            actual_output=result["actual_output"],

            latency=result["latency"],

            tools_called=tools_called,

            expected_tools=expected_tools,

            messages=result.get("messages", []),

            total_agent_turns=result.get("total_agent_turns", 1),

            domain_data={

                "num_tools_available": result.get("num_tools_available"),

                "domains_loaded": result.get("domains_loaded"),

            },

        )

    async def compute_domain_metrics(

        self, test_case: dict, result: TestCaseResult,

        shared_metrics: dict[str, dict] | None = None,

    ) -> dict[str, dict]:

        """Compute Execution Efficiency and Final State (Derived) metrics.

        Final State follows MCPAgentBench's "ignore parallel" scoring:
        Tool Correctness + Argument Correctness only, no execution order.
        Execution Efficiency is kept as a separate informational metric.
        """

        metrics: dict[str, dict] = {}

        if result.is_error:

            return metrics

        expected_execution = test_case.get("expected_execution")

        has_parallel = expected_execution and any(len(step) > 1 for step in expected_execution)

        if has_parallel and result.tools_called:

            eff = calculate_efficiency(expected_execution, result.tools_called)

            metrics["Execution Efficiency"] = {

                "score": eff["score"],

                "threshold": eff["threshold"],

                "success": eff["success"],

                "reason": eff["reason"],

            }

        shared = shared_metrics or {}

        tool_score = shared.get("Tool Correctness", {}).get("score")

        arg_score = shared.get("Argument Correctness [Reference]", {}).get("score")

        tool_ok = tool_score is not None and tool_score >= 1.0

        arg_ok = arg_score is not None and arg_score >= 1.0

        if tool_ok and arg_ok:

            final_score = 1.0

            reason = "Tool + Argument Correctness passed (execution order ignored)"

        else:

            final_score = 0.0

            failed = []

            if not tool_ok:

                failed.append(f"Tool Correctness: {tool_score}")

            if not arg_ok:

                failed.append(f"Argument Correctness: {arg_score}")

            reason = f"Failed: {', '.join(failed)}"

        metrics["Final State (Derived)"] = {

            "score": final_score,

            "threshold": 1.0,

            "success": final_score >= 1.0,

            "reason": reason,

            "component_scores": {

                "Tool Correctness": tool_score,

                "Argument Correctness": arg_score,

            },

        }

        return metrics

    async def teardown(self) -> None:

        pass

    async def _run_multi_agent(

        self,

        test_case: dict[str, Any],

        tracker: MultiAgentToolTracker,

        token_tracker: TokenTracker,

    ) -> dict[str, Any]:

        """Run a test case with any multi-agent architecture.

        When num_tools differs from default and tool pool is loaded,
        samples tools per test case and reconfigures the agent.
        """

        self._agent.clear_conversation_history()

        num_tools_available = None

        if self._all_multi_agent_tools:

            expected = get_expected_tool_names(test_case)

            case_tools = sample_tools(

                self._all_multi_agent_tools, expected, self.num_tools,

            )

            num_tools_available = len(case_tools)

            if hasattr(self._agent, "setup_for_test_case"):

                self._agent.setup_for_test_case(case_tools, test_case=test_case)

        if self.verbose:

            print(f"    Input: {test_case['input'][:80]}...")

            if num_tools_available is not None:

                print(f"    Tools: {num_tools_available} sampled")

        invokable = _get_invokable(self._agent)

        start_time = time.perf_counter()

        if invokable:

            result = await invokable.ainvoke(

                input={"messages": [{"role": "user", "content": test_case["input"]}]},

                config={"callbacks": [tracker, token_tracker]},

            )

            actual_output = result["messages"][-1].text

        else:

            actual_output = await self._agent.chat(

                test_case["input"], verbose=self.verbose,

                callbacks=[tracker, token_tracker],

            )

        latency = time.perf_counter() - start_time

        tools_called = tracker.get_mcp_calls()

        if self.verbose and invokable:

            print(f"    Response: {actual_output[:100]}...")

            for call in tools_called:

                print(f"    Tool: {call['name']} (agent={call.get('agent_id', '?')}) [{call['latency']:.2f}s]")

        return {

            "actual_output": actual_output,

            "latency": latency,

            "tools_called": tracker.calls.copy(),

            "messages": tracker.messages.copy(),

            "total_agent_turns": tracker.total_turns,

            "num_tools_available": num_tools_available,

        }

    async def _run_single_agent(

        self,

        test_case: dict[str, Any],

        tracker: ToolTracker,

        token_tracker: TokenTracker,

    ) -> dict[str, Any]:

        """Run a test case with the single agent (per-case tool sampling)."""

        result = await self._agent.run_test_case(

            test_case,

            callbacks=[tracker, token_tracker],

            verbose=self.verbose,

        )

        return {

            "actual_output": result["actual_output"],

            "latency": result["latency"],

            "tools_called": tracker.calls.copy(),

            "messages": [],

            "total_agent_turns": 1,

            "num_tools_available": result.get("num_tools_available"),

            "domains_loaded": result.get("domains_loaded"),

        }
def main() -> None:

    parser = argparse.ArgumentParser(

        description="MCPAgentBench evaluation (single-turn only, no GEval)"

    )

    ALL_AGENTS = [

        "single", "orchestrator_fine",

        "orchestrator_coarse", "swarm", "router",

    ]

    parser.add_argument(

        "--agent", "-a", nargs="+",

        choices=ALL_AGENTS + ["all"],

        default=["orchestrator_fine"],

        help="Agent type(s). Use 'all' to run every agent.",

    )

    parser.add_argument(

        "--mode", "-m", nargs="+",

        choices=list(TEST_CASE_MODES.keys()) + ["all"],

        default=["all"],

        help="Test dimension(s). Use 'all' to run every mode (default: all).",

    )

    parser.add_argument(

        "--num-tools", "-n", nargs="+", type=int, default=[DEFAULT_NUM_TOOLS],

        help=(

            f"Target tools per test case (default: {DEFAULT_NUM_TOOLS}). "

            "Pass multiple values to compare: --num-tools 10 20 40 80"

        ),

    )

    parser.add_argument(

        "--limit", "-l", type=int,

        help="Max number of test cases per mode (default: all)",

    )

    parser.add_argument(

        "--verbose", "-v", action="store_true",

        help="Show detailed output per test case",

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

    num_tools_list = args.num_tools

    combos = [(a, m, nt) for a in agents for m in modes for nt in num_tools_list]

    if len(combos) == 1:

        agent_type, mode, nt = combos[0]

        settings = get_settings()

        evaluator = MCPAgentBenchEvaluator(

            agent_type=agent_type,

            mode=mode,

            settings=settings,

            num_tools=nt,

            limit=args.limit,

            verbose=args.verbose,

        )

        asyncio.run(evaluator.run_evaluation())

    else:

        script = str(Path(__file__).resolve())

        for agent, mode, nt in combos:

            cmd = [sys.executable, script, "--agent", agent, "--mode", mode]

            cmd += ["--num-tools", str(nt)]

            if args.limit:

                cmd += ["--limit", str(args.limit)]

            if args.verbose:

                cmd.append("--verbose")

            if args.model:

                cmd += ["--model", args.model]

            print(f"\n{'='*70}")

            print(f">>> Spawning: {agent} / {mode} / {nt} tools")

            print(f"{'='*70}")

            result = subprocess.run(cmd)

            if result.returncode != 0:

                print(f"WARNING: {agent}/{mode}/{nt}tools exited with code {result.returncode}")
if __name__ == "__main__":

    main()

