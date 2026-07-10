"""
Multi-Agent Coordination Metrics for DeepEval
==============================================
Custom metrics for evaluating Multi-Agent System orchestration patterns.
Based on metrics from Google's "Towards a Science of Scaling Agent Systems" paper.
Metrics implemented:
1. CoordinationOverheadMetric - Token overhead vs single-agent baseline
Usage:
    from eval_utils.multi_agent_metrics import (
        MultiAgentTestCase,
        MultiAgentToolCall,
        AgentMessage,
        CoordinationOverheadMetric,
    )
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
@dataclass
class MultiAgentToolCall:

    """Extended ToolCall with agent attribution."""

    name: str

    agent_id: str

    input_parameters: dict[str, Any] = field(default_factory=dict)

    output: Any = None

    success: bool = True

    execution_time_ms: float = 0.0

    timestamp: float = 0.0
@dataclass
class AgentMessage:

    """Inter-agent communication message."""

    sender: str

    recipient: str

    content: str

    message_type: str

    timestamp: float = 0.0

    token_count: int = 0
@dataclass
class AgentTokenUsage:

    """Token usage per agent."""

    agent_id: str

    input_tokens: int = 0

    output_tokens: int = 0

    cached_tokens: int = 0

    reasoning_tokens: int = 0

    llm_calls: int = 0

    tool_call_llm_calls: int = 0

    @property

    def total_tokens(self) -> int:

        return self.input_tokens + self.output_tokens
@dataclass
class MultiAgentTestCase:

    """
    Extended test case for Multi-Agent evaluation.

    Can be converted to LLMTestCase for deepeval compatibility.
    """

    input: str

    actual_output: str

    expected_output: str = ""

    architecture: str = "orchestrator"

    tool_calls: list[MultiAgentToolCall] = field(default_factory=list)

    messages: list[AgentMessage] = field(default_factory=list)

    agent_tokens: list[AgentTokenUsage] = field(default_factory=list)

    expected_tools: list[str] = field(default_factory=list)

    single_agent_tokens: int = 0

    single_agent_turns: int = 0

    total_turns: int = 0

    completion_time_s: float = 0.0

    @property

    def total_tokens(self) -> int:

        return sum(a.total_tokens for a in self.agent_tokens)

    def to_llm_test_case(self) -> LLMTestCase:

        """Convert to standard LLMTestCase for deepeval metrics."""

        from deepeval.test_case import ToolCall

        tools_called = [

            ToolCall(

                name=tc.name,

                input_parameters=tc.input_parameters,

                output=tc.output,

            )

            for tc in self.tool_calls

        ]

        return LLMTestCase(

            input=self.input,

            actual_output=self.actual_output,

            expected_output=self.expected_output,

            tools_called=tools_called,

            expected_tools=self.expected_tools,

        )
class CoordinationOverheadMetric(BaseMetric):

    """
    Measures token overhead compared to single-agent baseline.

    Formula: overhead_pct = (tokens_multi_agent - tokens_single_agent) / tokens_single_agent * 100

    Requires a single-agent baseline for comparison.

    Interpretation (from Google Paper):
    - 0%: Same as single-agent (ideal but rare)
    - < 60%: Low overhead (Independent architecture)
    - 60-300%: Moderate overhead (Centralized/Decentralized)
    - > 300%: High overhead (Hybrid with extensive coordination)

    Lower is better for cost efficiency.
    """

    def __init__(

        self,

        threshold: float = 0.5,

        max_acceptable_overhead_pct: float = 300.0,

        include_reason: bool = True,

    ):

        self.threshold = threshold

        self.max_acceptable_overhead_pct = max_acceptable_overhead_pct

        self.include_reason = include_reason

        self.score: float = 0.0

        self.success: bool = False

        self.reason: str = ""

    def measure(self, test_case: MultiAgentTestCase) -> float:

        """Calculate coordination overhead score."""

        if test_case.single_agent_tokens <= 0:

            self.score = None

            self.success = True

            self.reason = "Skipped: No single-agent baseline provided for comparison."

            return 0.0

        multi_agent_tokens = test_case.total_tokens

        single_agent_tokens = test_case.single_agent_tokens

        overhead_pct = (

            (multi_agent_tokens - single_agent_tokens) / single_agent_tokens * 100

        )

        if overhead_pct <= 0:

            self.score = 1.0

        else:

            self.score = max(0.0, 1.0 - (overhead_pct / self.max_acceptable_overhead_pct))

        self.success = self.score >= self.threshold

        if self.include_reason:

            agent_breakdown = ", ".join(

                f"{a.agent_id}: {a.total_tokens}"

                for a in test_case.agent_tokens

            )

            efficiency_label = (

                "Excellent" if overhead_pct < 60 else

                "Good" if overhead_pct < 150 else

                "Moderate" if overhead_pct < 300 else

                "Poor"

            )

            self.reason = (

                f"Overhead: {overhead_pct:.1f}% "

                f"(MAS: {multi_agent_tokens} tokens vs SAS: {single_agent_tokens} tokens). "

                f"Per-agent: [{agent_breakdown}]. "

                f"{efficiency_label} cost efficiency."

            )

        return self.score

    async def a_measure(self, test_case: MultiAgentTestCase) -> float:

        return self.measure(test_case)

    def is_successful(self) -> bool:

        return self.success

    @property

    def __name__(self) -> str:

        return "Coordination Token Overhead"
class MultiAgentEvaluator:

    """
    Convenience class to run all multi-agent metrics at once.

    Usage:
        evaluator = MultiAgentEvaluator()
        results = evaluator.evaluate(test_case)

        for metric_name, result in results.items():
            print(f"{metric_name}: {result['score']:.2f} - {result['reason']}")
    """

    def __init__(self):

        self.metrics = []

    def evaluate(self, test_case: MultiAgentTestCase) -> dict[str, dict]:

        """Run all metrics and return results."""

        results = {}

        for metric in self.metrics:

            score = metric.measure(test_case)

            results[metric.__name__] = {

                "score": score,

                "success": metric.is_successful(),

                "reason": metric.reason,

                "threshold": metric.threshold,

            }

        return results

    def summary(self, test_case: MultiAgentTestCase) -> str:

        """Return formatted summary of all metrics."""

        results = self.evaluate(test_case)

        lines = [

            f"Multi-Agent Evaluation Summary",

            f"Architecture: {test_case.architecture}",

            f"{'=' * 60}",

        ]

        for name, result in results.items():

            status = "PASS" if result["success"] else "FAIL"

            lines.append(

                f"[{status}] {name}: {result['score']:.2f} "

                f"(threshold: {result['threshold']:.2f})"

            )

            lines.append(f"       {result['reason']}")

        return "\n".join(lines)

