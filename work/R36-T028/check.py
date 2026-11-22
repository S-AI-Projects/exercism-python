#!/usr/bin/env python3
"""
Automated verification check for Task R36-T028:
Verify exercises/practice/luhn metadata and test suite.

Requirements:
1. Dynamically resolve solution/test/example paths from exercises/practice/luhn/.meta/config.json.
2. Verify learner solution stub in the working tree is strictly unsolved ('pass').
3. Run the metadata checker (tools/course_checks/r36-t028.py) to assert that:
   - Real config passes.
   - All three deliberately invalid metadata fixtures (missing reference,
     missing test, path traversal) fail for their intended reasons.
4. Copy exercise (including dotfiles) to a temporary scratch directory, substitute
   the reference as the solution file, and run:
   python3 -m pytest -q
   python3 -m pytest -v
5. Verify child return codes (0), test counts (23), and that all test cases pass
   (including named baseline cases:
    test_single_digit_strings_can_not_be_valid,
    test_a_single_zero_is_invalid,
    test_a_simple_valid_sin_that_remains_valid_if_reversed).
6. Verify docs/maintenance/luhn.md exists and documents file roles and discovery mechanism.
7. Save evidence to work/R36-T028/results.json and results.txt.
8. Exit non-zero on any failure.
"""

from __future__ import annotations

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
    "test_single_digit_strings_can_not_be_valid",
    "test_a_single_zero_is_invalid",
    "test_a_simple_valid_sin_that_remains_valid_if_reversed",
    "test_a_simple_valid_sin_that_becomes_invalid_if_reversed",
    "test_a_valid_canadian_sin",
    "test_invalid_canadian_sin",
    "test_invalid_credit_card",
    "test_invalid_long_number_with_an_even_remainder",
    "test_invalid_long_number_with_a_remainder_divisible_by_5",
    "test_valid_number_with_an_even_number_of_digits",
    "test_valid_number_with_an_odd_number_of_spaces",
    "test_valid_strings_with_a_non_digit_added_at_the_end_become_invalid",
    "test_valid_strings_with_punctuation_included_become_invalid",
    "test_valid_strings_with_symbols_included_become_invalid",
    "test_single_zero_with_space_is_invalid",
    "test_more_than_a_single_zero_is_valid",
    "test_input_digit_9_is_correctly_converted_to_output_digit_9",
    "test_very_long_input_is_valid",
    "test_valid_luhn_with_an_odd_number_of_digits_and_non_zero_first_digit",
    "test_using_ascii_value_for_non_doubled_non_digit_isn_t_allowed",
    "test_using_ascii_value_for_doubled_non_digit_isn_t_allowed",
    "test_non_numeric_non_space_char_in_the_middle_with_a_sum_that_s_divisible_by_10_isn_t_allowed",
    "test_is_valid_can_be_called_repeatedly",
]

BASELINE_CASES = [
    "test_single_digit_strings_can_not_be_valid",
    "test_a_single_zero_is_invalid",
    "test_a_simple_valid_sin_that_remains_valid_if_reversed",
]


def main() -> int:
    print("[*] Starting automated check for Task R36-T028 (luhn)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/luhn")
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
    maintenance_doc = repo_root / "docs" / "maintenance" / "luhn.md"
    checker_tool = repo_root / "tools" / "course_checks" / "r36-t028.py"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner solution stub in working tree is strictly unsolved
    assert working_solution_file.is_file(), f"Solution file missing at {working_solution_file}"
    stub_content = working_solution_file.read_text(encoding="utf-8")
    is_stub_unsolved = "pass" in stub_content and "checksum" not in stub_content and "replace" not in stub_content
    assert is_stub_unsolved, "Learner solution stub luhn.py has been modified or solved!"
    print("[+] Verified learner solution stub in working tree is strictly unsolved.")

    # 3. Verify maintenance documentation
    assert maintenance_doc.is_file(), f"Maintenance document missing at {maintenance_doc}"
    maint_text = maintenance_doc.read_text(encoding="utf-8")
    assert "File-Role Map" in maint_text and "Discovery Mechanism" in maint_text, "Missing sections in luhn.md"
    assert "luhn.py" in maint_text and "luhn_test.py" in maint_text and ".meta/example.py" in maint_text
    print("[+] Verified maintenance document docs/maintenance/luhn.md.")

    # 4. Run metadata path checker tools/course_checks/r36-t028.py via subprocess
    assert checker_tool.is_file(), f"Checker tool missing at {checker_tool}"
    checker_proc = subprocess.run(
        [sys.executable, str(checker_tool)],
        capture_output=True,
        text=True,
    )
    print(f"[*] Metadata checker output:\n{checker_proc.stdout.strip()}")
    assert checker_proc.returncode == 0, f"Metadata checker failed with exit code {checker_proc.returncode}: {checker_proc.stderr}"
    print("[+] Metadata checker passed (real config valid, all 3 invalid fixtures rejected).")

    # Import and run checker module for structured data
    import importlib.util
    spec = importlib.util.spec_from_file_location("r36_t028_checker", checker_tool)
    assert spec is not None and spec.loader is not None, f"Cannot load checker module from {checker_tool}"
    r36_t028_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r36_t028_mod)
    fixture_results = r36_t028_mod.run_checks()

    # 5. Scratch copy test execution with pytest
    test_case_statuses = {}
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = Path(tmp_dir) / "luhn"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        # Substitute reference into solution filename in scratch copy
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

        # Run pytest -v
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, f"Pytest -v failed: {proc_v.stderr}"
        stdout_v = proc_v.stdout

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

        match_count = re.search(r"(\d+) passed", stdout_q)
        assert match_count is not None, f"Could not parse test count from: {stdout_q}"
        total_passed = int(match_count.group(1))
        assert total_passed == 23, f"Expected 23 passing tests, got {total_passed}"
        print(f"[+] All {total_passed} tests passed successfully in isolated scratch run.")

    # 6. Verify working tree learner stub remains strictly unchanged
    stub_content_after = working_solution_file.read_text(encoding="utf-8")
    assert stub_content == stub_content_after, "Working tree stub was modified during check execution!"
    print("[+] Confirmed working tree learner stub remained untouched.")

    # 7. Record results in work/R36-T028/results.json and results.txt
    results_record = {
        "task_id": "R36-T028",
        "exercise": "exercises/practice/luhn",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "maintenance_doc": str(maintenance_doc.relative_to(repo_root)),
            "checker_tool": str(checker_tool.relative_to(repo_root)),
            "canonical_cases": CANONICAL_CASES,
            "baseline_cases": BASELINE_CASES,
        },
        "metadata_checker_results": fixture_results,
        "counts": {
            "total_test_cases": len(CANONICAL_CASES),
            "executed_cases": total_passed,
            "passed_cases": total_passed,
            "failed_cases": 0,
        },
        "test_statuses": test_case_statuses,
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "real_config_passed": {
                "expected": True,
                "actual": fixture_results["real_config_status"]["valid"],
                "status": "PASS",
            },
            "fixture_missing_reference_rejected": {
                "expected": True,
                "actual": fixture_results["fixtures"]["missing_reference"]["rejected"],
                "status": "PASS",
            },
            "fixture_missing_test_rejected": {
                "expected": True,
                "actual": fixture_results["fixtures"]["missing_test"]["rejected"],
                "status": "PASS",
            },
            "fixture_path_traversal_rejected": {
                "expected": True,
                "actual": fixture_results["fixtures"]["path_traversal"]["rejected"],
                "status": "PASS",
            },
            "child_return_code": {
                "expected": 0,
                "actual": child_returncode,
                "status": "PASS",
            },
            "executed_tests_count": {
                "expected": 23,
                "actual": total_passed,
                "status": "PASS",
            },
            "baseline_cases_passed": {
                "expected": {c: "PASSED" for c in BASELINE_CASES},
                "actual": {c: test_case_statuses[c] for c in BASELINE_CASES},
                "status": "PASS",
            },
            "working_tree_learner_stub_untouched": {
                "expected": True,
                "actual": stub_content == stub_content_after,
                "status": "PASS",
            },
        },
        "summary": "Verified all 23 test cases pass against reference in scratch environment; verified real config passes and all 3 invalid metadata fixtures fail for their intended reasons. Learner stub remains strictly unsolved.",
    }

    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {results_json_path}")

    results_txt_path = work_dir / "results.txt"
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T028 Automated Check & Metadata Verification Report\n")
        f.write("=" * 65 + "\n\n")
        f.write("Exercise: exercises/practice/luhn\n")
        f.write("Tool Versions:\n")
        f.write(f"  Python: {py_version.splitlines()[0]}\n")
        f.write(f"  Pytest: {pytest_version}\n")
        f.write(f"  Platform: {platform_info}\n\n")
        f.write("Metadata Configuration & Fixture Verification (tools/course_checks/r36-t028.py):\n")
        f.write(f"  - Real metadata config: {'VALID (PASS)' if fixture_results['real_config_status']['valid'] else 'INVALID'}\n")
        f.write(f"  - Fixture 1 (Missing Reference): {'REJECTED (PASS)' if fixture_results['fixtures']['missing_reference']['rejected'] else 'UNEXPECTED PASS'}\n")
        f.write(f"      Error: {fixture_results['fixtures']['missing_reference']['error_message']}\n")
        f.write(f"  - Fixture 2 (Missing Test): {'REJECTED (PASS)' if fixture_results['fixtures']['missing_test']['rejected'] else 'UNEXPECTED PASS'}\n")
        f.write(f"      Error: {fixture_results['fixtures']['missing_test']['error_message']}\n")
        f.write(f"  - Fixture 3 (Path Traversal): {'REJECTED (PASS)' if fixture_results['fixtures']['path_traversal']['rejected'] else 'UNEXPECTED PASS'}\n")
        f.write(f"      Error: {fixture_results['fixtures']['path_traversal']['error_message']}\n\n")
        f.write("Pytest Execution Results (in isolated scratch directory):\n")
        f.write(f"  Child exit code: {child_returncode}\n")
        f.write(f"  Executed cases: {total_passed}/23 passed\n")
        f.write(f"  Output summary: {stdout_q}\n\n")
        f.write("Canonical & Track Test Cases Status:\n")
        for c in CANONICAL_CASES:
            baseline_tag = " (Baseline)" if c in BASELINE_CASES else ""
            f.write(f"  - {c}{baseline_tag}: {test_case_statuses.get(c)}\n")
        f.write("\nLearner Solution Stub Verification:\n")
        f.write(f"  Path: {solution_rel}\n")
        f.write("  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks and metadata fixture tests passed successfully.\n")
    print(f"[+] Saved text summary to {results_txt_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
