#!/usr/bin/env python3
"""Run tree-building tests against the maintained example in an isolated copy."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
REPO_ROOT = TASK_DIR.parents[1]
EXERCISE_REL = Path("exercises/practice/tree-building")
EXPECTED_CANONICAL_CASES = 16
EXPECTED_EXCLUDED_CASES = 0
EXPECTED_EXECUTED_TESTS = 13
REVIEWED_CASES = {
    "761790a3-4c27-461a-b4e9-8bce8ccee5a1": "test_empty_list_input",
    "dcc89dc3-eb39-4f26-a3cd-964e607c95ff": "test_one_node",
    "dcdb80f0-e5da-43e1-8b8d-6f307be89c0e": "test_three_nodes_in_order",
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
    for case_id in REVIEWED_CASES:
        assert case_id in cases, f"reviewed UUID missing from TOML: {case_id}"
        assert cases[case_id].get("include") is not False, (
            f"reviewed UUID is excluded: {case_id}"
        )

    test_source = (exercise / test_name).read_text()
    test_methods = {
        node.name
        for node in ast.walk(ast.parse(test_source))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    }
    for case_id, method in REVIEWED_CASES.items():
        assert method in test_methods, f"{case_id} has no matching test method {method}"
    assert len(test_methods) == EXPECTED_EXECUTED_TESTS, (
        f"expected {EXPECTED_EXECUTED_TESTS} test methods, found {len(test_methods)}"
    )

    inputs = {
        "exercise": EXERCISE_REL.as_posix(),
        "config": (EXERCISE_REL / ".meta/config.json").as_posix(),
        "solution_file_from_config": solution_name,
        "test_file_from_config": test_name,
        "example_file_from_config": example_rel.as_posix(),
        "reference_copy_target": solution_name,
        "canonical_entries": canonical_count,
        "excluded_entries": excluded_count,
        "expected_test_methods": EXPECTED_EXECUTED_TESTS,
        "reviewed_uuid_to_test": REVIEWED_CASES,
        "learner_solution_sha256_before": learner_hash_before,
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")

    example = exercise / example_rel
    assert example.is_file(), f"configured example file does not exist: {example}"
    with tempfile.TemporaryDirectory(prefix="tree-building-reference-") as tmp:
        scratch_exercise = Path(tmp) / EXERCISE_REL
        shutil.copytree(exercise, scratch_exercise)
        shutil.copy2(example, scratch_exercise / solution_name)

        command = [sys.executable, "-m", "pytest", "-q"]
        child = subprocess.run(
            command,
            cwd=scratch_exercise,
            text=True,
            capture_output=True,
            check=False,
        )
        output = child.stdout + child.stderr
        (TASK_DIR / "pytest-output.txt").write_text(output)
        matches = re.findall(r"\b(\d+) passed\b", output)
        executed = int(matches[-1]) if matches else 0
        learner_hash_after = sha256(source_solution)
        assert learner_hash_after == learner_hash_before, "learner solution changed during check"

        failures = []
        if child.returncode != 0:
            failures.append(f"pytest child exited with status {child.returncode}")
        if executed == 0:
            failures.append("pytest reported zero passed tests or no tests ran")
        if executed != EXPECTED_EXECUTED_TESTS:
            failures.append(
                f"expected {EXPECTED_EXECUTED_TESTS} executed tests, pytest reported {executed}"
            )

        results = {
            "command": command,
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
            print(output, file=sys.stderr, end="")
            return 1
        print(
            f"PASS: {executed} tests executed; {canonical_count} canonical entries, "
            f"{excluded_count} exclusions; learner solution unchanged."
        )
        print(output, end="")
        return 0


def main() -> int:
    versions = [
        subprocess.run([sys.executable, "--version"], text=True, capture_output=True),
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            text=True,
            capture_output=True,
            check=False,
        ),
    ]
    version_text = "\n".join((item.stdout + item.stderr).strip() for item in versions)
    (TASK_DIR / "tool-versions.txt").write_text(version_text + "\n")
    if versions[1].returncode:
        print("pytest is required; install it using docs/TESTS.md", file=sys.stderr)
        print(versions[1].stderr, file=sys.stderr, end="")
        return 1
    try:
        return run()
    except (AssertionError, OSError, KeyError, ValueError) as error:
        failure = {
            "status": "failed",
            "failures": [str(error)],
        }
        (TASK_DIR / "results.json").write_text(json.dumps(failure, indent=2) + "\n")
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
