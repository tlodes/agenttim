"""Tool Correctness metric for agent evaluation.
Measures whether the agent called the correct tools. Penalizes:
- Missing tools: Expected tools that were not called
- Extra tools: Tools called that were not expected
- Duplicate calls: Same tool called multiple times when only one call expected
Scoring:
    Score = |expected ∩ called_unique| / max(|expected|, |total_calls|)

    - 1.0 = All expected tools called exactly once, no extras
    - 0.5 = Half correct (e.g., 1 expected, 2 called including duplicate)
    - 0.0 = No expected tools were called
Examples:
    - Expected: [A], Called: [A] → 1/1 = 1.0
    - Expected: [A], Called: [A, A] → 1/2 = 0.5 (duplicate penalized)
    - Expected: [A, B], Called: [A] → 1/2 = 0.5 (missing B)
    - Expected: [A], Called: [A, B] → 1/2 = 0.5 (extra B)
    - Expected: [A], Called: [A, A, A] → 1/3 = 0.33 (2 duplicates)
"""
from dataclasses import dataclass, field
from typing import List, Optional, Set
from deepeval.metrics.base_metric import BaseMetric
from deepeval.test_case import LLMTestCase, ToolCall
@dataclass
class SubsetMatchResult:

    """Result of tool correctness matching."""

    expected_tools: Set[str]

    called_tools: Set[str]

    found_tools: Set[str]

    missing_tools: Set[str]

    extra_tools: Set[str]

    duplicate_count: int

    total_calls: int

    score: float

    reason: str
class SubsetToolCorrectnessMetric(BaseMetric):

    """Tool correctness metric that penalizes missing, extra, and duplicate calls.

    Scoring formula:
        Score = |expected ∩ called_unique| / max(|expected|, |total_calls|)

    This means:
    - Missing tools reduce the numerator
    - Extra tools (different tools) increase the denominator
    - Duplicate calls (same tool called multiple times) increase the denominator

    Example:
        ```python
        metric = SubsetToolCorrectnessMetric(threshold=1.0)

        # Expected: [A], Called: [A] → 1/1 = 1.0 ✓
        # Expected: [A], Called: [A, A] → 1/2 = 0.5 (duplicate penalized)
        # Expected: [A, B], Called: [A, B, B] → 2/3 = 0.67 (duplicate B)
        ```

    Args:
        threshold: Minimum score to pass (default: 1.0 = exact match required)
        include_reason: Include detailed reason in output (default: True)
        check_arguments: Also check argument correctness for matching tools (default: False)
        strict_mode: Raise exceptions on errors (default: False)
    """

    def __init__(

        self,

        threshold: float = 1.0,

        include_reason: bool = True,

        check_arguments: bool = False,

        strict_mode: bool = False,

        verbose_mode: bool = False,

    ):

        self.threshold = threshold

        self.include_reason = include_reason

        self.check_arguments = check_arguments

        self.strict_mode = strict_mode

        self.verbose_mode = verbose_mode

        self.score: Optional[float] = None

        self.reason: Optional[str] = None

        self.success: Optional[bool] = None

        self.match_result: Optional[SubsetMatchResult] = None

        self.error: Optional[str] = None

    @property

    def __name__(self) -> str:

        return "Tool Correctness"

    def _extract_tool_names(self, tools: List[ToolCall]) -> Set[str]:

        """Extract unique tool names from a list of ToolCalls."""

        return {t.name for t in tools if t.name}

    def _compute_subset_match(

        self,

        expected_tools: List[ToolCall],

        tools_called: List[ToolCall],

    ) -> SubsetMatchResult:

        """Compute tool correctness score.

        Uses total call count (not unique) to penalize duplicate calls.
        """

        expected_names = self._extract_tool_names(expected_tools)

        called_names = self._extract_tool_names(tools_called)

        total_calls = len(tools_called)

        unique_calls = len(called_names)

        duplicate_count = total_calls - unique_calls

        found = expected_names & called_names

        missing = expected_names - called_names

        extra = called_names - expected_names

        if not expected_names:

            score = 1.0

            reason = "No expected tools defined — nothing to evaluate."

        elif total_calls == 0:

            score = 0.0

            reason = f"No tools were called. Expected: {sorted(expected_names)}"

        else:

            total = max(len(expected_names), total_calls)

            score = len(found) / total

            if found == expected_names and not extra and duplicate_count == 0:

                reason = f"All {len(expected_names)} expected tools called exactly."

            else:

                parts = []

                if found:

                    parts.append(f"Correct: {sorted(found)}")

                if missing:

                    parts.append(f"Missing: {sorted(missing)}")

                if extra:

                    parts.append(f"Extra: {sorted(extra)}")

                if duplicate_count > 0:

                    parts.append(f"Duplicates: {duplicate_count}")

                reason = (

                    f"{len(found)}/{len(expected_names)} expected tools found, "

                    f"{total_calls} total calls. "

                    + ". ".join(parts)

                )

        return SubsetMatchResult(

            expected_tools=expected_names,

            called_tools=called_names,

            found_tools=found,

            missing_tools=missing,

            extra_tools=extra,

            duplicate_count=duplicate_count,

            total_calls=total_calls,

            score=score,

            reason=reason,

        )

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:

        """Evaluate tool correctness.

        Args:
            test_case: LLMTestCase with expected_tools and tools_called

        Returns:
            Score between 0.0 and 1.0
        """

        try:

            expected_tools = test_case.expected_tools or []

            tools_called = test_case.tools_called or []

            self.match_result = self._compute_subset_match(

                expected_tools, tools_called

            )

            self.score = self.match_result.score

            self.reason = self.match_result.reason

            self.success = self.score >= self.threshold

            if self.verbose_mode:

                print(f"[SubsetToolCorrectness] {self.reason}")

            return self.score

        except Exception as e:

            self.error = str(e)

            self.score = 0.0

            self.reason = f"Evaluation failed: {e}"

            self.success = False

            if self.strict_mode:

                raise

            return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:

        """Async version of measure (delegates to sync since no I/O needed)."""

        return self.measure(test_case, *args, **kwargs)

    def is_successful(self) -> bool:

        """Check if the metric score meets the threshold."""

        if self.score is None:

            return False

        return self.score >= self.threshold

    def get_missing_tools(self) -> Set[str]:

        """Get the set of expected tools that were NOT called."""

        if self.match_result is None:

            return set()

        return self.match_result.missing_tools

    def get_extra_tools(self) -> Set[str]:

        """Get the set of tools called that were NOT expected."""

        if self.match_result is None:

            return set()

        return self.match_result.extra_tools

    def get_duplicate_count(self) -> int:

        """Get the number of duplicate tool calls."""

        if self.match_result is None:

            return 0

        return self.match_result.duplicate_count
class SubsetArgumentCorrectnessMetric(BaseMetric):

    """BFCL-style subset matching for argument correctness.

    Only evaluates arguments for tools that appear in BOTH expected and called.
    Extra tools are ignored. Uses exact matching for arguments.

    For LLM-based semantic argument matching, use ReferenceArgumentCorrectnessMetric.

    Args:
        threshold: Minimum score to pass (default: 1.0)
        case_sensitive: Whether string comparisons are case-sensitive (default: False)
        include_reason: Include detailed reason in output (default: True)
    """

    def __init__(

        self,

        threshold: float = 1.0,

        case_sensitive: bool = False,

        include_reason: bool = True,

        strict_mode: bool = False,

        verbose_mode: bool = False,

    ):

        self.threshold = threshold

        self.case_sensitive = case_sensitive

        self.include_reason = include_reason

        self.strict_mode = strict_mode

        self.verbose_mode = verbose_mode

        self.score: Optional[float] = None

        self.reason: Optional[str] = None

        self.success: Optional[bool] = None

        self.error: Optional[str] = None

    @property

    def __name__(self) -> str:

        return "Argument Correctness [Subset]"

    def _normalize_value(self, value) -> str:

        """Normalize a value for comparison."""

        if value is None:

            return ""

        s = str(value)

        if not self.case_sensitive:

            s = s.lower()

        return s.strip()

    def _compare_args(

        self,

        expected_args: dict,

        actual_args: dict,

    ) -> tuple[float, List[str]]:

        """Compare argument dictionaries and return score + issues."""

        if not expected_args:

            return 1.0, []

        issues = []

        matches = 0

        total = len(expected_args)

        for key, expected_value in expected_args.items():

            if key not in actual_args:

                issues.append(f"Missing param '{key}'")

                continue

            actual_value = actual_args[key]

            exp_norm = self._normalize_value(expected_value)

            act_norm = self._normalize_value(actual_value)

            if exp_norm == act_norm:

                matches += 1

            else:

                if type(expected_value) != type(actual_value):

                    issues.append(

                        f"Type mismatch for '{key}': "

                        f"expected {type(expected_value).__name__}({expected_value}), "

                        f"got {type(actual_value).__name__}({actual_value})"

                    )

                else:

                    issues.append(

                        f"Value mismatch for '{key}': "

                        f"expected '{expected_value}', got '{actual_value}'"

                    )

        score = matches / total if total > 0 else 1.0

        return score, issues

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:

        """Evaluate argument correctness for matching tools only."""

        try:

            expected_tools = test_case.expected_tools or []

            tools_called = test_case.tools_called or []

            if not expected_tools:

                self.score = 1.0

                self.reason = "No expected tools defined — nothing to evaluate."

                self.success = True

                return self.score

            called_by_name = {}

            for tc in tools_called:

                if tc.name not in called_by_name:

                    called_by_name[tc.name] = tc

            tool_scores = []

            all_issues = []

            for expected in expected_tools:

                if expected.name not in called_by_name:

                    continue

                actual = called_by_name[expected.name]

                expected_args = expected.input_parameters or {}

                actual_args = actual.input_parameters or {}

                score, issues = self._compare_args(expected_args, actual_args)

                tool_scores.append(score)

                if issues:

                    all_issues.append(f"{expected.name}: {', '.join(issues)}")

            if not tool_scores:

                self.score = 1.0

                self.reason = "No matching tools to evaluate arguments for."

            else:

                self.score = sum(tool_scores) / len(tool_scores)

                if all_issues:

                    self.reason = f"Issues found: {'; '.join(all_issues)}"

                else:

                    self.reason = f"All {len(tool_scores)} matching tools have correct arguments."

            self.success = self.score >= self.threshold

            return self.score

        except Exception as e:

            self.error = str(e)

            self.score = 0.0

            self.reason = f"Evaluation failed: {e}"

            self.success = False

            if self.strict_mode:

                raise

            return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:

        """Async version of measure."""

        return self.measure(test_case, *args, **kwargs)

    def is_successful(self) -> bool:

        """Check if the metric score meets the threshold."""

        if self.score is None:

            return False

        return self.score >= self.threshold

