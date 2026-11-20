#!/usr/bin/env python3
"""Run palindrome-products tests against the maintained example in an isolated copy."""

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

try:
    import tomllib
except ImportError:
    import tomli as tomllib

TASK_DIR = Path(__file__).resolve().parent
REPO_ROOT = TASK_DIR.parents[1]
EXERCISE_REL = Path("exercises/practice/palindrome-products")
EXPECTED_CANONICAL_CASES = 13
EXPECTED_EXCLUDED_CASES = 0
EXPECTED_EXECUTED_TESTS = 13
REVIEWED_CASES = {
    "5cff78fe-cf02-459d-85c2-ce584679f887": "test_find_the_smallest_palindrome_from_single_digit_factors",
    "0853f82c-5fc4-44ae-be38-fadb2cced92d": "test_find_the_largest_palindrome_from_single_digit_factors",
    "66c3b496-bdec-4103-9129-3fcb5a9063e1": "test_find_the_smallest_palindrome_from_double_digit_factors",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run() -> int:
    exercise = REPO_ROOT / EXERCISE_REL
    config_path = exercise / ".meta/config.json"
    config = json.loads(config_path.read_text())
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_rel = Path(config["files"]["example"][0])
    source_solution = exercise / solution_name
    learner_hash_before = sha256(source_solution)

    cases = tomllib.loads((exercise / ".meta/tests.toml").read_text())
    canonical_count = len(cases)
    excluded_count = sum(case.get("include") is False for case in cases.values())
    assert canonical_count == EXPECTED_CANONICAL_CASES, (
        f"expected {EXPECTED_CANONICAL_CASES} canonical entries, found {canonical_count}"
    )
    assert excluded_count == EXPECTED_EXCLUDED_CASES, (
        f"expected {EXPECTED_EXCLUDED_CASES} excluded entries, found {excluded_count}"
    )

    inputs = {
        "exercise": str(EXERCISE_REL),
        "config": str(EXERCISE_REL / ".meta/config.json"),
        "solution_file_from_config": solution_name,
        "test_file_from_config": test_name,
        "example_file_from_config": str(example_rel),
        "reference_copy_target": solution_name,
        "canonical_entries": canonical_count,
        "excluded_entries": excluded_count,
        "expected_test_methods": EXPECTED_EXECUTED_TESTS,
        "reviewed_uuid_to_test": REVIEWED_CASES,
        "learner_solution_sha256_before": learner_hash_before,
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")

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
            "canonical_entries_before": canonical_count,
            "excluded_entries_before": excluded_count,
            "canonical_entries_after": canonical_count,
            "excluded_entries_after": excluded_count,
            "test_methods_expected": EXPECTED_EXECUTED_TESTS,
            "tests_executed_actual": executed,
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
            f"PASS: {executed} tests executed; {canonical_count} canonical entries, "
            f"{excluded_count} exclusions; learner solution unchanged."
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
