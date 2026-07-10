"""Reference-based Argument Correctness metric using LLM-as-judge.
Compares actual tool call arguments against expected arguments with
type-safety awareness. Unlike DeepEval's built-in ArgumentCorrectnessMetric
(which is reference-free and only evaluates args against the user input),
this metric uses the defined expected_tools as ground truth.
Evaluation criteria:
    - Parameter names: exact match required
    - Parameter values: semantic equivalence (LLM judges)
    - Type safety: mismatched types (e.g. "5" vs 5) are flagged
    - Extra parameters: penalized (model hallucinated args)
    - Missing parameters: penalized
    - Parameterless tools: any args = score 0
"""
import json
import textwrap
from typing import Any, Dict, List, Optional
from deepeval.metrics.base_metric import BaseMetric
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, ToolCall
JUDGE_PROMPT = textwrap.dedent("""\
    You are an evaluation judge for tool call argument correctness.

    Compare the EXPECTED tool calls against the ACTUAL tool calls.
    For each tool, evaluate whether the actual arguments match the expected arguments.

    ## Evaluation Rules

    1. **Parameter names**: Must match exactly. Extra or missing parameters are errors.
    2. **Parameter values**: Must be semantically equivalent.
       - "Repository" and "Repository" = match
       - "dashboardcases" and "DashboardCases" = match (case-insensitive for identifiers)
    3. **Type safety**: Flag type mismatches explicitly.
       - "5" (string) vs 5 (integer) = TYPE MISMATCH — penalize
       - "true" (string) vs true (boolean) = TYPE MISMATCH — penalize
       - Both strings with same value = match
    4. **Parameterless tools**: If expected has NO parameters but actual has parameters,
       score 0 for that tool — the model hallucinated arguments.
    5. **Extra parameters**: If actual has parameters not in expected, penalize.
    6. **Missing parameters**: If expected has parameters not in actual, penalize.

    ## Scoring

    Return a score between 0.0 and 1.0:
    - 1.0 = all tools have correct arguments with correct types
    - 0.5-0.9 = minor issues (e.g. one type mismatch, one extra optional param)
    - 0.0-0.4 = major issues (wrong values, missing required params, args on parameterless tool)

    If there are no expected tools, return score 1.0.

    ## Input

    Expected tool calls:
    {expected_tools}

    Actual tool calls:
    {actual_tools}

    ## Output Format

    Return ONLY valid JSON:
    {{
        "score": <float between 0.0 and 1.0>,
        "reason": "<detailed explanation listing each tool, its expected vs actual params, type mismatches, and issues found>"
    }}
""")
def _serialize_tool_calls(tool_calls: List[ToolCall]) -> str:

    """Serialize tool calls to a readable JSON string for the LLM judge."""

    serialized = []

    for tc in tool_calls:

        entry = {"name": tc.name, "input_parameters": tc.input_parameters or {}}

        typed_params = {}

        for key, value in entry["input_parameters"].items():

            typed_params[key] = {

                "value": value,

                "type": type(value).__name__,

            }

        entry["input_parameters_typed"] = typed_params

        serialized.append(entry)

    return json.dumps(serialized, indent=2, ensure_ascii=False)
def _parse_judge_response(response: str) -> Dict[str, Any]:

    """Parse the LLM judge's JSON response."""

    cleaned = response.strip()

    if cleaned.startswith("```"):

        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]

        cleaned = cleaned.rsplit("```", 1)[0]

    return json.loads(cleaned)
class ReferenceArgumentCorrectnessMetric(BaseMetric):

    """LLM-as-judge metric comparing actual tool args against expected args.

    Unlike DeepEval's built-in ArgumentCorrectnessMetric (reference-free),
    this metric is reference-based: it compares tools_called against
    expected_tools and considers type safety.

    Example:
        ```python
        metric = ReferenceArgumentCorrectnessMetric(
            model=eval_model,
            threshold=1.0,
        )
        evaluate(test_cases=[...], metrics=[metric])
        ```
    """

    def __init__(

        self,

        model: DeepEvalBaseLLM,

        threshold: float = 1.0,

        include_reason: bool = True,

        strict_mode: bool = False,

        async_mode: bool = True,

        verbose_mode: bool = False,

    ):

        self.model = model

        self.threshold = threshold

        self.include_reason = include_reason

        self.strict_mode = strict_mode

        self.async_mode = async_mode

        self.verbose_mode = verbose_mode

        self.score: Optional[float] = None

        self.reason: Optional[str] = None

        self.success: Optional[bool] = None

        self.evaluation_model: Optional[str] = None

        self.evaluation_cost: Optional[float] = None

        self.verbose_logs: Optional[str] = None

        self.error: Optional[str] = None

    @property

    def __name__(self) -> str:

        return "Argument Correctness [Reference]"

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:

        """Synchronous measurement — delegates to async."""

        import asyncio

        loop = asyncio.get_event_loop()

        return loop.run_until_complete(self.a_measure(test_case))

    async def a_measure(

        self, test_case: LLMTestCase, *args, **kwargs

    ) -> float:

        """Evaluate argument correctness by comparing expected vs actual args."""

        expected_tools = test_case.expected_tools or []

        tools_called = test_case.tools_called or []

        if not expected_tools:

            self.score = 1.0

            self.reason = "No expected tools defined — nothing to evaluate."

            self.success = True

            return self.score

        has_any_params = any(t.input_parameters for t in expected_tools)

        has_any_actual_params = any(t.input_parameters for t in tools_called)

        if not has_any_params and not has_any_actual_params:

            self.score = 1.0

            self.reason = (

                "N/A — all expected tools are parameterless and no "

                "arguments were passed. Nothing to evaluate."

            )

            self.success = True

            return self.score

        if not has_any_params and has_any_actual_params:

            tools_with_args = [

                f"{t.name}({t.input_parameters})"

                for t in tools_called

                if t.input_parameters

            ]

            self.score = 0.0

            self.reason = (

                f"Expected parameterless tool calls but model passed "

                f"arguments: {', '.join(tools_with_args)}"

            )

            self.success = False

            return self.score

        prompt = JUDGE_PROMPT.format(

            expected_tools=_serialize_tool_calls(expected_tools),

            actual_tools=_serialize_tool_calls(tools_called),

        )

        if self.verbose_mode:

            self.verbose_logs = prompt

        try:

            response = await self.model.a_generate(prompt)

            parsed = _parse_judge_response(response)

            self.score = max(0.0, min(1.0, float(parsed["score"])))

            self.reason = parsed.get("reason", "")

            self.evaluation_model = self.model.get_model_name()

        except Exception as e:

            self.error = str(e)

            self.score = 0.0

            self.reason = f"Evaluation failed: {e}"

        self.success = self.score >= self.threshold

        return self.score

    def is_successful(self) -> bool:

        """Check if the metric score meets the threshold."""

        if self.score is None:

            return False

        return self.score >= self.threshold

