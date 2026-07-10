"""Test case type definitions and shared imports.
Defines the expected structure for each test case category.
MCPAgentBench test cases use Pydantic BaseModel (JSON-loaded with validation).
Usage:
    # MCPAgentBench (JSON test cases with validation)
    from test_cases.schemas import MCPAgentBenchTestCase
"""
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
class MCPAgentBenchToolCall(BaseModel):

    """A single expected tool call with name and arguments."""

    name: str = Field(..., min_length=1)

    arguments: dict[str, Any] = Field(default_factory=dict)
class MCPAgentBenchTestCase(BaseModel):

    """Validated schema for MCPAgentBench JSON test cases.

    Covers all dimensions: STurn-1T (single), STurn-MT (parallel/sequential/mixed).
    """

    id: str = Field(..., pattern=r"^MCPAB-")

    source_id: str = Field(..., min_length=1)

    source_category: str = Field(..., min_length=1)

    dimension: Literal["STurn-1T", "STurn-MT"]

    dataset: Literal["MCPAgentBench"] = "MCPAgentBench"

    category: Literal["single", "parallel", "sequential", "mixed"]

    input: str = Field(..., min_length=1)

    expected_tool_calls: list[MCPAgentBenchToolCall] = Field(..., min_length=1)

    expected_execution: list[list[str]] = Field(..., min_length=1)

    @field_validator("expected_execution")

    @classmethod

    def validate_execution_steps_not_empty(

        cls, v: list[list[str]],

    ) -> list[list[str]]:

        for i, step in enumerate(v):

            if len(step) == 0:

                raise ValueError(f"expected_execution step {i} is empty")

        return v

    @model_validator(mode="after")

    def validate_tools_match_execution(self) -> "MCPAgentBenchTestCase":

        tool_names = {tc.name for tc in self.expected_tool_calls}

        execution_names = {name for step in self.expected_execution for name in step}

        if tool_names != execution_names:

            only_in_tools = tool_names - execution_names

            only_in_exec = execution_names - tool_names

            parts = []

            if only_in_tools:

                parts.append(f"in expected_tool_calls but not execution: {only_in_tools}")

            if only_in_exec:

                parts.append(f"in expected_execution but not tool_calls: {only_in_exec}")

            raise ValueError(

                f"Tool name mismatch: {'; '.join(parts)}"

            )

        return self

    def to_dict(self) -> dict[str, Any]:

        """Convert to dict for backward compatibility with existing evaluation code."""

        return self.model_dump()

