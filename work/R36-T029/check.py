#!/usr/bin/env python3
"""Verification suite for Task R36-T029 (poker isolated test runner).

Verifies:
1. Learner stub poker.py is untouched, unsolved, and preserves SHA-256 hash
   before and after all test runs.
2. Mode 1 (Real Reference): All 37 canonical test cases pass with exit code 0,
   including anchor cases:
   - test_single_hand_always_wins
   - test_highest_card_out_of_all_hands_wins
   - test_a_tie_has_multiple_winners
3. Mode 2 (Deliberately Failing Reference): Fails, detects assertion failure,
   and propagates non-zero exit code.
4. Mode 3 (Zero Tests / Empty Filter): Fails on zero executed tests and propagates
   non-zero exit code.
5. Temporary scratch directories are cleaned up in all cases.
6. Saves results.json and results.txt to work/R36-T029/.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Dict


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists() or (current / "exercises").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def load_isolated_runner(runner_path: Path):
    """Dynamically load isolated runner module from path."""
    if not runner_path.is_file():
        raise FileNotFoundError(f"Runner tool not found at {runner_path}")
    spec = importlib.util.spec_from_file_location("r36_t029_runner", str(runner_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for {runner_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_stub_unsolved(content: str) -> bool:
    """Check that learner stub contains only empty starter code."""
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
    has_def = any("def best_hands" in line for line in lines)
    has_pass = any(line == "pass" for line in lines)
    has_return = any("return " in line for line in lines)
    has_body = any("allmax" in line or "hand_rank" in line for line in lines)
    return has_def and has_pass and not has_return and not has_body


def main() -> None:
    repo_root = find_repo_root()
    exercise_dir = repo_root / "exercises" / "practice" / "poker"
    stub_path = exercise_dir / "poker.py"
    runner_tool_path = repo_root / "tools" / "course_checks" / "r36-t029.py"
    work_dir = repo_root / "work" / "R36-T029"
    work_dir.mkdir(parents=True, exist_ok=True)

    print("======================================================================")
    print("Task R36-T029 Verification Suite: Poker Isolated Test Runner")
    print("======================================================================")

    # 1. Initial Learner Stub Verification
    if not stub_path.is_file():
        raise FileNotFoundError(f"Learner stub missing: {stub_path}")

    stub_content = stub_path.read_text(encoding="utf-8")
    if not verify_stub_unsolved(stub_content):
        raise AssertionError("Learner stub poker.py is not in an unsolved state!")

    initial_stub_hash = compute_file_hash(stub_path)
    print(f"[*] Initial learner stub SHA-256: {initial_stub_hash}")
    print(f"[*] Learner stub is unsolved: OK ('def best_hands(hands): pass')")

    def assert_stub_integrity(phase_label: str) -> str:
        current_hash = compute_file_hash(stub_path)
        if current_hash != initial_stub_hash:
            raise AssertionError(
                f"FATAL: Learner stub modified during '{phase_label}'! "
                f"Expected {initial_stub_hash}, found {current_hash}"
            )
        current_content = stub_path.read_text(encoding="utf-8")
        if not verify_stub_unsolved(current_content):
            raise AssertionError(f"FATAL: Learner stub became solved during '{phase_label}'!")
        return current_hash

    # Load runner tool
    runner_mod = load_isolated_runner(runner_tool_path)
    run_isolated_tests = runner_mod.run_isolated_tests

    # Query tool versions
    pytest_version_proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    pytest_version_str = (pytest_version_proc.stdout or pytest_version_proc.stderr).strip()

    # ------------------------------------------------------------------
    # Mode 1: Maintained Reference Implementation
    # ------------------------------------------------------------------
    print("\n----------------------------------------------------------------------")
    print("Running Mode 1: Maintained Reference Implementation (all 37 tests)")
    print("----------------------------------------------------------------------")
    mode1_result = run_isolated_tests(exercise_dir=exercise_dir, verbose=False)

    print(f"[*] Mode 1 Exit Code: {mode1_result['exit_code']}")
    print(f"[*] Mode 1 Executed: {mode1_result['total_executed']} | Passed: {mode1_result['passed']} | Failed: {mode1_result['failed']}")
    print(f"[*] Mode 1 Scratch Cleaned: {mode1_result['scratch_dir_cleaned']}")

    # Check CLI subprocess execution parity
    cli_proc_mode1 = subprocess.run(
        [sys.executable, str(runner_tool_path), "--json"],
        capture_output=True,
        text=True,
    )
    assert cli_proc_mode1.returncode == 0, f"CLI runner failed on Mode 1 with code {cli_proc_mode1.returncode}"
    cli_json_mode1 = json.loads(cli_proc_mode1.stdout)
    assert cli_json_mode1["exit_code"] == 0, "CLI JSON reported non-zero exit code"
    assert cli_json_mode1["total_executed"] == 37, f"Expected 37 tests in CLI, got {cli_json_mode1['total_executed']}"

    # Assertions for Mode 1
    assert mode1_result["success"] is True, "Mode 1 failed but should have succeeded"
    assert mode1_result["exit_code"] == 0, f"Expected exit code 0, got {mode1_result['exit_code']}"
    assert mode1_result["child_returncode"] == 0, f"Expected child returncode 0, got {mode1_result['child_returncode']}"
    assert mode1_result["total_executed"] == 37, f"Expected 37 total executed, got {mode1_result['total_executed']}"
    assert mode1_result["passed"] == 37, f"Expected 37 passed, got {mode1_result['passed']}"
    assert mode1_result["failed"] == 0, f"Expected 0 failed, got {mode1_result['failed']}"
    assert mode1_result["scratch_dir_cleaned"] is True, "Scratch directory was not cleaned up in Mode 1"

    # Named anchor cases verification
    anchor_cases = [
        "test_single_hand_always_wins",
        "test_highest_card_out_of_all_hands_wins",
        "test_a_tie_has_multiple_winners",
    ]
    for case in anchor_cases:
        status = mode1_result["named_cases"].get(case)
        assert status == "PASSED", f"Anchor test case '{case}' was not PASSED (got: {status})"
        print(f"    [✓] Anchor Case '{case}': {status}")

    hash_after_mode1 = assert_stub_integrity("Mode 1 (Maintained Reference)")
    print(f"[*] Stub SHA-256 after Mode 1: {hash_after_mode1} (UNCHANGED)")

    # ------------------------------------------------------------------
    # Mode 2: Deliberately Failing Reference Implementation
    # ------------------------------------------------------------------
    print("\n----------------------------------------------------------------------")
    print("Running Mode 2: Deliberately Failing Reference Implementation")
    print("----------------------------------------------------------------------")
    failing_code = "def best_hands(hands):\n    return []\n"
    mode2_result = run_isolated_tests(
        exercise_dir=exercise_dir,
        override_reference_content=failing_code,
        verbose=False,
    )

    print(f"[*] Mode 2 Exit Code: {mode2_result['exit_code']}")
    print(f"[*] Mode 2 Executed: {mode2_result['total_executed']} | Passed: {mode2_result['passed']} | Failed: {mode2_result['failed']}")
    print(f"[*] Mode 2 Scratch Cleaned: {mode2_result['scratch_dir_cleaned']}")

    # Check CLI subprocess execution parity for Mode 2
    cli_proc_mode2 = subprocess.run(
        [sys.executable, str(runner_tool_path), "--override-ref-content", failing_code, "--json"],
        capture_output=True,
        text=True,
    )
    assert cli_proc_mode2.returncode != 0, f"CLI runner should have exited non-zero for Mode 2, got {cli_proc_mode2.returncode}"
    cli_json_mode2 = json.loads(cli_proc_mode2.stdout)
    assert cli_json_mode2["exit_code"] != 0, "CLI JSON should have reported non-zero exit code"

    # Assertions for Mode 2
    assert mode2_result["success"] is False, "Mode 2 should have reported failure"
    assert mode2_result["exit_code"] != 0, f"Expected non-zero exit code, got {mode2_result['exit_code']}"
    assert mode2_result["child_returncode"] != 0, f"Expected non-zero child returncode, got {mode2_result['child_returncode']}"
    assert mode2_result["failed"] > 0, f"Expected failed tests > 0, got {mode2_result['failed']}"
    assert mode2_result["scratch_dir_cleaned"] is True, "Scratch directory was not cleaned up in Mode 2"
    print("    [✓] Deliberate assertion failure detected and propagated correctly.")

    hash_after_mode2 = assert_stub_integrity("Mode 2 (Failing Reference)")
    print(f"[*] Stub SHA-256 after Mode 2: {hash_after_mode2} (UNCHANGED)")

    # ------------------------------------------------------------------
    # Mode 3: Zero-Test Selection (Empty Filter)
    # ------------------------------------------------------------------
    print("\n----------------------------------------------------------------------")
    print("Running Mode 3: Zero-Test Selection (Empty Filter)")
    print("----------------------------------------------------------------------")
    mode3_result = run_isolated_tests(
        exercise_dir=exercise_dir,
        pytest_args=["-k", "non_existent_test_filter_xyz"],
        verbose=False,
    )

    print(f"[*] Mode 3 Exit Code: {mode3_result['exit_code']}")
    print(f"[*] Mode 3 Executed: {mode3_result['total_executed']} | Deselected: {mode3_result['deselected']}")
    print(f"[*] Mode 3 Scratch Cleaned: {mode3_result['scratch_dir_cleaned']}")

    # Check CLI subprocess execution parity for Mode 3
    cli_proc_mode3 = subprocess.run(
        [sys.executable, str(runner_tool_path), "--pytest-args", "-k non_existent_test_filter_xyz", "--json"],
        capture_output=True,
        text=True,
    )
    assert cli_proc_mode3.returncode != 0, f"CLI runner should have exited non-zero for Mode 3, got {cli_proc_mode3.returncode}"
    cli_json_mode3 = json.loads(cli_proc_mode3.stdout)
    assert cli_json_mode3["exit_code"] != 0, "CLI JSON should have reported non-zero exit code"

    # Assertions for Mode 3
    assert mode3_result["success"] is False, "Mode 3 should have reported failure due to 0 executed tests"
    assert mode3_result["exit_code"] != 0, f"Expected non-zero exit code for 0 tests, got {mode3_result['exit_code']}"
    assert mode3_result["total_executed"] == 0, f"Expected total_executed == 0, got {mode3_result['total_executed']}"
    assert mode3_result["scratch_dir_cleaned"] is True, "Scratch directory was not cleaned up in Mode 3"
    print("    [✓] Zero-test execution correctly detected and rejected with non-zero exit code.")

    hash_after_mode3 = assert_stub_integrity("Mode 3 (Zero Tests)")
    print(f"[*] Stub SHA-256 after Mode 3: {hash_after_mode3} (UNCHANGED)")

    # ------------------------------------------------------------------
    # Final Results Assembly and Artifacts
    # ------------------------------------------------------------------
    results_data: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": "R36-T029",
        "exercise": "exercises/practice/poker",
        "system_info": {
            "python_version": sys.version,
            "pytest_version": pytest_version_str,
            "platform": platform.platform(),
        },
        "learner_stub": {
            "path": str(stub_path.relative_to(repo_root)),
            "initial_sha256": initial_stub_hash,
            "after_mode1_sha256": hash_after_mode1,
            "after_mode2_sha256": hash_after_mode2,
            "after_mode3_sha256": hash_after_mode3,
            "hash_identical_across_all_runs": (
                initial_stub_hash == hash_after_mode1 == hash_after_mode2 == hash_after_mode3
            ),
            "unsolved": True,
        },
        "modes": {
            "mode1_real_reference": {
                "description": "Maintained reference solution tested against full test suite",
                "expected_exit_code": 0,
                "actual_exit_code": mode1_result["exit_code"],
                "child_returncode": mode1_result["child_returncode"],
                "total_executed": mode1_result["total_executed"],
                "passed": mode1_result["passed"],
                "failed": mode1_result["failed"],
                "named_anchor_cases": mode1_result["named_cases"],
                "scratch_dir_cleaned": mode1_result["scratch_dir_cleaned"],
                "status": "PASSED",
            },
            "mode2_failing_reference": {
                "description": "Deliberately failing reference solution",
                "expected_exit_code": "non-zero (> 0)",
                "actual_exit_code": mode2_result["exit_code"],
                "child_returncode": mode2_result["child_returncode"],
                "total_executed": mode2_result["total_executed"],
                "passed": mode2_result["passed"],
                "failed": mode2_result["failed"],
                "scratch_dir_cleaned": mode2_result["scratch_dir_cleaned"],
                "status": "PASSED",
            },
            "mode3_zero_tests": {
                "description": "Zero-test execution via filtering",
                "expected_exit_code": "non-zero (> 0)",
                "actual_exit_code": mode3_result["exit_code"],
                "child_returncode": mode3_result["child_returncode"],
                "total_executed": mode3_result["total_executed"],
                "deselected": mode3_result["deselected"],
                "scratch_dir_cleaned": mode3_result["scratch_dir_cleaned"],
                "status": "PASSED",
            },
        },
        "overall_status": "PASSED",
    }

    # Save results.json
    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n[✓] Saved {results_json_path.relative_to(repo_root)}")

    # Save results.txt
    results_txt_path = work_dir / "results.txt"
    txt_content = f"""Task R36-T029 Verification Results
==================================
Date/Time: {results_data['timestamp']}
Exercise: {results_data['exercise']}
Python: {sys.version.split()[0]}
Pytest: {pytest_version_str}
Platform: {platform.platform()}
Overall Status: {results_data['overall_status']}

Learner Stub Integrity:
-----------------------
File: exercises/practice/poker/poker.py
Status: Strictly Unsolved (signature + pass)
Initial SHA-256: {initial_stub_hash}
After Mode 1:    {hash_after_mode1}
After Mode 2:    {hash_after_mode2}
After Mode 3:    {hash_after_mode3}
All Hashes Match: {results_data['learner_stub']['hash_identical_across_all_runs']}

Mode 1: Maintained Reference Implementation
-------------------------------------------
Exit Code: {mode1_result['exit_code']} (Expected: 0)
Child Return Code: {mode1_result['child_returncode']}
Executed Tests: {mode1_result['total_executed']} / 37
Passed: {mode1_result['passed']}
Failed: {mode1_result['failed']}
Scratch Cleaned: {mode1_result['scratch_dir_cleaned']}
Anchor Cases:
  - test_single_hand_always_wins: {mode1_result['named_cases']['test_single_hand_always_wins']}
  - test_highest_card_out_of_all_hands_wins: {mode1_result['named_cases']['test_highest_card_out_of_all_hands_wins']}
  - test_a_tie_has_multiple_winners: {mode1_result['named_cases']['test_a_tie_has_multiple_winners']}

Mode 2: Deliberately Failing Reference Implementation
-----------------------------------------------------
Exit Code: {mode2_result['exit_code']} (Expected: non-zero)
Child Return Code: {mode2_result['child_returncode']}
Executed Tests: {mode2_result['total_executed']}
Passed: {mode2_result['passed']}
Failed: {mode2_result['failed']}
Scratch Cleaned: {mode2_result['scratch_dir_cleaned']}
Assertion Failure Detected & Propagated: True

Mode 3: Zero-Test Selection (Empty Filter)
------------------------------------------
Exit Code: {mode3_result['exit_code']} (Expected: non-zero)
Child Return Code: {mode3_result['child_returncode']}
Executed Tests: {mode3_result['total_executed']}
Deselected Tests: {mode3_result['deselected']}
Scratch Cleaned: {mode3_result['scratch_dir_cleaned']}
Zero-Test Run Detected & Rejected: True
"""
    results_txt_path.write_text(txt_content, encoding="utf-8")
    print(f"[✓] Saved {results_txt_path.relative_to(repo_root)}")

    print("\n======================================================================")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY (EXIT 0)")
    print("======================================================================")


if __name__ == "__main__":
    main()
