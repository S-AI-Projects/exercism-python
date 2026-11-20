#!/usr/bin/env python3
"""Compare reference and alternative implementations of Sieve of Eratosthenes in an isolated scratch copy."""

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
EXERCISE_REL = Path("exercises/practice/sieve")
EXPECTED_EXECUTED_TESTS = 5
NAMED_CASES = [
    "test_no_primes_under_two",
    "test_find_first_prime",
    "test_find_primes_up_to_10",
]

ALTERNATIVE_CODE = """
def primes(limit):
    if limit < 2:
        return []
    composites = set()
    result = []
    for candidate in range(2, limit + 1):
        if candidate not in composites:
            result.append(candidate)
            composites.update(range(candidate * candidate, limit + 1, candidate))
    return result
"""


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
        "approaches": [
            "Reference: Boolean array direct indexing",
            "Alternative: Set-based composite filtering",
        ],
        "learner_solution_sha256_before": learner_hash_before,
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")

    failures = []
    pytest_cmd = [sys.executable, "-m", "pytest", "-q"]

    # 1. Test reference implementation
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir) / "exercise_ref"
        shutil.copytree(exercise, scratch)
        shutil.copy2(exercise / example_rel, scratch / solution_name)

        child_ref = subprocess.run(
            pytest_cmd,
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        ref_output = (child_ref.stdout + child_ref.stderr).strip()
        (TASK_DIR / "pytest-output.txt").write_text(ref_output + "\n")

        if child_ref.returncode != 0:
            failures.append(f"reference failed pytest ({child_ref.returncode})")

        passed_match = re.search(r"(\d+) passed", ref_output)
        executed_ref = int(passed_match.group(1)) if passed_match else 0
        if executed_ref != EXPECTED_EXECUTED_TESTS:
            failures.append(f"reference: expected {EXPECTED_EXECUTED_TESTS} tests, got {executed_ref}")

    # 2. Test alternative implementation
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir) / "exercise_alt"
        shutil.copytree(exercise, scratch)
        (scratch / solution_name).write_text(ALTERNATIVE_CODE)

        child_alt = subprocess.run(
            pytest_cmd,
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        alt_output = (child_alt.stdout + child_alt.stderr).strip()

        if child_alt.returncode != 0:
            failures.append(f"alternative failed pytest ({child_alt.returncode})")

        passed_match_alt = re.search(r"(\d+) passed", alt_output)
        executed_alt = int(passed_match_alt.group(1)) if passed_match_alt else 0
        if executed_alt != EXPECTED_EXECUTED_TESTS:
            failures.append(f"alternative: expected {EXPECTED_EXECUTED_TESTS} tests, got {executed_alt}")

    learner_hash_after = sha256(source_solution)
    if learner_hash_before != learner_hash_after:
        failures.append("learner solution hash changed during run")

    results = {
        "command": pytest_cmd,
        "reference_returncode": child_ref.returncode,
        "alternative_returncode": child_alt.returncode,
        "test_methods_expected": EXPECTED_EXECUTED_TESTS,
        "reference_tests_executed": executed_ref,
        "alternative_tests_executed": executed_alt,
        "both_passed": child_ref.returncode == 0 and child_alt.returncode == 0,
        "learner_solution_sha256_before": learner_hash_before,
        "learner_solution_sha256_after": learner_hash_after,
        "failures": failures,
        "status": "passed" if not failures else "failed",
    }
    (TASK_DIR / "results.json").write_text(json.dumps(results, indent=2) + "\n")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1

    print(
        f"PASS: {executed_ref} tests executed; both reference and alternative approaches passed 100%; learner solution unchanged."
    )
    print(ref_output)
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
