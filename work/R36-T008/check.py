#!/usr/bin/env python3
"""Run crypto-square metadata validation and reference checks."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent
REPO_ROOT = TASK_DIR.parents[1]
EXERCISE_REL = Path("exercises/practice/crypto-square")
EXPECTED_EXECUTED_TESTS = 8
NAMED_CASES = [
    "test_empty_plaintext_results_in_an_empty_ciphertext",
    "test_normalization_results_in_empty_plaintext",
    "test_lowercase",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> int:
    exercise = REPO_ROOT / EXERCISE_REL
    config = json.loads((exercise / ".meta/config.json").read_text())
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_rel = Path(config["files"]["example"][0])
    source_solution = exercise / solution_name
    learner_hash_before = sha256(source_solution)

    inputs = {
        "exercise": str(EXERCISE_REL),
        "config": str(EXERCISE_REL / ".meta/config.json"),
        "solution_file_from_config": solution_name,
        "test_file_from_config": test_name,
        "example_file_from_config": str(example_rel),
        "expected_test_methods": EXPECTED_EXECUTED_TESTS,
        "named_cases": NAMED_CASES,
        "learner_solution_sha256_before": learner_hash_before,
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")

    # Run tool checker
    tool_proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/course_checks/r36-t008.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if tool_proc.returncode != 0:
        print(f"FAIL: tool checker failed:\n{tool_proc.stdout}{tool_proc.stderr}", file=sys.stderr)
        return 1

    failures = []
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir) / "exercise"
        shutil.copytree(exercise, scratch)
        shutil.copy2(exercise / example_rel, scratch / solution_name)

        pytest_cmd = [sys.executable, "-m", "pytest", "-q"]
        child = subprocess.run(
            pytest_cmd,
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        output = (child.stdout + child.stderr).strip()
        (TASK_DIR / "pytest-output.txt").write_text(output + "\n")

        learner_hash_after = sha256(source_solution)
        if learner_hash_before != learner_hash_after:
            failures.append("learner solution hash changed during run")
        if child.returncode != 0:
            failures.append(f"pytest exited non-zero ({child.returncode})")

        passed_match = re.search(r"(\d+) passed", output)
        executed = int(passed_match.group(1)) if passed_match else 0
        if executed == 0:
            failures.append("pytest reported zero passed tests or no tests ran")
        if executed != EXPECTED_EXECUTED_TESTS:
            failures.append(
                f"expected {EXPECTED_EXECUTED_TESTS} executed tests, pytest reported {executed}"
            )

        results = {
            "command": pytest_cmd,
            "child_returncode": child.returncode,
            "test_methods_expected": EXPECTED_EXECUTED_TESTS,
            "tests_executed_actual": executed,
            "tool_check_passed": tool_proc.returncode == 0,
            "invalid_fixtures_rejected": 3,
            "learner_solution_sha256_before": learner_hash_before,
            "learner_solution_sha256_after": learner_hash_after,
            "failures": failures,
            "status": "passed" if not failures else "failed",
        }
        (TASK_DIR / "results.json").write_text(json.dumps(results, indent=2) + "\n")

        if failures:
            for failure in failures:
                print(f"FAIL: {failure}", file=sys.stderr)
            print(output, file=sys.stderr)
            return 1

        print(
            f"PASS: {executed} tests executed; metadata and fixtures validated; learner solution unchanged."
        )
        print(output)
        return 0


def main() -> int:
    versions = [
        subprocess.run([sys.executable, "--version"], text=True, capture_output=True),
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            text=True,
            capture_output=True,
        ),
    ]
    version_text = "\n".join((item.stdout + item.stderr).strip() for item in versions)
    (TASK_DIR / "tool-versions.txt").write_text(version_text + "\n")
    try:
        return run()
    except Exception as error:
        failure = {
            "status": "failed",
            "failures": [str(error)],
        }
        (TASK_DIR / "results.json").write_text(json.dumps(failure, indent=2) + "\n")
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
