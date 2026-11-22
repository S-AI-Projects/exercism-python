#!/usr/bin/env python3
"""Isolated test runner for exercises/practice/poker (Task R36-T029).

This tool executes tests for the poker exercise in an isolated temporary
scratch directory. It copies the exercise files (including dotfiles),
substitutes the reference implementation into the scratch solution file,
and runs pytest without touching the working-tree files.

It also supports testing custom/failing reference implementations and
custom pytest arguments, reporting case counts and propagating non-zero
exit codes upon failure or zero-test runs.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional


def find_repo_root() -> Path:
    """Find the root directory of the repository."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists() or (current / "exercises").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def resolve_metadata_paths(exercise_dir: Path) -> Dict[str, Path]:
    """Resolve solution, test, and example paths from .meta/config.json."""
    config_file = exercise_dir / ".meta" / "config.json"
    if not config_file.is_file():
        raise FileNotFoundError(f"Missing exercise metadata: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    files_cfg = config.get("files", {})
    solutions = files_cfg.get("solution", [])
    tests = files_cfg.get("test", [])
    examples = files_cfg.get("example", [])

    if not solutions:
        raise ValueError(f"No solution file specified in {config_file}")
    if not tests:
        raise ValueError(f"No test file specified in {config_file}")
    if not examples:
        raise ValueError(f"No example file specified in {config_file}")

    return {
        "solution_rel": Path(solutions[0]),
        "test_rel": Path(tests[0]),
        "example_rel": Path(examples[0]),
        "solution_abs": exercise_dir / solutions[0],
        "test_abs": exercise_dir / tests[0],
        "example_abs": exercise_dir / examples[0],
    }


def parse_pytest_output(stdout: str, stderr: str) -> Dict[str, Any]:
    """Parse pytest verbose output to extract test counts and named case statuses."""
    combined = stdout + "\n" + stderr
    named_cases = {
        "test_single_hand_always_wins": "NOT_RUN",
        "test_highest_card_out_of_all_hands_wins": "NOT_RUN",
        "test_a_tie_has_multiple_winners": "NOT_RUN",
    }

    # Match lines like: poker_test.py::PokerTest::test_name PASSED [ 78%]
    case_pattern = re.compile(r"::(test_\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)", re.IGNORECASE)
    for match in case_pattern.finditer(combined):
        test_name, status = match.group(1), match.group(2).upper()
        if test_name in named_cases:
            named_cases[test_name] = status

    # Parse summary counts
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    deselected = 0

    passed_match = re.search(r"(\d+)\s+passed", combined)
    if passed_match:
        passed = int(passed_match.group(1))

    failed_match = re.search(r"(\d+)\s+failed", combined)
    if failed_match:
        failed = int(failed_match.group(1))

    errors_match = re.search(r"(\d+)\s+error", combined)
    if errors_match:
        errors = int(errors_match.group(1))

    skipped_match = re.search(r"(\d+)\s+skipped", combined)
    if skipped_match:
        skipped = int(skipped_match.group(1))

    deselected_match = re.search(r"(\d+)\s+deselected", combined)
    if deselected_match:
        deselected = int(deselected_match.group(1))

    total_executed = passed + failed + errors

    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "deselected": deselected,
        "total_executed": total_executed,
        "named_cases": named_cases,
    }


def run_isolated_tests(
    exercise_dir: Optional[Path] = None,
    pytest_args: Optional[List[str]] = None,
    override_reference_content: Optional[str] = None,
    override_reference_file: Optional[Path] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Execute pytest in an isolated temporary directory.

    Args:
        exercise_dir: Path to the poker exercise directory.
        pytest_args: Additional command line arguments to pass to pytest.
        override_reference_content: Optional code string to use as solution.
        override_reference_file: Optional file path to copy as solution.
        verbose: Whether to include verbose logging.

    Returns:
        Dictionary containing execution summary, return code, test counts,
        and named case statuses.
    """
    if exercise_dir is None:
        repo_root = find_repo_root()
        exercise_dir = repo_root / "exercises" / "practice" / "poker"

    paths = resolve_metadata_paths(exercise_dir)
    scratch_cleaned = False

    with tempfile.TemporaryDirectory(prefix="poker_scratch_") as temp_dir:
        scratch_path = Path(temp_dir)
        try:
            # Copy exercise directory including dotfiles (.meta/)
            shutil.copytree(exercise_dir, scratch_path, dirs_exist_ok=True)

            target_solution = scratch_path / paths["solution_rel"]

            # Substitute reference implementation into the scratch copy
            if override_reference_content is not None:
                target_solution.write_text(override_reference_content, encoding="utf-8")
            elif override_reference_file is not None:
                shutil.copyfile(override_reference_file, target_solution)
            else:
                shutil.copyfile(scratch_path / paths["example_rel"], target_solution)

            # Build pytest command
            cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
            if pytest_args:
                cmd.extend(pytest_args)

            # Run pytest inside the isolated scratch directory
            proc = subprocess.run(
                cmd,
                cwd=str(scratch_path),
                capture_output=True,
                text=True,
            )

            parsed = parse_pytest_output(proc.stdout, proc.stderr)
            child_returncode = proc.returncode

            # Evaluate success criteria:
            # 1. Total executed must be > 0 (fail on zero-test runs)
            # 2. Child returncode must be 0
            # 3. No failures or errors
            if parsed["total_executed"] == 0:
                success = False
                exit_code = child_returncode if child_returncode != 0 else 1
                failure_reason = "Zero tests were executed."
            elif child_returncode != 0 or parsed["failed"] > 0 or parsed["errors"] > 0:
                success = False
                exit_code = child_returncode if child_returncode != 0 else 1
                failure_reason = f"Test execution failed (child exit {child_returncode})."
            else:
                success = True
                exit_code = 0
                failure_reason = None

            result = {
                "success": success,
                "exit_code": exit_code,
                "child_returncode": child_returncode,
                "failure_reason": failure_reason,
                "total_executed": parsed["total_executed"],
                "passed": parsed["passed"],
                "failed": parsed["failed"],
                "errors": parsed["errors"],
                "skipped": parsed["skipped"],
                "deselected": parsed["deselected"],
                "named_cases": parsed["named_cases"],
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "scratch_dir_cleaned": True,
            }

        finally:
            scratch_cleaned = True

    result["scratch_dir_cleaned"] = scratch_cleaned
    return result


def main() -> None:
    """CLI entry point for isolated test runner."""
    parser = argparse.ArgumentParser(description="Isolated test runner for poker exercise.")
    parser.add_argument(
        "--exercise-dir",
        type=Path,
        default=None,
        help="Path to exercises/practice/poker (default: auto-detected)",
    )
    parser.add_argument(
        "--pytest-args",
        type=str,
        default="",
        help="Extra arguments to forward to pytest (e.g. --pytest-args='-k <expr>')",
    )
    parser.add_argument(
        "--override-ref-file",
        type=Path,
        default=None,
        help="Path to an alternative reference implementation file",
    )
    parser.add_argument(
        "--override-ref-content",
        type=str,
        default=None,
        help="String code to use as reference implementation",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print verbose execution details",
    )

    args = parser.parse_args()

    pytest_args_list = shlex.split(args.pytest_args) if args.pytest_args else []

    result = run_isolated_tests(
        exercise_dir=args.exercise_dir,
        pytest_args=pytest_args_list,
        override_reference_content=args.override_ref_content,
        override_reference_file=args.override_ref_file,
        verbose=args.verbose,
    )

    if args.json:
        # Output clean JSON without large stdout/stderr unless verbose
        json_output = {k: v for k, v in result.items() if k not in ("stdout", "stderr") or args.verbose}
        print(json.dumps(json_output, indent=2))
    else:
        status_label = "PASSED" if result["success"] else "FAILED"
        print(f"[*] Isolated Poker Test Runner: {status_label}")
        print(f"[*] Exit Code: {result['exit_code']} (child returncode: {result['child_returncode']})")
        print(f"[*] Executed: {result['total_executed']} | Passed: {result['passed']} | Failed: {result['failed']}")
        if result["deselected"]:
            print(f"[*] Deselected: {result['deselected']}")
        if result["failure_reason"]:
            print(f"[*] Failure Reason: {result['failure_reason']}")
        print("[*] Named Cases:")
        for name, status in result["named_cases"].items():
            print(f"    - {name}: {status}")

        if args.verbose or not result["success"]:
            if result["stdout"]:
                print("\n--- stdout ---")
                print(result["stdout"])
            if result["stderr"]:
                print("\n--- stderr ---")
                print(result["stderr"])

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
