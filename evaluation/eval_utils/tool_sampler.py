"""Tool sampling for variable tool count evaluation.
Samples tools for a test case: keeps GT-required tools, fills up with
random distractor tools from the full pool until num_tools is reached.
Works across all benchmarks (BFCL, MCPAgentBench).
Usage:
    all_tools = [...]  # Full tool pool
    sampled = sample_tools(
        all_tools=all_tools,
        expected_tool_names={"cd", "mkdir", "mv"},
        num_tools=20,
    )
"""
from __future__ import annotations
import random
from typing import Any
def sample_tools(

    all_tools: list[Any],

    expected_tool_names: set[str],

    num_tools: int,

    seed: int | None = None,
) -> list[Any]:

    """Sample tools: GT tools + random distractors up to num_tools.

    Args:
        all_tools: Full pool of available tools (BaseTool instances).
        expected_tool_names: Tool names required by the test case (from GT).
        num_tools: Target number of tools. If <= 0 or >= len(all_tools),
                   returns all tools.
        seed: Optional random seed for reproducibility.

    Returns:
        Shuffled list of tools: all GT tools + random distractors.
        If num_tools < len(expected), returns just the GT tools.
    """

    if num_tools <= 0 or num_tools >= len(all_tools):

        tools = list(all_tools)

        if seed is not None:

            random.seed(seed)

        random.shuffle(tools)

        return tools

    gt_tools = [t for t in all_tools if t.name in expected_tool_names]

    non_gt_tools = [t for t in all_tools if t.name not in expected_tool_names]

    if len(gt_tools) >= num_tools:

        if seed is not None:

            random.seed(seed)

        random.shuffle(gt_tools)

        return gt_tools

    num_distractors = num_tools - len(gt_tools)

    if seed is not None:

        random.seed(seed)

    distractors = random.sample(

        non_gt_tools,

        min(num_distractors, len(non_gt_tools)),

    )

    sampled = gt_tools + distractors

    random.shuffle(sampled)

    return sampled
def get_expected_tool_names(test_case: dict) -> set[str]:

    """Extract expected tool names from a test case (any benchmark format).

    Handles:
    - BFCL multi-turn: turns[].expected_tool_calls[].name
    - BFCL/MCPAgentBench single-turn: expected_tool_calls[].name
    """

    names: set[str] = set()

    for turn in test_case.get("turns", []):

        for call in turn.get("expected_tool_calls", []):

            names.add(call["name"])

    for call in test_case.get("expected_tool_calls", []):

        names.add(call["name"])

    return names - {""}

