"""
Re-score Argument Correctness for test cases that failed with 403 errors.
The LLM-as-Judge (Azure OpenAI) was intermittently unavailable during evaluation
runs, causing Argument Correctness scores to be set to 0.0 with reason containing
"403". This script re-runs ONLY those specific test cases using the stored
comparison data (expected/actual tool calls are fully preserved in result files).
Usage:
    cd agenttim/evaluation
    python scripts/rescore_403_errors.py --dry-run          # Preview affected files
    python scripts/rescore_403_errors.py                     # Re-score and update files
    python scripts/rescore_403_errors.py --input results     # Use original results dir
    python scripts/rescore_403_errors.py --concurrency 5     # Limit parallel requests
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any
if sys.platform == "win32":

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
_eval_dir = Path(__file__).resolve().parent.parent
_python_services_dir = _eval_dir.parent.parent
for _path in [str(_eval_dir.parent), str(_python_services_dir)]:

    if _path not in sys.path:

        sys.path.insert(0, _path)
from deepeval.test_case import LLMTestCase, ToolCall
from agenttim.config.settings import get_settings
from agenttim.services.llm_service import create_llm, EVAL_JUDGE_MODEL
from agenttim.services.deepeval_model import LangChainDeepEvalModel
from agenttim.evaluation.eval_utils.argument_correctness import (

    ReferenceArgumentCorrectnessMetric,
)
METRIC_KEY = "Argument Correctness [Reference]"
def find_affected_files(input_dir: Path) -> list[dict[str, Any]]:

    """Find all result files containing test cases with 403 errors in AC metric."""

    affected = []

    for fp in sorted(input_dir.rglob("*.json")):

        if "_errors" in fp.name:

            continue

        try:

            data = json.loads(fp.read_text(encoding="utf-8"))

            test_cases = data.get("test_cases", [])

            if not test_cases:

                continue

            n_403 = 0

            for tc in test_cases:

                ac = tc.get("metrics", {}).get(METRIC_KEY, {})

                reason = str(ac.get("reason", ""))

                if "403" in reason:

                    n_403 += 1

            if n_403 > 0:

                affected.append({

                    "path": fp,

                    "rel_path": str(fp.relative_to(input_dir)),

                    "n_403": n_403,

                    "n_total": len(test_cases),

                    "agent": data.get("agent_type", "?"),

                    "mode": data.get("mode", "?"),

                    "benchmark": data.get("benchmark", "?"),

                    "num_tools": data.get("num_tools"),

                })

        except (json.JSONDecodeError, OSError):

            continue

    return affected
def build_test_case_from_comparison(comparison: dict) -> LLMTestCase | None:

    """Build a DeepEval LLMTestCase from stored comparison data."""

    expected = comparison.get("expected", [])

    actual = comparison.get("actual", [])

    if not expected and not actual:

        return None

    expected_tools = [

        ToolCall(

            name=t["name"],

            input_parameters=t.get("input_parameters", {}),

        )

        for t in expected

    ]

    actual_tools = [

        ToolCall(

            name=t["name"],

            input_parameters=t.get("input_parameters", {}),

        )

        for t in actual

    ]

    return LLMTestCase(

        input="rescore",

        actual_output="rescore",

        expected_tools=expected_tools,

        tools_called=actual_tools,

    )
async def rescore_file(

    fp: Path,

    metric_factory,

    semaphore: asyncio.Semaphore,

    dry_run: bool = False,
) -> dict[str, Any]:

    """Re-score all 403-affected test cases in a single result file."""

    data = json.loads(fp.read_text(encoding="utf-8"))

    test_cases = data.get("test_cases", [])

    rescored = 0

    failed = 0

    skipped = 0

    for tc in test_cases:

        ac = tc.get("metrics", {}).get(METRIC_KEY, {})

        reason = str(ac.get("reason", ""))

        if "403" not in reason:

            skipped += 1

            continue

        comparison = ac.get("comparison", {})

        if not comparison:

            skipped += 1

            continue

        if dry_run:

            rescored += 1

            continue

        llm_test_case = build_test_case_from_comparison(comparison)

        if llm_test_case is None:

            skipped += 1

            continue

        async with semaphore:

            metric = metric_factory()

            try:

                await metric.a_measure(llm_test_case)

                ac["score"] = metric.score

                ac["reason"] = metric.reason

                ac["success"] = metric.success

                rescored += 1

            except Exception as e:

                failed += 1

                ac["rescore_error"] = str(e)

    if not dry_run and rescored > 0:

        fp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"path": str(fp), "rescored": rescored, "failed": failed, "skipped": skipped}
async def rescore_all(

    input_dir: Path,

    dry_run: bool = False,

    concurrency: int = 3,
) -> None:

    """Find and re-score all 403-affected test cases."""

    print(f"Scanning: {input_dir}")

    affected = find_affected_files(input_dir)

    if not affected:

        print("No 403 errors found.")

        return

    total_403 = sum(f["n_403"] for f in affected)

    print(f"Found {total_403} affected test cases in {len(affected)} files:")

    print()

    print(f"  {'File':<75} | {'403s':>5} | {'Total':>5}")

    print("  " + "-" * 95)

    for f in affected:

        print(f"  {f['rel_path']:<75} | {f['n_403']:>5} | {f['n_total']:>5}")

    print()

    if dry_run:

        print("[DRY RUN] Would re-score the above test cases. Run without --dry-run to execute.")

        return

    print(f"Initializing LLM judge: {EVAL_JUDGE_MODEL}")

    settings = get_settings()

    judge_llm = create_llm(settings, model_override=EVAL_JUDGE_MODEL, temperature=0.0)

    eval_model = LangChainDeepEvalModel(judge_llm)

    def metric_factory():

        return ReferenceArgumentCorrectnessMetric(

            model=eval_model,

            threshold=1.0,

            include_reason=True,

        )

    print("Testing LLM connection...")

    try:

        test_metric = metric_factory()

        test_tc = LLMTestCase(

            input="test",

            actual_output="test",

            expected_tools=[ToolCall(name="test_tool", input_parameters={"x": 1})],

            tools_called=[ToolCall(name="test_tool", input_parameters={"x": 1})],

        )

        await test_metric.a_measure(test_tc)

        print(f"  Connection OK (score={test_metric.score})")

    except Exception as e:

        print(f"  Connection FAILED: {e}")

        print("  Aborting. Check VPN and Azure OpenAI endpoint.")

        return

    semaphore = asyncio.Semaphore(concurrency)

    start = time.time()

    print(f"\nRe-scoring {total_403} test cases (concurrency={concurrency})...")

    print()

    results = []

    for f in affected:

        result = await rescore_file(

            f["path"],

            metric_factory,

            semaphore,

            dry_run=False,

        )

        results.append(result)

        print(

            f"  {f['rel_path']:<75} | "

            f"rescored={result['rescored']:>3} | "

            f"failed={result['failed']:>3}"

        )

    elapsed = time.time() - start

    total_rescored = sum(r["rescored"] for r in results)

    total_failed = sum(r["failed"] for r in results)

    print()

    print(f"Done in {elapsed:.1f}s")

    print(f"  Rescored: {total_rescored}")

    print(f"  Failed:   {total_failed}")

    print(f"  Files updated: {sum(1 for r in results if r['rescored'] > 0)}")
def main():

    parser = argparse.ArgumentParser(

        description="Re-score Argument Correctness for 403-affected test cases",

    )

    parser.add_argument(

        "--input", "-i", default="results",

        help="Input directory (default: results)",

    )

    parser.add_argument(

        "--dry-run", action="store_true",

        help="Only show affected files, don't re-score",

    )

    parser.add_argument(

        "--concurrency", "-c", type=int, default=3,

        help="Max concurrent LLM calls (default: 3)",

    )

    args = parser.parse_args()

    input_dir = Path(args.input)

    if not input_dir.is_absolute():

        input_dir = Path(__file__).resolve().parent.parent / input_dir

    asyncio.run(rescore_all(input_dir, dry_run=args.dry_run, concurrency=args.concurrency))
if __name__ == "__main__":

    main()

