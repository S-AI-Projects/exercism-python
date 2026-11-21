#!/usr/bin/env python3
"""Run complex-numbers checks and verify contract decision table in isolated environment."""

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
EXERCISE_REL = Path("exercises/practice/complex-numbers")
HINTS_FILE = REPO_ROOT / EXERCISE_REL / ".docs/hints.md"
EXPECTED_EXECUTED_TESTS = 43
NAMED_CASES = [
    "test_real_part_of_a_purely_real_number",
    "test_real_part_of_a_purely_imaginary_number",
    "test_real_part_of_a_number_with_real_and_imaginary_part",
]

DECISION_TABLE_ENTRIES = [
    {"name": "test_real_part_of_a_purely_real_number", "input": "(1, 0)", "expected": "1"},
    {"name": "test_real_part_of_a_purely_imaginary_number", "input": "(0, 1)", "expected": "0"},
    {"name": "test_real_part_of_a_number_with_real_and_imaginary_part", "input": "(1, 2)", "expected": "1"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    exercise = REPO_ROOT / EXERCISE_REL
    config_path = exercise / ".meta/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_rel = Path(config["files"]["example"][0])

    learner_file = exercise / solution_name
    learner_hash_before = sha256(learner_file)

    # 1. Verify hints.md decision table
    if not HINTS_FILE.exists():
        print(f"Assertion failed: hints file missing at {HINTS_FILE}")
        sys.exit(1)

    hints_content = HINTS_FILE.read_text(encoding="utf-8")
    for entry in DECISION_TABLE_ENTRIES:
        if entry["name"] not in hints_content:
            print(f"Assertion failed: test case {entry['name']} missing from hints decision table")
            sys.exit(1)
        if entry["input"] not in hints_content or entry["expected"] not in hints_content:
            print(f"Assertion failed: input/expected value missing for {entry['name']} in hints table")
            sys.exit(1)

    # 2. Run pytest in isolated tempdir with reference implementation
    with tempfile.TemporaryDirectory(prefix="complex_numbers_check_") as tmpdir:
        tmp_path = Path(tmpdir)
        for item in exercise.iterdir():
            dest = tmp_path / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)

        # Replace learner stub with reference implementation
        shutil.copy2(exercise / example_rel, tmp_path / solution_name)

        python_bin = sys.executable
        cmd = [python_bin, "-m", "pytest", str(tmp_path / test_name), "-v"]
        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0:
            print(f"Assertion failed: reference tests failed with code {res.returncode}:\n{res.stdout}")
            sys.exit(1)

        pytest_output = res.stdout

        # Check all named cases
        for case in NAMED_CASES:
            if case not in pytest_output:
                print(f"Assertion failed: named case {case} not found in pytest output!")
                sys.exit(1)

        match = re.search(r"(\d+)\s+passed", pytest_output)
        if not match:
            print("Assertion failed: failed to parse test count!")
            sys.exit(1)

        passed_count = int(match.group(1))
        if passed_count != EXPECTED_EXECUTED_TESTS:
            print(f"Assertion failed: expected {EXPECTED_EXECUTED_TESTS} tests, got {passed_count}")
            sys.exit(1)

    # 3. Verify learner file is untouched
    learner_hash_after = sha256(learner_file)
    if learner_hash_before != learner_hash_after:
        print("Assertion failed: learner stub file was altered!")
        sys.exit(1)

    # 4. Generate task evidence artifacts
    TASK_DIR.mkdir(parents=True, exist_ok=True)

    inputs_data = {
        "task_id": "R36-T010",
        "exercise": "complex-numbers",
        "hints_file": "exercises/practice/complex-numbers/.docs/hints.md",
        "named_cases": NAMED_CASES,
        "decision_table": DECISION_TABLE_ENTRIES,
        "expected_test_count": EXPECTED_EXECUTED_TESTS,
        "learner_file": str(EXERCISE_REL / solution_name),
        "learner_sha256": learner_hash_before
    }
    (TASK_DIR / "inputs.json").write_text(json.dumps(inputs_data, indent=2), encoding="utf-8")

    results_data = {
        "task_id": "R36-T010",
        "status": "PASS",
        "tests_executed": passed_count,
        "tests_passed": passed_count,
        "named_cases_verified": True,
        "decision_table_verified": True,
        "learner_file_unmodified": True
    }
    (TASK_DIR / "results.json").write_text(json.dumps(results_data, indent=2), encoding="utf-8")

    (TASK_DIR / "pytest-output.txt").write_text(pytest_output, encoding="utf-8")

    v_proc = subprocess.run([python_bin, "--version"], capture_output=True, text=True)
    py_ver = v_proc.stdout.strip()
    try:
        pt_proc = subprocess.run([python_bin, "-m", "pytest", "--version"], capture_output=True, text=True)
        pt_ver = pt_proc.stdout.strip()
    except Exception:
        pt_ver = "pytest available"

    versions_txt = f"{py_ver}\n{pt_ver}\n"
    (TASK_DIR / "tool-versions.txt").write_text(versions_txt, encoding="utf-8")

    print(f"PASS: All {passed_count} tests executed and verified against decision table.")


if __name__ == "__main__":
    main()
