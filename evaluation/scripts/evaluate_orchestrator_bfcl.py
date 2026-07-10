"""
Orchestrator Evaluation Script for BFCL Dataset.
This script evaluates the Orchestrator agent pattern against BFCL test cases,
measuring:
- Tool call accuracy (AST matching)
- Argument correctness
- Delegation trace
- Token usage (input/output)
- Latency (per call and total)
Usage:
    python evaluate_orchestrator_bfcl.py --jwt-token "..." [--verbose]
    python evaluate_orchestrator_bfcl.py --dry-run  # Test without API calls
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
_script_dir = Path(__file__).resolve().parent
_evaluation_dir = _script_dir.parent
_agenttim_dir = _evaluation_dir.parent
_python_services_dir = _agenttim_dir.parent
for p in [str(_agenttim_dir), str(_python_services_dir)]:

    if p not in sys.path:

        sys.path.insert(0, p)
import importlib.util
_bfcl_path = _evaluation_dir / "test_cases" / "singleturn" / "bfcl_sturn_mt.py"
spec = importlib.util.spec_from_file_location("bfcl_sturn_mt", _bfcl_path)
bfcl_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bfcl_module)
BFCL_ST_MT_CASES = bfcl_module.BFCL_ST_MT_CASES
logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BFCLEvaluator")
@dataclass
class TokenUsage:

    """Track token usage for a single call."""

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    def __add__(self, other: "TokenUsage") -> "TokenUsage":

        return TokenUsage(

            input_tokens=self.input_tokens + other.input_tokens,

            output_tokens=self.output_tokens + other.output_tokens,

            total_tokens=self.total_tokens + other.total_tokens,

        )
@dataclass
class ToolCallResult:

    """Result of a single tool call."""

    name: str

    arguments: dict

    timestamp: float = 0.0
@dataclass
class DelegationStep:

    """A single delegation step in the orchestrator."""

    agent_name: str

    task_description: str

    tool_calls: list[ToolCallResult] = field(default_factory=list)

    latency_ms: float = 0.0

    tokens: TokenUsage = field(default_factory=TokenUsage)
@dataclass
class EvaluationResult:

    """Result of evaluating a single test case."""

    test_id: str

    input_query: str

    tool_name_correct: bool = False

    arguments_correct: bool = False

    overall_correct: bool = False

    expected_tool: str = ""

    actual_tool: str = ""

    expected_args: dict = field(default_factory=dict)

    actual_args: dict = field(default_factory=dict)

    arg_errors: list[str] = field(default_factory=list)

    delegation_steps: list[DelegationStep] = field(default_factory=list)

    total_latency_ms: float = 0.0

    tokens: TokenUsage = field(default_factory=TokenUsage)

    error: Optional[str] = None
@dataclass
class EvaluationReport:

    """Summary report for all test cases."""

    timestamp: str

    pattern: str = "orchestrator"

    dataset: str = "BFCL"

    total_cases: int = 0

    passed_cases: int = 0

    failed_cases: int = 0

    error_cases: int = 0

    tool_accuracy: float = 0.0

    argument_accuracy: float = 0.0

    overall_accuracy: float = 0.0

    avg_latency_ms: float = 0.0

    p50_latency_ms: float = 0.0

    p95_latency_ms: float = 0.0

    total_input_tokens: int = 0

    total_output_tokens: int = 0

    avg_tokens_per_case: float = 0.0

    results: list[EvaluationResult] = field(default_factory=list)
class ASTMatcher:

    """Evaluate tool calls using AST-style matching (BFCL methodology)."""

    @staticmethod

    def normalize_string(s: str) -> str:

        """Normalize string for comparison (case-insensitive, whitespace)."""

        if not isinstance(s, str):

            return str(s)

        return s.lower().strip().replace("_", " ").replace("-", " ")

    @staticmethod

    def values_match(actual: Any, expected: Any) -> bool:

        """Check if actual value matches expected (with tolerance for alternatives)."""

        if isinstance(expected, list):

            return any(ASTMatcher.values_match(actual, e) for e in expected)

        if isinstance(expected, str) and isinstance(actual, str):

            return ASTMatcher.normalize_string(actual) == ASTMatcher.normalize_string(expected)

        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):

            if isinstance(expected, float) or isinstance(actual, float):

                return abs(float(actual) - float(expected)) < 0.0001

            return actual == expected

        if isinstance(expected, bool):

            if isinstance(actual, bool):

                return actual == expected

            if isinstance(actual, str):

                return actual.lower() in ("true", "1", "yes") if expected else actual.lower() in ("false", "0", "no")

        if isinstance(expected, list) and isinstance(actual, list):

            if len(actual) != len(expected):

                return False

            return all(ASTMatcher.values_match(a, e) for a, e in zip(actual, expected))

        if isinstance(expected, dict) and isinstance(actual, dict):

            for key, exp_val in expected.items():

                if key not in actual:

                    return False

                if not ASTMatcher.values_match(actual[key], exp_val):

                    return False

            return True

        return actual == expected

    @staticmethod

    def evaluate_tool_call(

        actual_call: ToolCallResult,

        expected: dict,

        evaluation_criteria: dict

    ) -> tuple[bool, bool, list[str]]:

        """
        Evaluate a tool call against expected output.

        Returns:
            (tool_name_correct, arguments_correct, list of arg errors)
        """

        errors = []

        expected_name = expected.get("name", "")

        if isinstance(expected_name, list):

            tool_name_correct = actual_call.name in expected_name

        else:

            tool_name_correct = actual_call.name == expected_name

        if not tool_name_correct:

            errors.append(f"Wrong tool: expected {expected_name}, got {actual_call.name}")

            return tool_name_correct, False, errors

        required_args = evaluation_criteria.get("required_args", [])

        for arg in required_args:

            if arg not in actual_call.arguments:

                errors.append(f"Missing required argument: {arg}")

        expected_args = expected.get("arguments", {})

        arguments_correct = True

        for arg_name, expected_values in expected_args.items():

            actual_value = actual_call.arguments.get(arg_name)

            if actual_value is None:

                continue

            if not ASTMatcher.values_match(actual_value, expected_values):

                errors.append(f"Argument '{arg_name}': expected {expected_values}, got {actual_value}")

                arguments_correct = False

        if "arg_values_must_contain" in evaluation_criteria:

            required_values = set(evaluation_criteria["arg_values_must_contain"])

            actual_values = set()

            for v in actual_call.arguments.values():

                if isinstance(v, (int, float)):

                    actual_values.add(v)

                elif isinstance(v, list):

                    actual_values.update(v)

            if not required_values.issubset(actual_values):

                missing = required_values - actual_values

                errors.append(f"Missing required values: {missing}")

                arguments_correct = False

        if "exact_values" in evaluation_criteria:

            for arg_name, exact_val in evaluation_criteria["exact_values"].items():

                actual_val = actual_call.arguments.get(arg_name)

                if actual_val != exact_val:

                    errors.append(f"Exact match failed for '{arg_name}': expected {exact_val}, got {actual_val}")

                    arguments_correct = False

        allowed_args = set(expected_args.keys())

        if required_args:

            allowed_args.update(required_args)

        allowed_args.update(["get_area", "get_perimeter", "get_circumference", "equal_variance",

                           "include_human_impact", "price_type", "trend_type", "rank", "category"])

        for arg_name in actual_call.arguments:

            if arg_name not in allowed_args:

                pass

        return tool_name_correct, arguments_correct and len(errors) == 0, errors
class MockOrchestrator:

    """Mock orchestrator for testing the evaluation framework."""

    def __init__(self):

        self.call_count = 0

    async def initialize(self):

        pass

    async def run(

        self,

        query: str,

        available_functions: list[dict],

        on_delegation: callable = None,

        on_tool_call: callable = None,

    ) -> dict:

        """Simulate orchestrator run with mock responses."""

        self.call_count += 1

        if on_delegation:

            on_delegation("intent", f"Analyze: {query[:50]}...")

            await asyncio.sleep(0.1)

            on_delegation("schema_discovery", "Map to schema")

            await asyncio.sleep(0.1)

        selected_func = None

        for func in available_functions:

            name = func["name"].lower()

            query_lower = query.lower()

            if "triangle" in query_lower and "triangle" in name:

                selected_func = func

                break

            elif "delete" in query_lower and "delete" in name:

                selected_func = func

                break

            elif "price" in query_lower and "price" in name:

                selected_func = func

                break

            elif "forecast" in query_lower and "forecast" in name:

                selected_func = func

                break

            elif "color" in query_lower and "color" in name:

                selected_func = func

                break

            elif ("hcf" in query_lower or "factor" in query_lower) and ("hcf" in name or "gcd" in name):

                selected_func = func

                break

            elif "t-test" in query_lower and "ttest" in name:

                selected_func = func

                break

            elif "neuronal" in query_lower and "neuronal" in name:

                selected_func = func

                break

            elif "tennis" in query_lower and "tennis" in name:

                selected_func = func

                break

            elif "forest" in query_lower and "forest" in name and "human" not in name:

                if "include_human_impact" in str(func.get("parameters", {})):

                    selected_func = func

                    break

        if not selected_func:

            selected_func = available_functions[0]

        mock_args = self._generate_mock_args(query, selected_func)

        if on_tool_call:

            on_tool_call(selected_func["name"], mock_args, "{}")

        return {

            "tool_calls": [{"name": selected_func["name"], "arguments": mock_args}],

            "response": f"Mock response for {selected_func['name']}",

            "tokens": {"input": 150, "output": 50, "total": 200},

        }

    def _generate_mock_args(self, query: str, func: dict) -> dict:

        """Generate mock arguments based on query and function schema."""

        args = {}

        params = func.get("parameters", {}).get("properties", {})

        required = func.get("parameters", {}).get("required", [])

        for param_name, param_info in params.items():

            param_type = param_info.get("type", "string")

            if param_type == "integer":

                import re

                numbers = re.findall(r'\b(\d+)\b', query)

                if numbers:

                    args[param_name] = int(numbers[0])

                    numbers.pop(0)

                else:

                    args[param_name] = 1

            elif param_type == "float" or param_type == "number":

                import re

                numbers = re.findall(r'\b(\d+\.?\d*)\b', query)

                if numbers:

                    args[param_name] = float(numbers[0])

                else:

                    args[param_name] = 1.0

            elif param_type == "boolean":

                args[param_name] = True

            elif param_type == "array":

                import re

                arrays = re.findall(r'\[([^\]]+)\]', query)

                if arrays:

                    try:

                        args[param_name] = [int(x.strip()) for x in arrays[0].split(",")]

                        arrays.pop(0)

                    except:

                        args[param_name] = []

                else:

                    args[param_name] = []

            else:

                if "location" in param_name or "region" in param_name:

                    if "new york" in query.lower():

                        args[param_name] = "New York"

                    elif "yellowstone" in query.lower():

                        args[param_name] = "Yellowstone"

                    else:

                        args[param_name] = "Unknown"

                elif "room" in param_name:

                    args[param_name] = "living room"

                elif "gender" in param_name:

                    args[param_name] = "women"

                elif "sport" in param_name:

                    args[param_name] = "tennis"

                else:

                    args[param_name] = "value"

        return args
class OrchestratorBFCLEvaluator:

    """Evaluate Orchestrator pattern against BFCL test cases."""

    def __init__(

        self,

        orchestrator,

        test_cases: list[dict],

        verbose: bool = False,

    ):

        self.orchestrator = orchestrator

        self.test_cases = test_cases

        self.verbose = verbose

        self.matcher = ASTMatcher()

    async def evaluate_single(self, test_case: dict) -> EvaluationResult:

        """Evaluate a single test case."""

        result = EvaluationResult(

            test_id=test_case["id"],

            input_query=test_case["input"],

            expected_tool=str(test_case["expected_tool_call"]["name"]),

            expected_args=test_case["expected_tool_call"]["arguments"],

        )

        delegation_steps = []

        tool_calls = []

        def on_delegation(agent_name: str, task: str):

            delegation_steps.append(DelegationStep(

                agent_name=agent_name,

                task_description=task,

            ))

        def on_tool_call(name: str, args: dict, response: str):

            tool_calls.append(ToolCallResult(

                name=name,

                arguments=args,

                timestamp=time.time(),

            ))

        start_time = time.time()

        try:

            response = await self.orchestrator.run(

                query=test_case["input"],

                available_functions=test_case["available_functions"],

                on_delegation=on_delegation,

                on_tool_call=on_tool_call,

            )

            result.total_latency_ms = (time.time() - start_time) * 1000

            if "tokens" in response:

                result.tokens = TokenUsage(

                    input_tokens=response["tokens"].get("input", 0),

                    output_tokens=response["tokens"].get("output", 0),

                    total_tokens=response["tokens"].get("total", 0),

                )

            if tool_calls:

                actual_call = tool_calls[-1]

            elif "tool_calls" in response and response["tool_calls"]:

                tc = response["tool_calls"][0]

                actual_call = ToolCallResult(

                    name=tc["name"],

                    arguments=tc.get("arguments", {}),

                )

            else:

                result.error = "No tool call made"

                return result

            result.actual_tool = actual_call.name

            result.actual_args = actual_call.arguments

            result.delegation_steps = delegation_steps

            tool_correct, args_correct, errors = self.matcher.evaluate_tool_call(

                actual_call=actual_call,

                expected=test_case["expected_tool_call"],

                evaluation_criteria=test_case["evaluation_criteria"],

            )

            result.tool_name_correct = tool_correct

            result.arguments_correct = args_correct

            result.overall_correct = tool_correct and args_correct

            result.arg_errors = errors

        except Exception as e:

            result.error = str(e)

            result.total_latency_ms = (time.time() - start_time) * 1000

        return result

    async def evaluate_all(self) -> EvaluationReport:

        """Evaluate all test cases and generate report."""

        report = EvaluationReport(

            timestamp=datetime.now().isoformat(),

            total_cases=len(self.test_cases),

        )

        latencies = []

        for i, test_case in enumerate(self.test_cases):

            if self.verbose:

                logger.info(f"Evaluating {i+1}/{len(self.test_cases)}: {test_case['id']}")

            result = await self.evaluate_single(test_case)

            report.results.append(result)

            if result.error:

                report.error_cases += 1

            elif result.overall_correct:

                report.passed_cases += 1

            else:

                report.failed_cases += 1

            latencies.append(result.total_latency_ms)

            report.total_input_tokens += result.tokens.input_tokens

            report.total_output_tokens += result.tokens.output_tokens

            if self.verbose:

                status = "PASS" if result.overall_correct else "FAIL"

                logger.info(f"  [{status}] Tool: {result.actual_tool} | Latency: {result.total_latency_ms:.0f}ms")

                if result.arg_errors:

                    for err in result.arg_errors:

                        logger.info(f"    - {err}")

        report.tool_accuracy = sum(1 for r in report.results if r.tool_name_correct) / len(report.results)

        report.argument_accuracy = sum(1 for r in report.results if r.arguments_correct) / len(report.results)

        report.overall_accuracy = report.passed_cases / report.total_cases

        if latencies:

            latencies_sorted = sorted(latencies)

            report.avg_latency_ms = sum(latencies) / len(latencies)

            report.p50_latency_ms = latencies_sorted[len(latencies) // 2]

            report.p95_latency_ms = latencies_sorted[int(len(latencies) * 0.95)]

        report.avg_tokens_per_case = (report.total_input_tokens + report.total_output_tokens) / report.total_cases

        return report

    def print_report(self, report: EvaluationReport):

        """Print a formatted report."""

        PASS = "[PASS]"

        FAIL = "[FAIL]"

        CHECK = "[+]"

        CROSS = "[-]"

        print("\n" + "=" * 70)

        print("  ORCHESTRATOR EVALUATION REPORT - BFCL Dataset")

        print("=" * 70)

        print(f"  Timestamp: {report.timestamp}")

        print(f"  Pattern:   {report.pattern}")

        print(f"  Dataset:   {report.dataset}")

        print()

        print("  ACCURACY")

        print("  " + "-" * 40)

        print(f"  Total Cases:        {report.total_cases}")

        print(f"  Passed:             {report.passed_cases} ({report.passed_cases/report.total_cases*100:.1f}%)")

        print(f"  Failed:             {report.failed_cases}")

        print(f"  Errors:             {report.error_cases}")

        print()

        print(f"  Tool Accuracy:      {report.tool_accuracy*100:.1f}%")

        print(f"  Argument Accuracy:  {report.argument_accuracy*100:.1f}%")

        print(f"  Overall Accuracy:   {report.overall_accuracy*100:.1f}%")

        print()

        print("  PERFORMANCE")

        print("  " + "-" * 40)

        print(f"  Avg Latency:        {report.avg_latency_ms:.0f}ms")

        print(f"  P50 Latency:        {report.p50_latency_ms:.0f}ms")

        print(f"  P95 Latency:        {report.p95_latency_ms:.0f}ms")

        print()

        print(f"  Total Input Tokens: {report.total_input_tokens:,}")

        print(f"  Total Output Tokens:{report.total_output_tokens:,}")

        print(f"  Avg Tokens/Case:    {report.avg_tokens_per_case:.0f}")

        print()

        print("  INDIVIDUAL RESULTS")

        print("  " + "-" * 40)

        for r in report.results:

            status = PASS if r.overall_correct else FAIL

            tool_status = CHECK if r.tool_name_correct else CROSS

            arg_status = CHECK if r.arguments_correct else CROSS

            print(f"  {status} {r.test_id}")

            print(f"     Tool: {tool_status} {r.actual_tool}")

            print(f"     Args: {arg_status} | Latency: {r.total_latency_ms:.0f}ms | Tokens: {r.tokens.total_tokens}")

            if r.arg_errors:

                for err in r.arg_errors[:2]:

                    print(f"       - {err[:60]}")

            if r.error:

                print(f"       ERROR: {r.error[:60]}")

        print()

        print("=" * 70)

    def save_report(self, report: EvaluationReport, output_path: Path):

        """Save report to JSON file."""

        def to_dict(obj):

            if hasattr(obj, "__dataclass_fields__"):

                return {k: to_dict(v) for k, v in asdict(obj).items()}

            elif isinstance(obj, list):

                return [to_dict(item) for item in obj]

            elif isinstance(obj, dict):

                return {k: to_dict(v) for k, v in obj.items()}

            return obj

        report_dict = to_dict(report)

        with open(output_path, "w", encoding="utf-8") as f:

            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved to {output_path}")
async def main():

    parser = argparse.ArgumentParser(

        description="Evaluate Orchestrator pattern against BFCL dataset"

    )

    parser.add_argument(

        "--jwt-token", "-t",

        type=str,

        help="JWT token for MCP authentication",

    )

    parser.add_argument(

        "--verbose", "-v",

        action="store_true",

        help="Show detailed output",

    )

    parser.add_argument(

        "--dry-run",

        action="store_true",

        help="Run with mock orchestrator (no API calls)",

    )

    parser.add_argument(

        "--output", "-o",

        type=str,

        default="bfcl_orchestrator_report.json",

        help="Output file for JSON report",

    )

    args = parser.parse_args()

    if args.dry_run:

        logger.info("Running in DRY-RUN mode with mock orchestrator")

        orchestrator = MockOrchestrator()

    else:

        if not args.jwt_token:

            logger.error("JWT token required for real evaluation. Use --dry-run for testing.")

            sys.exit(1)

        from config.settings import get_settings

        from orchestrator.orchestrator_agent import OrchestratorAgent

        settings = get_settings()

        orchestrator = OrchestratorAgent(settings, jwt_token=args.jwt_token)

    await orchestrator.initialize()

    evaluator = OrchestratorBFCLEvaluator(

        orchestrator=orchestrator,

        test_cases=BFCL_ST_MT_CASES,

        verbose=args.verbose,

    )

    logger.info(f"Starting evaluation of {len(BFCL_ST_MT_CASES)} BFCL test cases...")

    report = await evaluator.evaluate_all()

    evaluator.print_report(report)

    output_path = Path(args.output)

    evaluator.save_report(report, output_path)
if __name__ == "__main__":

    asyncio.run(main())

