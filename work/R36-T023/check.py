#!/usr/bin/env python3
"""
Automated verification check for Task R36-T023:
Mutation-driven regression for linked-list.

Requirements:
1. Resolve solution/test/example paths from exercises/practice/linked-list/.meta/config.json.
2. Use Python subprocess and temporary directories for execution.
3. Test original reference solution in scratch copy:
   - Must pass all 24 test cases, including named anchor cases:
     test_pop_gets_element_from_the_list,
     test_push_pop_respectively_add_remove_at_the_end_of_the_list,
     test_shift_gets_an_element_from_the_list.
4. Verify working tree learner stub is strictly unsolved.
5. Create deliberate mutant in a separate scratch copy:
   - Mutant changes condition in pop():
     'if node is None or node.prev is None:' -> 'if node is None or node.succeeding is None:'
   - Verify original passes and mutant fails named assertion in:
     test_push_pop_respectively_add_remove_at_the_end_of_the_list.
   - Verify test_pop_gets_element_from_the_list and test_shift_gets_an_element_from_the_list pass.
6. Check that hints.md and maintenance documentation exist and document the contract.
7. Record inputs, expected vs actual results, tool versions in work/R36-T023/.
8. Exit non-zero on any assertion failure.
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


ANCHOR_CASES = [
    "test_pop_gets_element_from_the_list",
    "test_push_pop_respectively_add_remove_at_the_end_of_the_list",
    "test_shift_gets_an_element_from_the_list",
]

REJECTING_CASE = "test_push_pop_respectively_add_remove_at_the_end_of_the_list"
REJECTING_UUID = "c3f67e5d-cfa2-4c3e-a18f-7ce999c3c885"


def main() -> int:
    print("[*] Starting automated check for Task R36-T023 (linked-list)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/linked-list")
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
    maintenance_doc = repo_root / "docs" / "maintenance" / "linked-list.md"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner stub in working tree is unsolved
    assert working_solution_file.is_file(), "Learner solution file missing"
    with open(working_solution_file, "r", encoding="utf-8") as f:
        stub_content = f.read()

    is_stub_unsolved = "pass" in stub_content and "self.head" not in stub_content
    assert is_stub_unsolved, "Working tree learner stub has been solved or modified!"
    print("[+] Verified learner stub in working tree is unsolved.")

    # 3. Verify documentation files
    assert hints_file.is_file(), f"hints.md missing at {hints_file}"
    hints_text = hints_file.read_text(encoding="utf-8")
    assert "pop()" in hints_text and "succeeding" in hints_text and "prev" in hints_text
    print("[+] Verified hints.md exists and explains the pointer contract.")

    assert maintenance_doc.is_file(), f"maintenance doc missing at {maintenance_doc}"
    maint_text = maintenance_doc.read_text(encoding="utf-8")
    assert REJECTING_CASE in maint_text and REJECTING_UUID in maint_text
    print("[+] Verified docs/maintenance/linked-list.md exists and records the mutant.")

    # 4. Scratch Test Execution of Original Reference Solution
    with tempfile.TemporaryDirectory() as orig_tmp_str:
        orig_tmp = Path(orig_tmp_str)
        scratch_exercise = orig_tmp / "exercise"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        scratch_sol = scratch_exercise / solution_rel
        scratch_ex = scratch_exercise / example_rel

        # Substitute reference into solution filename in scratch copy only
        shutil.copyfile(scratch_ex, scratch_sol)

        print("[*] Running pytest against original reference implementation in scratch copy...")
        proc_pytest = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )

        child_exit_code = proc_pytest.returncode
        child_stdout = proc_pytest.stdout
        child_stderr = proc_pytest.stderr

        print(f"[*] Original child return code: {child_exit_code}")
        print(f"[*] Pytest stdout:\n{child_stdout.strip()}")
        if child_stderr:
            print(f"[*] Pytest stderr:\n{child_stderr.strip()}")

        assert child_exit_code == 0, f"Original reference failed pytest with exit code {child_exit_code}"

        # Parse test count
        match = re.search(r"(\d+)\s+passed", child_stdout)
        assert match is not None, f"Could not parse passed test count:\n{child_stdout}"
        passed_count = int(match.group(1))

        print(f"[+] Reported executed cases: {passed_count}")
        assert passed_count > 0, "Zero tests executed!"
        assert passed_count == 24, f"Expected 24 passed tests, got {passed_count}"

        # Run with -v to verify individual anchor cases
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, "pytest -v run failed"

        original_anchor_status = {}
        for ac in ANCHOR_CASES:
            assert f"{ac} PASSED" in proc_v.stdout, f"Anchor case {ac} did not pass in original reference!"
            original_anchor_status[ac] = "PASSED"
        print("[+] Verified all anchor cases passed in original reference.")

    # 5. Confirm working tree was not rewritten
    with open(working_solution_file, "r", encoding="utf-8") as f:
        post_test_stub = f.read()
    assert post_test_stub == stub_content, "Working tree solution file was unexpectedly modified!"
    print("[+] Confirmed working tree solution file was untouched.")

    # 6. Scratch Test Execution of Mutated Reference Solution
    with tempfile.TemporaryDirectory() as mut_tmp_str:
        mut_tmp = Path(mut_tmp_str)
        scratch_mut_exercise = mut_tmp / "exercise"
        shutil.copytree(exercise_dir, scratch_mut_exercise, dirs_exist_ok=True)

        scratch_mut_sol = scratch_mut_exercise / solution_rel
        scratch_mut_ex = scratch_mut_exercise / example_rel

        # Read original example and construct deliberate mutant
        orig_code = scratch_mut_ex.read_text(encoding="utf-8")
        target_condition = "if node is None or node.prev is None:"
        mutated_condition = "if node is None or node.succeeding is None:"
        assert target_condition in orig_code, f"Target condition not found in {example_rel}"

        mutant_code = orig_code.replace(target_condition, mutated_condition)
        assert mutant_code != orig_code, "Mutant code identical to original!"

        # Write mutant into scratch solution file
        scratch_mut_sol.write_text(mutant_code, encoding="utf-8")

        print("[*] Running pytest against mutated reference implementation in scratch copy...")
        proc_mut = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "-k", " or ".join(ANCHOR_CASES)],
            cwd=str(scratch_mut_exercise),
            capture_output=True,
            text=True,
        )

        mutant_exit_code = proc_mut.returncode
        mutant_stdout = proc_mut.stdout
        print(f"[*] Mutant child return code: {mutant_exit_code} (non-zero expected: {mutant_exit_code != 0})")

        # Mutant MUST fail child exit code (exit non-zero)
        assert mutant_exit_code != 0, "Mutant unexpectedly passed all anchor tests!"

        # Specifically verify the rejecting case failed and other anchors passed
        mutant_anchor_status = {}
        for ac in ANCHOR_CASES:
            if ac == REJECTING_CASE:
                is_failed = f"{ac} FAILED" in mutant_stdout
                assert is_failed, f"Expected {ac} to FAIL on mutant, but it did not!"
                mutant_anchor_status[ac] = "FAILED"
                print(f"[+] Successfully confirmed mutant is REJECTED by {ac}")
            else:
                is_passed = f"{ac} PASSED" in mutant_stdout
                assert is_passed, f"Expected {ac} to PASS on mutant, but it did not!"
                mutant_anchor_status[ac] = "PASSED"
                print(f"[+] Confirmed {ac} PASSED on mutant")

    # 7. Save results, expected vs actual, inputs, and tool versions in work/R36-T023/
    results_record = {
        "task_id": "R36-T023",
        "exercise": "exercises/practice/linked-list",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "hints_file": str(hints_file.relative_to(repo_root)),
            "maintenance_doc": str(maintenance_doc.relative_to(repo_root)),
            "anchor_cases": ANCHOR_CASES,
            "rejecting_case": REJECTING_CASE,
            "rejecting_uuid": REJECTING_UUID,
            "mutation": {
                "original_line": target_condition,
                "mutated_line": mutated_condition,
                "description": "Mutated pop() boundary condition checking succeeding instead of prev",
            },
        },
        "counts": {
            "total_test_cases": passed_count,
            "anchor_cases_count": len(ANCHOR_CASES),
        },
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "original_child_return_code": {
                "expected": 0,
                "actual": child_exit_code,
                "status": "PASS",
            },
            "original_total_passed": {
                "expected": 24,
                "actual": passed_count,
                "status": "PASS",
            },
            "original_anchors_status": {
                "expected": {ac: "PASSED" for ac in ANCHOR_CASES},
                "actual": original_anchor_status,
                "status": "PASS",
            },
            "mutant_child_return_code": {
                "expected": "non-zero",
                "actual": mutant_exit_code,
                "status": "PASS",
            },
            "mutant_rejecting_case_status": {
                "expected": "FAILED",
                "actual": mutant_anchor_status[REJECTING_CASE],
                "status": "PASS",
            },
            "mutant_non_rejecting_anchors_status": {
                "expected": {ac: "PASSED" for ac in ANCHOR_CASES if ac != REJECTING_CASE},
                "actual": {ac: mutant_anchor_status[ac] for ac in ANCHOR_CASES if ac != REJECTING_CASE},
                "status": "PASS",
            },
            "working_tree_unchanged": {
                "expected": True,
                "actual": True,
                "status": "PASS",
            },
        },
        "summary": "Original reference passed all 24 tests; mutant was successfully rejected by test_push_pop_respectively_add_remove_at_the_end_of_the_list.",
    }

    json_out = work_dir / "results.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {json_out}")

    txt_out = work_dir / "results.txt"
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write("Task R36-T023 Automated Check Verification Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Tool Versions:\n  Python: {py_version.splitlines()[0]}\n  Pytest: {pytest_version}\n  Platform: {platform_info}\n\n")
        f.write(f"Original Reference Execution:\n  Exit code: {child_exit_code}\n  Executed cases: {passed_count}/24 passed\n\n")
        f.write("Anchor Cases (Original Reference):\n")
        for ac, st in original_anchor_status.items():
            f.write(f"  - {ac}: {st}\n")
        f.write("\nMutant Execution (Condition Mutation in pop):\n")
        f.write(f"  Mutation: {target_condition} -> {mutated_condition}\n")
        f.write(f"  Child exit code: {mutant_exit_code} (non-zero: PASS)\n")
        for ac, st in mutant_anchor_status.items():
            f.write(f"  - {ac}: {st}\n")
        f.write(f"\nRejecting Test Confirmed: {REJECTING_CASE} (UUID: {REJECTING_UUID})\n")
        f.write("\nWorking Tree Learner Stub:\n  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks passed successfully.\n")
    print(f"[+] Saved text summary to {txt_out}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
