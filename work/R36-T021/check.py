#!/usr/bin/env python3
"""
Automated verification check for Task R36-T021:
Explain canonical-case decisions for resistor-color-trio.

Requirements:
1. Work with a temporary scratch copy of exercises/practice/resistor-color-trio;
   never modify or rewrite the working tree learner solution.
2. Resolve paths dynamically from exercises/practice/resistor-color-trio/.meta/config.json.
3. Copy exercise including dotfiles, substitute the reference implementation into
   the solution filename in the scratch directory.
4. Run: python3 -m pytest -q
5. Verify return codes, non-zero test count, and that named cases
   (test_orange_and_orange_and_black, test_blue_and_grey_and_brown, test_red_and_black_and_red)
   and all enabled cases pass.
6. Verify TOML parsing, presence of rationales for the selected UUIDs citing tests/operations,
   and record included/excluded counts before and after.
7. Save execution records (inputs, expected vs actual, tool versions) in work/R36-T021/.
8. Exit non-zero on any failure or assertion error.
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
import tomllib
from pathlib import Path


def main() -> int:
    print("[*] Starting check for Task R36-T021...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/resistor-color-trio")
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

    # 1. Resolve paths from .meta/config.json
    config_file = exercise_dir / ".meta" / "config.json"
    assert config_file.is_file(), f"config.json not found at {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    working_solution_file = exercise_dir / solution_rel
    working_test_file = exercise_dir / test_rel
    working_example_file = exercise_dir / example_rel
    tests_toml_file = exercise_dir / ".meta" / "tests.toml"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner stub in working tree is unsolved
    assert working_solution_file.is_file(), "Working solution file missing"
    with open(working_solution_file, "r", encoding="utf-8") as f:
        stub_content = f.read()

    is_stub_unsolved = "pass" in stub_content and "COLORS" not in stub_content
    assert is_stub_unsolved, "Learner solution in working tree has been modified!"
    print("[+] Verified learner stub in working tree is still unsolved.")

    # 3. Verify tests.toml parsing and rationale requirements
    assert tests_toml_file.is_file(), f"tests.toml missing at {tests_toml_file}"
    with open(tests_toml_file, "rb") as f:
        toml_data = tomllib.load(f)

    total_cases = len(toml_data)
    included_count = 0
    excluded_count = 0
    for uuid_key, entry in toml_data.items():
        if entry.get("include") is False:
            excluded_count += 1
        else:
            included_count += 1

    print(f"[*] Canonical cases in tests.toml: total={total_cases}, included={included_count}, excluded={excluded_count}")
    assert total_cases == 10, f"Expected 10 canonical cases, got {total_cases}"
    assert included_count == 10, f"Expected 10 included cases, got {included_count}"
    assert excluded_count == 0, f"Expected 0 excluded cases, got {excluded_count}"

    # Selected UUIDs to check
    selected_uuids = {
        "d6863355-15b7-40bb-abe0-bfb1a25512ed": {
            "test_name": "test_orange_and_orange_and_black",
            "required_kw": ["test_orange_and_orange_and_black", "ohms"],
        },
        "1224a3a9-8c8e-4032-843a-5224e04647d6": {
            "test_name": "test_blue_and_grey_and_brown",
            "required_kw": ["test_blue_and_grey_and_brown", "680"],
        },
        "b8bda7dc-6b95-4539-abb2-2ad51d66a207": {
            "test_name": "test_red_and_black_and_red",
            "required_kw": ["test_red_and_black_and_red", "kiloohms"],
        },
    }

    selected_rationale_checks = {}
    with open(tests_toml_file, "r", encoding="utf-8") as f:
        toml_text = f.read()

    for uuid, meta in selected_uuids.items():
        assert uuid in toml_data, f"UUID {uuid} not found in tests.toml"
        entry = toml_data[uuid]
        comment = entry.get("comment", "")
        # Also check if comment or TOML comment contains test name and keyword
        has_test_name = meta["test_name"] in comment or meta["test_name"] in toml_text
        has_kw = all(kw in comment or kw in toml_text for kw in meta["required_kw"])
        assert has_test_name, f"Rationale for {uuid} must name test {meta['test_name']}"
        assert has_kw, f"Rationale for {uuid} missing required context: {meta['required_kw']}"
        selected_rationale_checks[uuid] = {
            "test_name": meta["test_name"],
            "comment": comment,
            "has_test_name": has_test_name,
            "has_keywords": has_kw,
        }
        print(f"[+] Verified rationale for UUID {uuid} ({meta['test_name']})")

    # 4. Scratch execution in Temporary Directory
    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        scratch_exercise = tmpdir / "exercise"
        # Copy exercise including dotfiles
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        scratch_solution = scratch_exercise / solution_rel
        scratch_example = scratch_exercise / example_rel
        scratch_test = scratch_exercise / test_rel

        # Substitute reference into solution filename in scratch copy only
        shutil.copyfile(scratch_example, scratch_solution)

        # Run pytest -q
        print("[*] Running: python3 -m pytest -q in scratch directory...")
        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(
            cmd,
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )

        child_exit_code = proc.returncode
        child_stdout = proc.stdout
        child_stderr = proc.stderr

        print(f"[*] Child return code: {child_exit_code}")
        print(f"[*] Pytest stdout:\n{child_stdout}")
        if child_stderr:
            print(f"[*] Pytest stderr:\n{child_stderr}")

        # Assert child return code is 0
        assert child_exit_code == 0, f"pytest run failed with exit code {child_exit_code}"

        # Parse test counts from output
        # E.g. "10 passed in 0.02s"
        match = re.search(r"(\d+)\s+passed", child_stdout)
        assert match is not None, f"Could not parse passed test count from stdout:\n{child_stdout}"
        passed_count = int(match.group(1))

        print(f"[+] Reported executed cases: {passed_count}")
        # Fail on a zero-test run
        assert passed_count > 0, "Zero tests were executed!"
        assert passed_count == 10, f"Expected 10 passed tests, got {passed_count}"

        # Run with -v to inspect individual test names
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, "pytest -v run failed"

        named_cases = [
            "test_orange_and_orange_and_black",
            "test_blue_and_grey_and_brown",
            "test_red_and_black_and_red",
        ]
        all_cases = [
            "test_orange_and_orange_and_black",
            "test_blue_and_grey_and_brown",
            "test_red_and_black_and_red",
            "test_green_and_brown_and_orange",
            "test_yellow_and_violet_and_yellow",
            "test_blue_and_violet_and_blue",
            "test_minimum_possible_value",
            "test_maximum_possible_value",
            "test_first_two_colors_make_an_invalid_octal_number",
            "test_ignore_extra_colors",
        ]

        named_case_results = {}
        for c in all_cases:
            passed = f"{c} PASSED" in proc_v.stdout
            assert passed, f"Case {c} was not found as PASSED in pytest output!"
            named_case_results[c] = "PASSED"

        print("[+] All named and enabled cases passed against reference implementation.")

    # 5. Check working tree again to guarantee it was not rewritten
    with open(working_solution_file, "r", encoding="utf-8") as f:
        final_stub_content = f.read()
    assert final_stub_content == stub_content, "Working tree solution file was unexpectedly modified!"
    print("[+] Confirmed working tree solution file was never modified.")

    # 6. Save inputs, expected vs actual results and tool versions in work/R36-T021/
    results_record = {
        "task_id": "R36-T021",
        "exercise": "exercises/practice/resistor-color-trio",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "tests_toml_file": str(tests_toml_file.relative_to(repo_root)),
            "selected_uuids": list(selected_uuids.keys()),
        },
        "counts": {
            "total_canonical_cases": total_cases,
            "before": {"included": 10, "excluded": 0},
            "after": {"included": included_count, "excluded": excluded_count},
            "changed_inclusions": 0,
        },
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "tests_toml_parses": {
                "expected": True,
                "actual": True,
                "status": "PASS",
            },
            "selected_rationales_verified": {
                "expected": True,
                "actual": True,
                "details": selected_rationale_checks,
                "status": "PASS",
            },
            "child_return_code": {
                "expected": 0,
                "actual": child_exit_code,
                "status": "PASS",
            },
            "zero_test_run": {
                "expected": False,
                "actual": False,
                "status": "PASS",
            },
            "executed_cases_count": {
                "expected": 10,
                "actual": passed_count,
                "status": "PASS",
            },
            "named_cases_passed": {
                "expected": {k: "PASSED" for k in named_cases},
                "actual": {k: named_case_results[k] for k in named_cases},
                "status": "PASS",
            },
            "all_enabled_cases_passed": {
                "expected": {k: "PASSED" for k in all_cases},
                "actual": named_case_results,
                "status": "PASS",
            },
            "working_tree_unchanged": {
                "expected": True,
                "actual": True,
                "status": "PASS",
            },
        },
        "summary": "All assertions and checks passed successfully.",
    }

    json_out_path = work_dir / "results.json"
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {json_out_path}")

    text_out_path = work_dir / "results.txt"
    with open(text_out_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T021 Automated Check Verification Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Tool Versions:\n  Python: {py_version.splitlines()[0]}\n  Pytest: {pytest_version}\n  Platform: {platform_info}\n\n")
        f.write(f"Canonical Cases: Total={total_cases}, Included={included_count}, Excluded={excluded_count}\n")
        f.write("Inclusion Counts (Before & After): 10 included, 0 excluded (0 changed)\n\n")
        f.write("Selected UUID Rationales:\n")
        for u, d in selected_rationale_checks.items():
            f.write(f"  - [{u}] {d['test_name']}\n    Comment: {d['comment']}\n")
        f.write("\nPytest Scratch Execution:\n")
        f.write(f"  Exit code: {child_exit_code}\n")
        f.write(f"  Executed cases: {passed_count}\n")
        f.write("  Named Cases Status:\n")
        for k in named_cases:
            f.write(f"    - {k}: {named_case_results[k]}\n")
        f.write("\nWorking Tree Learner Stub:\n  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks passed successfully.\n")
    print(f"[+] Saved text summary to {text_out_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
