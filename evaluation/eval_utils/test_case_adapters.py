"""Adapters to normalize benchmark-specific test cases into UnifiedTestCase.
Each benchmark has its own raw format. These adapters convert to the unified
format so evaluation code can work with a single interface.
"""
from __future__ import annotations
from typing import Any
from .test_case_models import (

    UnifiedTestCase,

    UnifiedToolCall,

    UnifiedTurn,
)
def normalize_bfcl_single_turn(tc: dict[str, Any]) -> UnifiedTestCase:

    """Normalize a BFCL single-turn test case (STurn-1T or STurn-MT)."""

    expected_calls = [

        UnifiedToolCall(name=c["name"], arguments=c.get("arguments", {}))

        for c in tc.get("expected_tool_calls", [])

    ]

    return UnifiedTestCase(

        id=tc["id"],

        dataset="BFCL",

        dimension=tc.get("dimension", "STurn-1T"),

        category=tc.get("source_category", ""),

        input=tc["input"],

        expected_tool_calls=expected_calls,

        expected_execution=tc.get("expected_execution", []),

        domain_data={

            "available_functions": tc.get("available_functions", []),

            "source_id": tc.get("source_id", ""),

        },

        raw=tc,

    )
def normalize_bfcl_multi_turn(tc: dict[str, Any]) -> UnifiedTestCase:

    """Normalize a BFCL multi-turn test case (MTurn-MT)."""

    turns = []

    all_expected = []

    for turn in tc.get("turns", []):

        turn_calls = [

            UnifiedToolCall(name=c["name"], arguments=c.get("arguments", {}))

            for c in turn.get("expected_tool_calls", [])

        ]

        turns.append(UnifiedTurn(input=turn["input"], expected_tool_calls=turn_calls))

        all_expected.extend(turn_calls)

    first_input = turns[0].input if turns else tc.get("input", "")

    return UnifiedTestCase(

        id=tc["id"],

        dataset="BFCL",

        dimension=tc.get("dimension", "MTurn-MT"),

        category=tc.get("category", "base"),

        input=first_input,

        expected_tool_calls=all_expected,

        turns=turns,

        domain_data={

            "available_functions": tc.get("available_functions", []),

            "initial_config": tc.get("initial_config", {}),

            "long_context": tc.get("long_context", False),

            "source_id": tc.get("source_id", ""),

        },

        raw=tc,

    )
def normalize_mcpagentbench(tc: dict[str, Any]) -> UnifiedTestCase:

    """Normalize an MCPAgentBench test case (always single-turn)."""

    expected_calls = [

        UnifiedToolCall(name=c["name"], arguments=c.get("arguments", {}))

        for c in tc.get("expected_tool_calls", [])

    ]

    return UnifiedTestCase(

        id=tc["id"],

        dataset="MCPAgentBench",

        dimension=tc.get("dimension", "STurn-1T"),

        category=tc.get("category", "single"),

        input=tc["input"],

        expected_tool_calls=expected_calls,

        expected_output=tc.get("expected_output", ""),

        expected_execution=tc.get("expected_execution", []),

        domain_data={

            "source_id": tc.get("source_id", ""),

            "source_category": tc.get("source_category", ""),

        },

        raw=tc,

    )

