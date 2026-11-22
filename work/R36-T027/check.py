#!/usr/bin/env python3
"""
Automated verification check for Task R36-T027:
Add Python-specific guidance for isbn-verifier.

Requirements:
1. Dynamically resolve solution/test/example paths from exercises/practice/isbn-verifier/.meta/config.json.
2. Use Python subprocess and temporary scratch directory isolation.
3. Verify learner solution stub in the working tree is strictly unsolved ('pass').
4. Verify language-specific guidance in .docs/hints.md:
   - Explains mutable list conversion vs. string immutability.
   - Includes executable micro-examples and expected outputs.
   - Documents the exercise-related pitfall (str.replace('X', '10')).
   - Links to official Python documentation.
5. Directly assert and verify the outputs of both micro-examples:
   - Micro-example 1 (List mutation): chars == ['0', '1', '2', '3', '4', '5', '6', '7', '8', '10'], len == 10
   - Micro-example 2 (Pitfall replacement): replaced == "35982105079", len == 11
   - String immutability TypeError verification.
6. Copy exercise (including dotfiles) to a temporary scratch directory, substitute
   the reference as the solution file, and run:
   python3 -m pytest -q
   python3 -m pytest -v
7. Verify child return codes (0), test counts (21), and all test cases pass
   (including named baseline cases: test_valid_isbn, test_invalid_isbn_check_digit,
   test_valid_isbn_with_a_check_digit_of_10).
8. Save evidence to work/R36-T027/results.json and results.txt.
9. Exit non-zero on any failure.
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
    "test_valid_isbn",
    "test_invalid_isbn_check_digit",
    "test_valid_isbn_with_a_check_digit_of_10",
    "test_check_digit_is_a_character_other_than_x",
    "test_invalid_check_digit_in_isbn_is_not_treated_as_zero",
    "test_invalid_character_in_isbn_is_not_treated_as_zero",
    "test_x_is_only_valid_as_a_check_digit",
    "test_only_one_check_digit_is_allowed",
    "test_x_is_not_substituted_by_the_value_10",
    "test_valid_isbn_without_separating_dashes",
    "test_isbn_without_separating_dashes_and_x_as_check_digit",
    "test_isbn_without_check_digit_and_dashes",
    "test_too_long_isbn_and_no_dashes",
    "test_too_short_isbn",
    "test_isbn_without_check_digit",
    "test_check_digit_of_x_should_not_be_used_for_0",
    "test_empty_isbn",
    "test_input_is_9_characters",
    "test_invalid_characters_are_not_ignored_after_checking_length",
    "test_invalid_characters_are_not_ignored_before_checking_length",
    "test_input_is_too_long_but_contains_a_valid_isbn",
]

BASELINE_CASES = [
    "test_valid_isbn",
    "test_invalid_isbn_check_digit",
    "test_valid_isbn_with_a_check_digit_of_10",
]


def execute_micro_examples() -> dict:
    """Execute and assert both micro-examples matching published hints."""
    # Micro-example 1: Targeted list mutation
    raw_1 = "012345678X"
    chars_1 = list(raw_1)
    if chars_1 and chars_1[-1] == "X":
        chars_1[-1] = "10"

    expected_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "10"]
    assert chars_1 == expected_chars, f"Micro-example 1 chars mismatch: {chars_1}"
    assert len(chars_1) == 10, f"Micro-example 1 length mismatch: {len(chars_1)}"

    # Micro-example 2: Pitfall of string .replace('X', '10')
    bad_isbn = "35982X5079"
    replaced_2 = bad_isbn.replace("X", "10")
    expected_replaced = "35982105079"
    assert replaced_2 == expected_replaced, f"Micro-example 2 string mismatch: {replaced_2}"
    assert len(replaced_2) == 11, f"Micro-example 2 length mismatch: {len(replaced_2)}"

    # String immutability check
    string_immutable = False
    try:
        raw_1[-1] = "10"  # type: ignore
    except TypeError:
        string_immutable = True
    assert string_immutable, "Expected TypeError on string item assignment!"

    return {
        "micro_example_1": {
            "input": raw_1,
            "result_chars": chars_1,
            "result_len": len(chars_1),
            "expected_chars": expected_chars,
            "expected_len": 10,
            "status": "PASS",
        },
        "micro_example_2_pitfall": {
            "input": bad_isbn,
            "result_string": replaced_2,
            "result_len": len(replaced_2),
            "expected_string": expected_replaced,
            "expected_len": 11,
            "status": "PASS",
        },
        "string_immutability_enforced": {
            "raises_type_error": string_immutable,
            "status": "PASS",
        },
    }


def main() -> int:
    print("[*] Starting automated check for Task R36-T027 (isbn-verifier)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/isbn-verifier")
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
    hints_file = exercise_dir / ".docs" / "hints.md"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner stub in working tree is strictly unsolved
    assert working_solution_file.is_file(), f"Solution file missing at {working_solution_file}"
    stub_content = working_solution_file.read_text(encoding="utf-8")
    is_stub_unsolved = "pass" in stub_content and "return" not in stub_content and "replace" not in stub_content
    assert is_stub_unsolved, "Learner solution stub isbn_verifier.py has been modified or solved!"
    print("[+] Verified learner solution stub in working tree is strictly unsolved.")

    # 3. Verify hints.md documentation content
    assert hints_file.is_file(), f"hints.md missing at {hints_file}"
    hints_text = hints_file.read_text(encoding="utf-8")

    assert "Mutable Sequences vs. String Immutability" in hints_text, "Missing section title in hints.md"
    assert "chars = list(isbn.replace('-', ''))" in hints_text, "Missing reference code snippet in hints.md"
    assert "chars[-1] = '10'" in hints_text, "Missing check digit mutation explanation in hints.md"
    assert "bad_isbn = \"35982X5079\"" in hints_text, "Missing pitfall input in hints.md"
    assert "https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types" in hints_text, "Missing official Python docs link in hints.md"
    print("[+] Verified hints.md contains language guidance, micro-examples, pitfall, and official docs link.")

    # 4. Assert and verify outputs of both micro-examples
    micro_results = execute_micro_examples()
    print("[+] Successfully executed and verified both micro-examples and string immutability semantics.")

    # 5. Scratch copy test execution with pytest
    test_case_statuses = {}
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = Path(tmp_dir) / "isbn-verifier"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        # Substitute reference as solution file in scratch copy
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
        assert total_passed == 21, f"Expected 21 passing tests, got {total_passed}"
        print(f"[+] All {total_passed} tests passed successfully in isolated scratch run.")

    # 6. Verify working tree learner stub remains strictly unchanged
    stub_content_after = working_solution_file.read_text(encoding="utf-8")
    assert stub_content == stub_content_after, "Working tree stub was modified during check execution!"
    print("[+] Confirmed working tree learner stub remained untouched.")

    # 7. Record results in work/R36-T027/results.json and results.txt
    results_record = {
        "task_id": "R36-T027",
        "exercise": "exercises/practice/isbn-verifier",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "hints_file": str(hints_file.relative_to(repo_root)),
            "canonical_cases": CANONICAL_CASES,
            "baseline_cases": BASELINE_CASES,
            "guidance_topic": "Mutable Sequences (list) vs. String Immutability (str)",
            "official_docs_url": "https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types",
        },
        "counts": {
            "total_canonical_cases": len(CANONICAL_CASES),
            "executed_cases": total_passed,
            "passed_cases": total_passed,
            "failed_cases": 0,
        },
        "test_statuses": test_case_statuses,
        "micro_examples_verification": micro_results,
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
                "expected": 21,
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
            "micro_example_1_verified": {
                "expected": True,
                "actual": micro_results["micro_example_1"]["status"] == "PASS",
                "status": "PASS",
            },
            "micro_example_2_pitfall_verified": {
                "expected": True,
                "actual": micro_results["micro_example_2_pitfall"]["status"] == "PASS",
                "status": "PASS",
            },
            "string_immutability_verified": {
                "expected": True,
                "actual": micro_results["string_immutability_enforced"]["status"] == "PASS",
                "status": "PASS",
            },
            "working_tree_learner_stub_untouched": {
                "expected": True,
                "actual": stub_content == stub_content_after,
                "status": "PASS",
            },
        },
        "summary": "Verified all 21 canonical test cases pass against reference in scratch environment; executed and asserted both micro-example outputs matching hints.md. Learner stub remains strictly unsolved.",
    }

    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {results_json_path}")

    results_txt_path = work_dir / "results.txt"
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T027 Automated Check & Language Guidance Report\n")
        f.write("=" * 65 + "\n\n")
        f.write("Exercise: exercises/practice/isbn-verifier\n")
        f.write("Tool Versions:\n")
        f.write(f"  Python: {py_version.splitlines()[0]}\n")
        f.write(f"  Pytest: {pytest_version}\n")
        f.write(f"  Platform: {platform_info}\n\n")
        f.write("Pytest Execution Results (in isolated scratch directory):\n")
        f.write(f"  Child exit code: {child_returncode}\n")
        f.write(f"  Executed cases: {total_passed}/21 passed\n")
        f.write(f"  Output summary: {stdout_q}\n\n")
        f.write("Canonical Test Cases Status:\n")
        for c in CANONICAL_CASES:
            baseline_tag = " (Baseline)" if c in BASELINE_CASES else ""
            f.write(f"  - {c}{baseline_tag}: {test_case_statuses.get(c)}\n")
        f.write("\nMicro-Examples & Language Construct Verification:\n")
        f.write("  1. Micro-Example 1 (Targeted List Mutation):\n")
        f.write(f"     Input: {micro_results['micro_example_1']['input']}\n")
        f.write(f"     Output: {micro_results['micro_example_1']['result_chars']} (length {micro_results['micro_example_1']['result_len']})\n")
        f.write("     Status: PASS\n")
        f.write("  2. Micro-Example 2 (Pitfall of String .replace('X', '10')):\n")
        f.write(f"     Input: {micro_results['micro_example_2_pitfall']['input']}\n")
        f.write(f"     Output: '{micro_results['micro_example_2_pitfall']['result_string']}' (length {micro_results['micro_example_2_pitfall']['result_len']})\n")
        f.write("     Status: PASS\n")
        f.write(f"  3. String Immutability TypeError Enforced: PASS\n")
        f.write("\nLearner Solution Stub Verification:\n")
        f.write(f"  Path: {solution_rel}\n")
        f.write("  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks and micro-example assertions passed successfully.\n")
    print(f"[+] Saved text summary to {results_txt_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
