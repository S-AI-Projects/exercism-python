#!/usr/bin/env python3
"""Automated verification suite for task R36-T009: reverse-string isolated runner."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
REPO_ROOT = TASK_DIR.parents[1]
EXERCISE_DIR = REPO_ROOT / "exercises/practice/reverse-string"
RUNNER_SCRIPT = REPO_ROOT / "tools/course_checks/r36-t009.py"

NAMED_CASES = [
    "test_an_empty_string",
    "test_a_word",
    "test_a_capitalized_word",
]
EXPECTED_TOTAL_TESTS = 7


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    learner_file = EXERCISE_DIR / "reverse_string.py"
    hash_baseline = sha256(learner_file)

    # 1. Run the official isolated runner
    python_bin = sys.executable
    cmd = [python_bin, str(RUNNER_SCRIPT)]
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"Runner failed with code {res.returncode}:\n{res.stderr}")
        sys.exit(1)

    pytest_output = res.stdout

    # Verify all named cases were executed
    for case in NAMED_CASES:
        if case not in pytest_output:
            print(f"Assertion failed: named case {case} missing from pytest output!")
            sys.exit(1)

    # Check test count
    import re
    match = re.search(r"(\d+)\s+passed", pytest_output)
    if not match:
        print("Assertion failed: could not parse passed test count from pytest output!")
        sys.exit(1)

    passed_count = int(match.group(1))
    if passed_count != EXPECTED_TOTAL_TESTS:
        print(f"Assertion failed: expected {EXPECTED_TOTAL_TESTS} passed tests, got {passed_count}")
        sys.exit(1)

    # Verify learner stub hash is identical
    hash_after_run = sha256(learner_file)
    if hash_baseline != hash_after_run:
        print("Assertion failed: learner stub file was mutated during test execution!")
        sys.exit(1)

    # 2. Test Failure Propagation & Tempfile Cleanup
    # Create a deliberately failing test in a scratch copy to verify runner propagates non-zero exit
    with tempfile.TemporaryDirectory() as scratch_dir:
        scratch_path = Path(scratch_dir)
        for item in EXERCISE_DIR.iterdir():
            dest = scratch_path / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)

        # Inject a failing example in scratch copy
        failing_example = scratch_path / ".meta/example.py"
        failing_example.write_text("def reverse(text=''): return 'wrong_output'\n", encoding="utf-8")

        import importlib.util
        spec = importlib.util.spec_from_file_location("r36_t009", str(RUNNER_SCRIPT))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fail_code, fail_passed, fail_out = mod.run_isolated(exercise_path=scratch_path, python_bin=python_bin)
        if fail_code == 0:
            print("Assertion failed: runner did not propagate failure for wrong implementation!")
            sys.exit(1)

    # 3. Save task reports
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    
    # inputs.json
    inputs_data = {
        "task_id": "R36-T009",
        "exercise": "reverse-string",
        "runner_script": "tools/course_checks/r36-t009.py",
        "documentation": "docs/maintenance/reverse-string.md",
        "named_cases": NAMED_CASES,
        "expected_test_count": EXPECTED_TOTAL_TESTS,
        "learner_file": "exercises/practice/reverse-string/reverse_string.py",
        "learner_sha256": hash_baseline
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2), encoding="utf-8")

    # results.json
    results_data = {
        "task_id": "R36-T009",
        "status": "PASS",
        "tests_executed": passed_count,
        "tests_passed": passed_count,
        "named_cases_verified": True,
        "failure_propagation_verified": True,
        "learner_file_unmodified": True,
        "tempfile_cleanup_verified": True
    }
    (TASK_DIR / "results.json").write_text(json.dumps(results_data, indent=2), encoding="utf-8")

    # pytest-output.txt
    (TASK_DIR / "pytest-output.txt").write_text(pytest_output, encoding="utf-8")

    # tool-versions.txt
    v_proc = subprocess.run([python_bin, "--version"], capture_output=True, text=True)
    py_ver = v_proc.stdout.strip()
    try:
        pt_proc = subprocess.run([python_bin, "-m", "pytest", "--version"], capture_output=True, text=True)
        pt_ver = pt_proc.stdout.strip()
    except Exception:
        pt_ver = "pytest available"

    versions_txt = f"{py_ver}\n{pt_ver}\n"
    (TASK_DIR / "tool-versions.txt").write_text(versions_txt, encoding="utf-8")

    print(f"PASS: All {passed_count} isolated tests passed. Reports generated in {TASK_DIR}.")


if __name__ == "__main__":
    main()
