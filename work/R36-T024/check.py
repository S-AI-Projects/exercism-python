#!/usr/bin/env python3
"""
Automated verification check for Task R36-T024:
Clarify spiral_matrix in the spiral-matrix reference implementation.

Requirements:
1. Dynamically resolve solution/test/example paths from exercises/practice/spiral-matrix/.meta/config.json.
2. Use Python subprocess and temporary directory isolation.
3. Verify learner solution stub in the working tree is strictly unsolved ('pass').
4. Verify before-and-after outputs across all canonical cases agree identically:
   - test_empty_spiral (size 0)
   - test_trivial_spiral (size 1)
   - test_spiral_of_size_2 (size 2)
   - test_spiral_of_size_3 (size 3)
   - test_spiral_of_size_4 (size 4)
   - test_spiral_of_size_5 (size 5)
5. Copy exercise (including dotfiles) to a temporary scratch directory, substitute
   the refactored reference as the solution file, and run:
   python3 -m pytest -q
   python3 -m pytest -v
6. Verify child return codes (0), test counts (6), and all test cases pass.
7. Save verification evidence to work/R36-T024/results.json and results.txt.
8. Exit non-zero on any failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CANONICAL_CASES = [
    "test_empty_spiral",
    "test_trivial_spiral",
    "test_spiral_of_size_2",
    "test_spiral_of_size_3",
    "test_spiral_of_size_4",
    "test_spiral_of_size_5",
]

BASELINE_CASES = [
    "test_empty_spiral",
    "test_trivial_spiral",
    "test_spiral_of_size_2",
]


def load_module_from_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def original_spiral_matrix(size):
    """Historical original reference implementation before readability refactoring."""
    matrix = [[0] * size for _ in range(size)]
    idx = 0
    jdx = -1
    element = 1

    digital = [0, 1, 0, -1]
    disco = [1, 0, -1, 0]

    for edx in range(2 * size - 1):
        for _ in range((2 * size - edx) // 2):
            idx += digital[edx % 4]
            jdx += disco[edx % 4]
            matrix[idx][jdx] = element
            element += 1
    return matrix


def main() -> int:
    print("[*] Starting automated check for Task R36-T024 (spiral-matrix)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/spiral-matrix")
    exercise_dir = repo_root / exercise_rel

    print(f"[*] Repository root: {repo_root}")
    print(f"[*] Exercise directory: {exercise_dir}")

    # Tool versions
    py_version = sys.version
    pytest_proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    pytest_version = pytest_proc.stdout.strip() or pytest_proc.stderr.strip()
    platform_info = platform.platform()

    tool_versions = {
        "python": py_version,
        "pytest": pytest_version,
        "platform": platform_info,
    }
    print(f"[*] Python: {py_version.splitlines()[0]}")
    print(f"[*] Pytest: {pytest_version}")

    # 1. Resolve paths dynamically from .meta/config.json
    config_file = exercise_dir / ".meta" / "config.json"
    assert config_file.is_file(), f"config.json missing at {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    working_solution_file = exercise_dir / solution_rel
    working_test_file = exercise_dir / test_rel
    working_example_file = exercise_dir / example_rel

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner solution stub in working tree is unsolved
    assert working_solution_file.is_file(), f"Solution file not found: {working_solution_file}"
    stub_content = working_solution_file.read_text(encoding="utf-8")
    is_stub_unsolved = "pass" in stub_content and "for " not in stub_content and "return " not in stub_content
    assert is_stub_unsolved, "Learner solution stub spiral_matrix.py has been modified or solved!"
    print("[+] Verified learner solution stub in working tree is strictly unsolved.")

    # 3. Verify before-and-after functional parity across all canonical inputs
    refactored_module = load_module_from_file("spiral_matrix_refactored", working_example_file)
    parity_results = {}
    for size in range(6):
        before_out = original_spiral_matrix(size)
        after_out = refactored_module.spiral_matrix(size)
        assert before_out == after_out, f"Output mismatch for size {size}: before={before_out}, after={after_out}"
        parity_results[f"size_{size}"] = {
            "size": size,
            "output": after_out,
            "match": True,
        }
    print("[+] Verified before-and-after parity for sizes 0..5 (all canonical cases identical).")

    # 4. Verify refactored reference implementation readability features
    example_text = working_example_file.read_text(encoding="utf-8")
    required_identifiers = ["row_deltas", "col_deltas", "row", "col", "segment_steps"]
    for identifier in required_identifiers:
        assert identifier in example_text, f"Expected identifier '{identifier}' missing in {working_example_file}"
    assert "invariant" in example_text.lower(), "Expected invariant comment missing in example.py"
    print("[+] Verified all readability improvements, identifiers, and invariant explanation exist.")

    # 5. Scratch copy execution with pytest in temporary directory
    test_case_statuses = {}
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = Path(tmp_dir) / "spiral-matrix"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        # Substitute refactored reference into scratch copy solution file
        scratch_solution = scratch_exercise / solution_rel
        scratch_example = scratch_exercise / example_rel
        shutil.copyfile(scratch_example, scratch_solution)

        # Run pytest -q
        proc_q = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
        )
        child_returncode = proc_q.returncode
        stdout_q = proc_q.stdout.strip()
        stderr_q = proc_q.stderr.strip()

        print(f"[*] Pytest -q returncode: {child_returncode}")
        print(f"[*] Pytest -q output: {stdout_q}")
        assert child_returncode == 0, f"Pytest -q failed with exit code {child_returncode}: {stderr_q}"

        # Run pytest -v for granular reporting
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, f"Pytest -v failed: {proc_v.stderr}"
        stdout_v = proc_v.stdout

        # Parse test outcomes
        for case in CANONICAL_CASES:
            case_pattern = rf"{case}\s+(PASSED|FAILED|ERROR)"
            match = re.search(case_pattern, stdout_v)
            if match:
                test_case_statuses[case] = match.group(1)
            elif f"{case} PASSED" in stdout_v:
                test_case_statuses[case] = "PASSED"
            else:
                test_case_statuses[case] = "NOT_FOUND"

        for case in CANONICAL_CASES:
            assert test_case_statuses.get(case) == "PASSED", f"Case {case} did not pass: {test_case_statuses.get(case)}"

        # Verify total test count
        summary_match = re.search(r"(\d+) passed", stdout_q)
        assert summary_match is not None, f"Could not parse test count from: {stdout_q}"
        total_passed = int(summary_match.group(1))
        assert total_passed == 6, f"Expected 6 passing tests, got {total_passed}"
        print(f"[+] All {total_passed} tests passed successfully in isolated scratch run.")

    # 6. Verify working tree learner stub remains unchanged after test execution
    stub_content_after = working_solution_file.read_text(encoding="utf-8")
    assert stub_content == stub_content_after, "Learner solution stub was modified during check execution!"
    print("[+] Confirmed working tree learner stub remained untouched.")

    # 7. Record results in work/R36-T024/results.json and results.txt
    results_record = {
        "task_id": "R36-T024",
        "exercise": "exercises/practice/spiral-matrix",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "canonical_cases": CANONICAL_CASES,
            "baseline_cases": BASELINE_CASES,
            "refactored_identifiers": required_identifiers,
            "refactor_description": (
                "Replaced cryptic variable names (digital, disco, idx, jdx, edx) with descriptive "
                "identifiers (row_deltas, col_deltas, row, col, segment_index, segment_steps) "
                "and documented the step-length invariant (2*size - segment_index) // 2."
            ),
        },
        "counts": {
            "total_canonical_cases": len(CANONICAL_CASES),
            "executed_cases": total_passed,
            "passed_cases": total_passed,
            "failed_cases": 0,
        },
        "test_statuses": test_case_statuses,
        "parity_verification": parity_results,
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "child_return_code": {
                "expected": 0,
                "actual": child_returncode,
                "status": "PASS",
            },
            "executed_tests_count": {
                "expected": 6,
                "actual": total_passed,
                "status": "PASS",
            },
            "baseline_cases_passed": {
                "expected": {c: "PASSED" for c in BASELINE_CASES},
                "actual": {c: test_case_statuses[c] for c in BASELINE_CASES},
                "status": "PASS",
            },
            "canonical_cases_passed": {
                "expected": {c: "PASSED" for c in CANONICAL_CASES},
                "actual": test_case_statuses,
                "status": "PASS",
            },
            "before_after_parity": {
                "expected": True,
                "actual": all(v["match"] for v in parity_results.values()),
                "status": "PASS",
            },
            "working_tree_learner_stub_untouched": {
                "expected": True,
                "actual": stub_content == stub_content_after,
                "status": "PASS",
            },
        },
        "summary": "Refactored reference implementation passed all 6 canonical test cases with 100% parity against original logic. Learner stub remains strictly unsolved.",
    }

    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {results_json_path}")

    results_txt_path = work_dir / "results.txt"
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T024 Automated Check Verification Report\n")
        f.write("=" * 55 + "\n\n")
        f.write(f"Exercise: exercises/practice/spiral-matrix\n")
        f.write(f"Tool Versions:\n")
        f.write(f"  Python: {py_version.splitlines()[0]}\n")
        f.write(f"  Pytest: {pytest_version}\n")
        f.write(f"  Platform: {platform_info}\n\n")
        f.write(f"Pytest Execution Results (in isolated scratch directory):\n")
        f.write(f"  Child exit code: {child_returncode}\n")
        f.write(f"  Executed cases: {total_passed}/6 passed\n")
        f.write(f"  Output summary: {stdout_q}\n\n")
        f.write("Canonical Test Cases Status:\n")
        for c in CANONICAL_CASES:
            baseline_tag = " (Baseline)" if c in BASELINE_CASES else ""
            f.write(f"  - {c}{baseline_tag}: {test_case_statuses.get(c)}\n")
        f.write("\nBefore vs. After Parity Check (sizes 0 through 5):\n")
        for k, v in parity_results.items():
            f.write(f"  - size {v['size']}: MATCH (output={v['output']})\n")
        f.write("\nLearner Solution Stub Verification:\n")
        f.write(f"  Path: {solution_rel}\n")
        f.write(f"  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks passed successfully.\n")
    print(f"[+] Saved text summary to {results_txt_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
