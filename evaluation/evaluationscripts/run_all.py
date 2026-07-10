"""
Run evaluation scripts across benchmarks and test dimensions.
Usage:
    python evaluationscripts/run_all.py --jwt-token "eyJ..." --benchmark mcpagentbench --agent multi
    python evaluationscripts/run_all.py --jwt-token "eyJ..." --benchmark bfcl --modes st-1t st-mt
    python evaluationscripts/run_all.py --jwt-token "eyJ..." --benchmark all
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
SCRIPT_DIR = Path(__file__).resolve().parent
BENCHMARKS = {

    "mcpagentbench": {

        "script": "evaluate_mcpagentbench.py",

        "modes": ["st-1t", "st-mt"],

        "needs_jwt": False,

    },

    "bfcl": {

        "script": "evaluate_bfcl.py",

        "modes": ["st-1t", "st-mt", "mt-mt"],

        "needs_jwt": True,

    },
}
RESULTS_DIR = SCRIPT_DIR.parent / "results"
def run_script(

    script: str, jwt_token: str | None, agent: str, mode: str,

    verbose: bool = False, limit: int | None = None,
) -> tuple[bool, float, str]:

    """Run a single evaluation script and return (success, duration, stderr)."""

    cmd = [

        sys.executable,

        str(SCRIPT_DIR / script),

        "--agent", agent,

        "--mode", mode,

    ]

    if jwt_token:

        cmd.extend(["--jwt-token", jwt_token])

    if verbose:

        cmd.append("--verbose")

    if limit:

        cmd.extend(["--limit", str(limit)])

    start = time.perf_counter()

    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR.parent), capture_output=True, text=True)

    duration = time.perf_counter() - start

    if result.stdout:

        print(result.stdout, end="")

    return result.returncode == 0, duration, result.stderr
def main() -> None:

    parser = argparse.ArgumentParser(description="Run evaluation scripts across benchmarks")

    parser.add_argument(

        "--jwt-token", "-t",

        help="JWT token for MCP authentication (required for bfcl)",

    )

    parser.add_argument(

        "--benchmark", "-b",

        choices=list(BENCHMARKS.keys()) + ["all"],

        default="all",

        help="Which benchmark to evaluate (default: all)",

    )

    parser.add_argument(

        "--agent", "-a",

        choices=["single", "multi", "both"],

        default="both",

        help="Agent type (default: both)",

    )

    parser.add_argument(

        "--modes", "-m",

        nargs="+",

        help="Which modes to run (default: all supported by benchmark)",

    )

    parser.add_argument(

        "--limit", "-l", type=int,

        help="Max test cases per mode (default: all)",

    )

    parser.add_argument(

        "--verbose", "-v", action="store_true",

        help="Show detailed output",

    )

    args = parser.parse_args()

    benchmarks = list(BENCHMARKS.keys()) if args.benchmark == "all" else [args.benchmark]

    agent_types = ["single", "multi"] if args.agent == "both" else [args.agent]

    runs = []

    for bench in benchmarks:

        config = BENCHMARKS[bench]

        if config["needs_jwt"] and not args.jwt_token:

            print(f"Skipping {bench}: requires --jwt-token")

            continue

        modes = args.modes if args.modes else config["modes"]

        modes = [m for m in modes if m in config["modes"]]

        for agent in agent_types:

            for mode in modes:

                runs.append((bench, config["script"], agent, mode))

    print(f"\n{'='*60}")

    print(f"AgentTim Evaluation Runner")

    print(f"{'='*60}")

    print(f"Benchmarks: {', '.join(benchmarks)}")

    print(f"Agents:     {', '.join(agent_types)}")

    print(f"Runs:       {len(runs)}")

    print(f"{'='*60}\n")

    results = []

    total_start = time.perf_counter()

    for i, (bench, script, agent, mode) in enumerate(runs, 1):

        print(f"[{i}/{len(runs)}] {bench} / {agent} / {mode} ...")

        success, duration, stderr = run_script(

            script, args.jwt_token, agent, mode, args.verbose, args.limit

        )

        status = "OK" if success else "FAILED"

        print(f"         {status} ({duration:.0f}s)\n")

        if not success and stderr:

            stderr_lines = stderr.strip().splitlines()

            for line in stderr_lines[-5:]:

                print(f"         stderr: {line}")

            print()

        results.append((bench, agent, mode, success, duration))

    total_duration = time.perf_counter() - total_start

    print(f"\n{'='*60}")

    print("SUMMARY")

    print(f"{'='*60}")

    passed = sum(1 for *_, s, _ in results if s)

    failed = len(results) - passed

    print(f"Passed: {passed}/{len(results)}")

    if failed:

        print(f"Failed: {failed}")

        for bench, agent, mode, success, _ in results:

            if not success:

                print(f"  - {bench} / {agent} / {mode}")

    print(f"Total:  {total_duration:.0f}s")

    print(f"\nResults saved to: evaluation/results/")

    _print_error_report()
def _print_error_report() -> None:

    """Read all _errors.json files from today's runs and print a consolidated report."""

    if not RESULTS_DIR.exists():

        return

    error_files = sorted(RESULTS_DIR.rglob("*_errors.json"), reverse=True)

    if not error_files:

        return

    latest_prefix = error_files[0].stem.split("_")[0]

    recent_files = [f for f in error_files if f.stem.startswith(latest_prefix)]

    all_errors = []

    for filepath in recent_files:

        try:

            errors = json.loads(filepath.read_text(encoding="utf-8"))

            benchmark = filepath.parent.name

            for err in errors:

                err["benchmark"] = benchmark

            all_errors.extend(errors)

        except (json.JSONDecodeError, OSError):

            continue

    if not all_errors:

        return

    print(f"\n{'='*60}")

    print(f"ERROR REPORT ({len(all_errors)} errors across {len(recent_files)} runs)")

    print(f"{'='*60}")

    by_type: dict[str, list[dict]] = {}

    for err in all_errors:

        by_type.setdefault(err["error_type"], []).append(err)

    for error_type, errors in sorted(by_type.items(), key=lambda x: -len(x[1])):

        tc_ids = [f"{e.get('benchmark', '?')}/{e['test_case_id']}" for e in errors]

        print(f"\n  {error_type} ({len(errors)}x)")

        for tc_id in tc_ids:

            print(f"    - {tc_id}")

        print(f"    Example: {errors[0]['error_message'][:120]}")

    print(f"\nDetails: {RESULTS_DIR}/*_errors.json")
if __name__ == "__main__":

    main()

