"""Unified data models for test cases and evaluation results.
Used across benchmarks (BFCL, MCPAgentBench).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
@dataclass
class UnifiedToolCall:

    """Normalized tool call for both expected and actual calls.

    Unifies BFCL's {"name", "arguments"} and MCPAgentBench's {"name", "arguments"}.
    """

    name: str

    arguments: dict[str, Any] = field(default_factory=dict)
@dataclass
class UnifiedTurn:

    """One turn in a multi-turn test case."""

    input: str

    expected_tool_calls: list[UnifiedToolCall] = field(default_factory=list)
@dataclass
class UnifiedTestCase:

    """Normalized test case format for all benchmarks.

    Single-turn: turns is empty, use input + expected_tool_calls directly.
    Multi-turn: turns contains per-turn input and expected calls.
    """

    id: str

    dataset: str

    dimension: str

    category: str

    input: str

    expected_tool_calls: list[UnifiedToolCall] = field(default_factory=list)

    turns: list[UnifiedTurn] = field(default_factory=list)

    expected_output: str = ""

    expected_execution: list[list[str]] = field(default_factory=list)

    description: str = ""

    domain_data: dict[str, Any] = field(default_factory=dict)

    raw: dict[str, Any] = field(default_factory=dict)
@dataclass
class TestCaseResult:

    """Standardized result from running a single test case.

    Returned by BaseEvaluator.run_test_case() and consumed by
    metric computation and result saving.
    """

    test_id: str

    actual_output: str

    latency: float

    tools_called: list[dict[str, Any]] = field(default_factory=list)

    expected_tools: list[dict[str, Any]] = field(default_factory=list)

    messages: list = field(default_factory=list)

    total_agent_turns: int = 1

    per_turn: list[dict[str, Any]] = field(default_factory=list)

    domain_data: dict[str, Any] = field(default_factory=dict)

    token_tracker: Any = None

    error: Optional[str] = None

    error_type: Optional[str] = None

    error_traceback: Optional[str] = None

    @property

    def is_error(self) -> bool:

        return self.error is not None

