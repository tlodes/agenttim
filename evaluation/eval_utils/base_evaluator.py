"""BaseEvaluator — Unified evaluation framework for all benchmarks.
Handles the main evaluation loop, shared metric computation, result saving,
summary printing, and error tracking. Domain-specific logic is injected
via abstract methods and optional overrides.
Usage:
    class MyEvaluator(BaseEvaluator):
        async def load_test_cases(self) -> list[dict]: ...
        async def setup(self) -> None: ...
        async def run_test_case(self, tc) -> TestCaseResult: ...
        async def teardown(self) -> None: ...

    evaluator = MyEvaluator(agent_type="single", mode="base", settings=settings)
    await evaluator.run_evaluation()
"""
from __future__ import annotations
import asyncio
import json
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from deepeval.test_case import LLMTestCase, ToolCall
from .constants import MODEL_PRICING
from .utils import sanitize_args
from .token_tracker import TokenTracker
from .tool_tracker import ToolTracker
from .multi_agent_tool_tracker import MultiAgentToolTracker
from .subset_tool_correctness import SubsetToolCorrectnessMetric
from .argument_correctness import ReferenceArgumentCorrectnessMetric
from .multi_agent_metrics import (

    MultiAgentTestCase,

    AgentTokenUsage,

    MultiAgentEvaluator,
)
from .test_case_models import TestCaseResult
RESULTS_DIR = Path(__file__).parent.parent / "results"
TEST_CASE_TIMEOUT = 120
class TestCaseTimeoutError(Exception):

    """Raised when a test case exceeds the allowed time limit."""
class BaseEvaluator(ABC):

    """Unified evaluation loop for all benchmarks.

    Subclasses implement domain-specific logic:
    - load_test_cases(): load and filter test cases
    - setup(): create agent, load tools
    - run_test_case(): invoke agent, return TestCaseResult
    - teardown(): cleanup
    """

    def __init__(

        self,

        agent_type: str,

        mode: str,

        settings: Any,

        limit: Optional[int] = None,

        verbose: bool = False,

        num_tools: Optional[int] = None,

    ):

        self.agent_type = agent_type

        self.mode = mode

        self.settings = settings

        self.limit = limit

        self.verbose = verbose

        self.num_tools = num_tools

        self.is_multi_agent: bool = False

        self._eval_model: Any = None

    @abstractmethod

    def get_benchmark_name(self) -> str:

        """Return benchmark identifier (e.g., 'bfcl_multiturn')."""

    @abstractmethod

    def get_agent_label(self) -> str:

        """Return human-readable agent label for printing."""

    @abstractmethod

    async def load_test_cases(self) -> list[dict[str, Any]]:

        """Load test cases for this mode. Return list of raw dicts."""

    @abstractmethod

    async def setup(self) -> None:

        """One-time setup: create agent, load tools, init metrics."""

    @abstractmethod

    async def run_test_case(

        self,

        test_case: dict[str, Any],

        tracker: ToolTracker | MultiAgentToolTracker,

        token_tracker: TokenTracker,

    ) -> TestCaseResult:

        """Run a single test case. Return standardized result."""

    async def teardown(self) -> None:

        """Cleanup after evaluation. Override if needed."""

        pass

    async def compute_domain_metrics(

        self, test_case: dict, result: TestCaseResult,

        shared_metrics: dict[str, dict] | None = None,

    ) -> dict[str, dict]:

        """Return domain-specific metrics for a test case.

        Override to add State Match (BFCL), etc.
        Returns: {"Metric Name": {"score", "threshold", "success", "reason"}}
        """

        return {}

    def get_domain_summary_lines(self, all_results: list[TestCaseResult]) -> list[str]:

        """Return extra summary lines. Override for domain-specific stats."""

        return []

    async def run_evaluation(self) -> None:

        """Main evaluation loop. Runs once in the base; never overridden."""

        test_cases = await self.load_test_cases()

        if self.limit and self.limit < len(test_cases):

            test_cases = test_cases[:self.limit]

        await self.setup()

        self._print_header(test_cases)

        all_results: list[TestCaseResult] = []

        all_errors: list[dict] = []

        for i, tc in enumerate(test_cases, 1):

            tc_id = tc.get("id", f"case_{i}")

            print(f"[{i}/{len(test_cases)}] {tc_id}")

            tracker = MultiAgentToolTracker() if self.is_multi_agent else ToolTracker()

            token_tracker = TokenTracker()

            try:

                result = await asyncio.wait_for(

                    self.run_test_case(tc, tracker, token_tracker),

                    timeout=TEST_CASE_TIMEOUT,

                )

                result.token_tracker = token_tracker

                all_results.append(result)

                self._print_case_status(result, tracker)

            except asyncio.TimeoutError:

                error_msg = f"Test case timed out after {TEST_CASE_TIMEOUT}s"

                print(f"    TIMEOUT: {error_msg}")

                error_result = TestCaseResult(

                    test_id=tc_id,

                    actual_output=f"Error: {error_msg}",

                    latency=float(TEST_CASE_TIMEOUT),

                    error=error_msg,

                    error_type="TestCaseTimeoutError",

                    error_traceback="",

                    token_tracker=token_tracker,

                )

                all_results.append(error_result)

                all_errors.append({

                    "test_case_id": tc_id,

                    "error_type": "TestCaseTimeoutError",

                    "error_message": error_msg,

                    "traceback": "",

                })

            except Exception as e:

                tb = traceback.format_exc()

                print(f"    ERROR: {type(e).__name__}: {e}")

                error_result = TestCaseResult(

                    test_id=tc_id,

                    actual_output=f"Error: {e}",

                    latency=0.0,

                    error=str(e),

                    error_type=type(e).__name__,

                    error_traceback=tb,

                    token_tracker=token_tracker,

                )

                all_results.append(error_result)

                all_errors.append({

                    "test_case_id": tc_id,

                    "error_type": type(e).__name__,

                    "error_message": str(e),

                    "traceback": tb,

                })

        evaluated = await self._compute_all_metrics(test_cases, all_results)

        self._print_summary(test_cases, all_results, evaluated, all_errors)

        self._save_results(test_cases, all_results, evaluated, all_errors)

        await self.teardown()

    async def _compute_all_metrics(

        self, test_cases: list[dict], results: list[TestCaseResult],

    ) -> list[dict[str, dict]]:

        """Compute shared + domain metrics for each test case."""

        all_evaluated = []

        tool_metric = SubsetToolCorrectnessMetric(threshold=1.0, include_reason=True)

        for tc, result in zip(test_cases, results):

            metrics: dict[str, dict] = {}

            if result.is_error:

                all_evaluated.append(metrics)

                continue

            expected_tools = [

                ToolCall(name=t.get("name", ""), input_parameters=t.get("arguments", t.get("input_parameters", {})))

                for t in result.expected_tools

            ]

            tools_called = [

                ToolCall(name=c.get("name", ""), input_parameters=sanitize_args(c.get("args", c.get("input_parameters", {}))))

                for c in result.tools_called

            ]

            tool_test_case = LLMTestCase(

                input=tc.get("input", ""),

                actual_output=result.actual_output,

                expected_tools=expected_tools,

                tools_called=tools_called,

            )

            tool_metric.measure(tool_test_case)

            expected_tool_names = [t.name for t in expected_tools]

            actual_tool_names = [t.name for t in tools_called]

            expected_params = [

                {"name": t.get("name", ""), "input_parameters": t.get("arguments", t.get("input_parameters", {}))}

                for t in result.expected_tools

            ]

            actual_params = [

                {"name": c.get("name", ""), "input_parameters": sanitize_args(c.get("args", c.get("input_parameters", {})))}

                for c in result.tools_called

            ]

            metrics["Tool Correctness"] = {

                "score": tool_metric.score or 0.0,

                "threshold": 1.0,

                "success": tool_metric.is_successful(),

                "reason": tool_metric.reason or "",

                "comparison": {

                    "expected": expected_tool_names,

                    "actual": actual_tool_names,

                },

            }

            if self._eval_model:

                expected_names = {t.name for t in expected_tools}

                actual_names = {t.name for t in tools_called}

                overlap_names = expected_names & actual_names

                overlap_expected = [t for t in expected_tools if t.name in overlap_names]

                overlap_actual = [t for t in tools_called if t.name in overlap_names]

                if overlap_expected:

                    arg_test_case = LLMTestCase(

                        input=tc.get("input", ""),

                        actual_output=result.actual_output,

                        expected_tools=overlap_expected,

                        tools_called=overlap_actual,

                    )

                    arg_metric = ReferenceArgumentCorrectnessMetric(

                        model=self._eval_model, threshold=1.0, include_reason=True,

                    )

                    try:

                        score = await arg_metric.a_measure(arg_test_case)

                        metrics["Argument Correctness [Reference]"] = {

                            "score": score,

                            "threshold": 1.0,

                            "success": arg_metric.is_successful(),

                            "reason": arg_metric.reason or "",

                            "comparison": {

                                "expected": [

                                    {"name": t.name, "input_parameters": t.input_parameters}

                                    for t in overlap_expected

                                ],

                                "actual": [

                                    {"name": t.name, "input_parameters": t.input_parameters}

                                    for t in overlap_actual

                                ],

                            },

                        }

                    except Exception as e:

                        metrics["Argument Correctness [Reference]"] = {

                            "score": 0.0, "threshold": 1.0,

                            "success": False, "reason": f"Judge error: {e}",

                        }

                else:

                    metrics["Argument Correctness [Reference]"] = {

                        "score": 0.0, "threshold": 1.0,

                        "success": False,

                        "reason": "No overlapping tools to evaluate arguments for.",

                    }

            if self.is_multi_agent and result.messages:

                ma_test_case = MultiAgentTestCase(

                    input=tc.get("input", ""),

                    actual_output=result.actual_output,

                    architecture=self.agent_type,

                    tool_calls=[],

                    messages=result.messages,

                    agent_tokens=self._build_agent_tokens(result.token_tracker),

                    expected_tools=[t.get("name", "") for t in result.expected_tools],

                    total_turns=result.total_agent_turns,

                )

                ma_evaluator = MultiAgentEvaluator()

                ma_metrics = ma_evaluator.evaluate(ma_test_case)

                for name, m in ma_metrics.items():

                    metrics[name] = m

            domain_metrics = await self.compute_domain_metrics(tc, result, metrics)

            metrics.update(domain_metrics)

            all_evaluated.append(metrics)

        return all_evaluated

    def _print_header(self, test_cases: list) -> None:

        benchmark = self.get_benchmark_name()

        label = self.get_agent_label()

        print(f"\n{benchmark} Evaluation [{self.mode}]")

        print(f"Agent: {label}")

        if self.num_tools:

            print(f"Tool Limit: {self.num_tools}")

        print(f"Test Cases: {len(test_cases)}")

        print("=" * 70)

    def _print_case_status(

        self, result: TestCaseResult, tracker: ToolTracker | MultiAgentToolTracker,

    ) -> None:

        n_tools = len(result.tools_called)

        latency = result.latency

        turns = len(result.per_turn) if result.per_turn else 1

        print(f"    {turns} turn(s), {n_tools} tool call(s), {latency:.1f}s")

    def _print_summary(

        self,

        test_cases: list,

        results: list[TestCaseResult],

        evaluated: list[dict],

        errors: list[dict],

    ) -> None:

        total = len(test_cases)

        total_latency = sum(r.latency for r in results)

        passed = sum(

            1 for m in evaluated

            if m.get("Tool Correctness", {}).get("success", False)

        )

        print(f"\n{'='*70}")

        print(f"EVALUATION SUMMARY ({self.agent_type})")

        print(f"{'='*70}")

        print(f"Benchmark:    {self.get_benchmark_name()}")

        print(f"Mode:         {self.mode}")

        print(f"Test Cases:   {total}")

        if total:

            print(f"Passed:       {passed}/{total} ({100*passed/total:.1f}%)")

            print(f"Failed:       {total - passed - len(errors)}/{total}")

            print(f"Errors:       {len(errors)}/{total}")

            print(f"Total Latency: {total_latency:.1f}s")

            print(f"Avg Latency:  {total_latency/total:.1f}s")

        metric_names = set()

        for m in evaluated:

            metric_names.update(m.keys())

        if metric_names:

            print(f"\n--- Metric Averages ---")

            for name in sorted(metric_names):

                scores = [

                    m[name]["score"] for m in evaluated

                    if name in m and m[name].get("score") is not None

                ]

                if scores:

                    avg = sum(scores) / len(scores)

                    print(f"  {name}: {avg:.2f}")

        for line in self.get_domain_summary_lines(results):

            print(f"  {line}")

        if errors:

            print(f"\n--- Errors ---")

            for err in errors:

                print(f"  [{err['test_case_id']}] {err['error_type']}: {err['error_message'][:100]}")

    def _save_results(

        self,

        test_cases: list,

        results: list[TestCaseResult],

        evaluated: list[dict],

        errors: list[dict],

    ) -> Path:

        benchmark = self.get_benchmark_name()

        model_name = self.settings.AZURE_OPENAI_MODEL

        tools_dir = f"t{self.num_tools}" if self.num_tools else "all"

        results_dir = RESULTS_DIR / model_name / benchmark / tools_dir

        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        filename = f"{timestamp}_{self.agent_type}_{self.mode}.json"

        pricing = MODEL_PRICING.get(self.settings.AZURE_OPENAI_MODEL, {"input": 0.0, "output": 0.0})

        total = len(test_cases)

        total_prompt = sum(r.token_tracker.prompt_tokens for r in results if r.token_tracker)

        total_completion = sum(r.token_tracker.completion_tokens for r in results if r.token_tracker)

        total_cached = sum(r.token_tracker.cached_tokens for r in results if r.token_tracker)

        total_reasoning = sum(r.token_tracker.reasoning_tokens for r in results if r.token_tracker)

        total_llm_calls = sum(r.token_tracker.llm_calls for r in results if r.token_tracker)

        total_tool_call_llm_calls = sum(r.token_tracker.tool_call_llm_calls for r in results if r.token_tracker)

        total_cost = sum(

            ((r.token_tracker.prompt_tokens / 1_000_000) * pricing["input"]

             + (r.token_tracker.completion_tokens / 1_000_000) * pricing["output"])

            for r in results if r.token_tracker

        )

        total_latency = sum(r.latency for r in results)

        passed = sum(

            1 for m in evaluated

            if m.get("Tool Correctness", {}).get("success", False)

        )

        per_case = []

        for tc, result, metrics in zip(test_cases, results, evaluated):

            tt = result.token_tracker

            case_cost = 0.0

            if tt:

                case_cost = (

                    (tt.prompt_tokens / 1_000_000) * pricing["input"]

                    + (tt.completion_tokens / 1_000_000) * pricing["output"]

                )

            per_case.append({

                "id": result.test_id,

                "dimension": tc.get("dimension", ""),

                "category": tc.get("category", ""),

                "input": tc.get("input", "")[:200],

                "expected_tools": result.expected_tools,

                "tools_called": result.tools_called,

                "metrics": metrics,

                "per_turn": result.per_turn,

                "tokens": {

                    "prompt_tokens": tt.prompt_tokens if tt else 0,

                    "completion_tokens": tt.completion_tokens if tt else 0,

                    "total_tokens": (tt.prompt_tokens + tt.completion_tokens) if tt else 0,

                    "cached_tokens": tt.cached_tokens if tt else 0,

                    "reasoning_tokens": tt.reasoning_tokens if tt else 0,

                    "llm_calls": tt.llm_calls if tt else 0,

                    "tool_call_llm_calls": tt.tool_call_llm_calls if tt else 0,

                    "cost": round(case_cost, 6),

                    "step_breakdown": tt.get_step_breakdown() if tt else {},

                    "per_node": tt.get_per_node_summary() if tt else [],

                },

                "latency": {

                    "total": round(result.latency, 3),

                    "per_turn": [

                        round(t.get("latency", 0), 3) for t in result.per_turn

                    ] if result.per_turn else [],

                },

                "error": {

                    "type": result.error_type,

                    "message": result.error,

                } if result.is_error else None,

            })

        output = {

            "timestamp": datetime.now(timezone.utc).isoformat(),

            "model": self.settings.AZURE_OPENAI_MODEL,

            "benchmark": benchmark,

            "agent_type": self.agent_type,

            "mode": self.mode,

            "num_tools": self.num_tools,

            "num_test_cases": total,

            "errors_summary": {

                "total_errors": len(errors),

                "total_test_cases": total,

                "error_rate": len(errors) / total if total else 0,

            },

            "aggregate": {

                "total_prompt_tokens": total_prompt,

                "total_completion_tokens": total_completion,

                "total_tokens": total_prompt + total_completion,

                "total_cached_tokens": total_cached,

                "total_reasoning_tokens": total_reasoning,

                "total_llm_calls": total_llm_calls,

                "total_tool_call_llm_calls": total_tool_call_llm_calls,

                "total_cost": round(total_cost, 6),

                "total_latency": round(total_latency, 3),

                "avg_latency": round(total_latency / total, 3) if total else 0,

                "pass_rate": passed / total if total else 0,

                "passed": passed,

                "failed": total - passed - len(errors),

                "errors": len(errors),

            },

            "test_cases": per_case,

            "test_case_errors": errors,

        }

        out_path = results_dir / filename

        out_path.write_text(

            json.dumps(output, indent=2, default=str, ensure_ascii=False),

            encoding="utf-8",

        )

        print(f"\nResults saved to: {out_path}")

        if errors:

            errors_path = results_dir / filename.replace(".json", "_errors.json")

            errors_path.write_text(

                json.dumps(errors, indent=2, default=str, ensure_ascii=False),

                encoding="utf-8",

            )

        return out_path

    def _create_tracker(self) -> ToolTracker | MultiAgentToolTracker:

        return MultiAgentToolTracker() if self.is_multi_agent else ToolTracker()

    def _create_token_tracker(self) -> TokenTracker:

        return TokenTracker()

    @staticmethod

    def _build_agent_tokens(tt: Optional[TokenTracker]) -> list[AgentTokenUsage]:

        """Build per-agent token breakdown from TokenTracker's per-node data."""

        if not tt:

            return [AgentTokenUsage(agent_id="unknown")]

        if not tt.per_node:

            return [AgentTokenUsage(

                agent_id="single",

                input_tokens=tt.prompt_tokens,

                output_tokens=tt.completion_tokens,

                cached_tokens=tt.cached_tokens,

                reasoning_tokens=tt.reasoning_tokens,

                llm_calls=tt.llm_calls,

                tool_call_llm_calls=tt.tool_call_llm_calls,

            )]

        return [

            AgentTokenUsage(

                agent_id=name,

                input_tokens=node.prompt_tokens,

                output_tokens=node.completion_tokens,

                cached_tokens=node.cached_tokens,

                reasoning_tokens=node.reasoning_tokens,

                llm_calls=node.llm_calls,

                tool_call_llm_calls=node.tool_call_llm_calls,

            )

            for name, node in sorted(tt.per_node.items())

        ]

