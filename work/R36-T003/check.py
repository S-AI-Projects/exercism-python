#!/usr/bin/env python3
"""Run pov test suite against the reference and verify mutant rejection in a scratch copy."""

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
EXERCISE_REL = Path("exercises/practice/pov")
EXPECTED_EXECUTED_TESTS = 15
REJECTING_CASE = "test_can_reroot_a_tree_with_a_parent_and_one_sibling"


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
        "rejecting_test_case": REJECTING_CASE,
        "mutation": {
            "target": "stack.append(child.add(tree.remove(child.label)))",
            "replacement": "stack.append(child.add(tree))",
        },
        "learner_solution_sha256_before": learner_hash_before,
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")

    failures = []
    # Test 1: Original reference passes all tests
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
        orig_output = (child.stdout + child.stderr).strip()
        (TASK_DIR / "pytest-output.txt").write_text(orig_output + "\n")

        if child.returncode != 0:
            failures.append(f"original reference failed pytest ({child.returncode})")

        passed_match = re.search(r"(\d+) passed", orig_output)
        executed = int(passed_match.group(1)) if passed_match else 0
        if executed != EXPECTED_EXECUTED_TESTS:
            failures.append(
                f"expected {EXPECTED_EXECUTED_TESTS} passed tests, found {executed}"
            )

    # Test 2: Mutant fails the rejecting case
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir) / "exercise_mutant"
        shutil.copytree(exercise, scratch)
        example_code = (exercise / example_rel).read_text()
        mutated_code = example_code.replace(
            "stack.append(child.add(tree.remove(child.label)))",
            "stack.append(child.add(tree))",
        )
        assert mutated_code != example_code, "failed to apply mutation"
        (scratch / solution_name).write_text(mutated_code)

        mutant_proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-k", REJECTING_CASE],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        if mutant_proc.returncode == 0:
            failures.append(f"mutant unexpectedly passed {REJECTING_CASE}")

    learner_hash_after = sha256(source_solution)
    if learner_hash_before != learner_hash_after:
        failures.append("learner solution hash changed during execution")

    results = {
        "command": pytest_cmd,
        "clean_reference_returncode": child.returncode,
        "mutant_returncode": mutant_proc.returncode,
        "tests_executed_actual": executed,
        "rejecting_test_case": REJECTING_CASE,
        "mutant_rejected": mutant_proc.returncode != 0,
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
        f"PASS: {executed} tests passed on reference; mutant correctly rejected by "
        f"{REJECTING_CASE}; learner solution unchanged."
    )
    print(orig_output)
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
