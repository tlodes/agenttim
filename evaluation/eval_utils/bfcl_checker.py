"""Higher-level checker that orchestrates multi-turn BFCL evaluation.
Compares per-turn tool selection (subset matching) and aggregates
pass/fail based on tool correctness and optional state matching.
"""
import logging
from typing import Any, Optional
logger = logging.getLogger(__name__)
def _extract_tool_names(tool_calls: list[dict[str, Any]]) -> set[str]:

    """Extract tool names from a list of tool call dicts."""

    names: set[str] = set()

    for call in tool_calls:

        name = call.get("name", "")

        if name:

            names.add(name)

    return names
class BFCLMultiTurnChecker:

    """Checks multi-turn BFCL evaluation results.

    Per turn: subset matching of expected vs actual tool names.
    Overall: pass if all turns have correct tools.
    """

    def check_test_case(

        self,

        turn_results: list[dict[str, Any]],

        state_match: Optional[dict[str, Any]] = None,

        **kwargs,

    ) -> dict[str, Any]:

        """Check tool correctness across all turns.

        Args:
            turn_results: Per-turn dicts with 'tools_called' and
                          'expected_tool_calls'.
            state_match: Optional state comparison result (from MCP
                         admin_get_state or in-process comparison).

        Returns:
            {"pass": bool, "per_turn": [...], "state_match": {...}}
        """

        per_turn: list[dict[str, Any]] = []

        all_tools_match = True

        for turn_idx, turn in enumerate(turn_results):

            tools_called = turn.get("tools_called", [])

            expected = turn.get("expected_tool_calls", [])

            actual_names = _extract_tool_names(tools_called)

            expected_names = _extract_tool_names(expected)

            tool_match = expected_names.issubset(actual_names)

            if not tool_match:

                missing = expected_names - actual_names

                logger.info(

                    "Turn %d: missing tools %s (actual: %s)",

                    turn_idx, missing, actual_names,

                )

                all_tools_match = False

            per_turn.append({

                "turn": turn_idx,

                "tool_match": tool_match,

                "expected": sorted(expected_names),

                "actual": sorted(actual_names),

            })

        has_state = (

            state_match is not None

            and state_match.get("match") is not None

        )

        state_ok = state_match.get("match", True) if has_state else True

        is_pass = all_tools_match and state_ok

        return {

            "pass": is_pass,

            "all_tools_match": all_tools_match,

            "state_match": state_match or {},

            "per_turn": per_turn,

        }

