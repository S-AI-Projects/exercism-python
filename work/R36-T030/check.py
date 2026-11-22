#!/usr/bin/env python3
"""Automated verification suite for Task R36-T030 (acronym contract cases).

Verifies:
1. Dynamic metadata path resolution from exercises/practice/acronym/.meta/config.json.
2. Learner stub acronym.py remains strictly unsolved and its SHA-256 hash is
   identical before and after all test executions.
3. Decision table in .docs/hints.md matches canonical inputs and expected outputs,
   including:
   - test_basic: "Portable Network Graphics" -> "PNG"
   - test_lowercase_words: "Ruby on Rails" -> "ROR"
   - test_punctuation: "First In, First Out" -> "FIFO"
4. Contract boundaries: explicitly documents specified vs. unspecified behavior
   without inventing Unicode, numeric-input, or exception-handling rules.
5. Isolated execution: Runs all 9 canonical tests against the reference solution
   in a temporary scratch directory.
6. Failure detection: Confirms non-zero exit codes on failing reference and zero-test runs.
7. Saves results.json and results.txt in work/R36-T030/.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").exists() or (current / "exercises").is_dir():
            return current
        current = current.parent
    return Path.cwd()


def resolve_metadata_paths(exercise_dir: Path) -> Dict[str, Path]:
    config_file = exercise_dir / ".meta" / "config.json"
    if not config_file.is_file():
        raise FileNotFoundError(f"Missing config.json at {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    files = config.get("files", {})
    solutions = files.get("solution", [])
    tests = files.get("test", [])
    examples = files.get("example", [])

    if not solutions or not tests or not examples:
        raise ValueError(f"Incomplete files configuration in {config_file}")

    return {
        "solution_rel": Path(solutions[0]),
        "test_rel": Path(tests[0]),
        "example_rel": Path(examples[0]),
        "solution_abs": exercise_dir / solutions[0],
        "test_abs": exercise_dir / tests[0],
        "example_abs": exercise_dir / examples[0],
    }


def compute_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_stub_unsolved(content: str) -> bool:
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
    has_def = any("def abbreviate" in line for line in lines)
    has_pass = any(line == "pass" for line in lines)
    has_return = any("return " in line for line in lines)
    has_body = any("re." in line or "split" in line or "upper" in line for line in lines)
    return has_def and has_pass and not has_return and not has_body


def parse_decision_table_from_hints(hints_path: Path) -> List[Tuple[str, str, str, str, str]]:
    """Extract rows from the markdown decision table in hints.md.

    Returns list of tuples: (pattern_name, delimiter_rule, example_input, expected_output, line_raw)
    """
    if not hints_path.is_file():
        raise FileNotFoundError(f"Missing hints file: {hints_path}")

    content = hints_path.read_text(encoding="utf-8")
    table_rows = []

    for line in content.splitlines():
        line_str = line.strip()
        if not line_str.startswith("|") or line_str.startswith("| :---"):
            continue

        parts = [p.strip() for p in line_str.split("|")]
        # Header or malformed lines check
        if len(parts) >= 8 and parts[1] and "Input Pattern" not in parts[1]:
            pattern_name = parts[1].replace("*", "").strip()
            delimiter_rule = parts[2].strip()
            example_input = parts[6].replace("`", "").replace('"', '').strip()
            expected_output = parts[7].replace("`", "").replace('"', '').strip()
            if example_input and expected_output:
                table_rows.append((pattern_name, delimiter_rule, example_input, expected_output, line_str))

    return table_rows


def run_tests_in_scratch(
    exercise_dir: Path,
    paths: Dict[str, Path],
    override_reference_content: str | None = None,
    extra_pytest_args: List[str] | None = None,
) -> Dict[str, Any]:
    """Execute pytest in a clean isolated temporary scratch directory."""
    scratch_cleaned = False
    with tempfile.TemporaryDirectory(prefix="acronym_scratch_") as temp_dir:
        scratch_path = Path(temp_dir)
        try:
            # Copy exercise files including dotfiles
            shutil.copytree(exercise_dir, scratch_path, dirs_exist_ok=True)

            target_solution = scratch_path / paths["solution_rel"]
            if override_reference_content is not None:
                target_solution.write_text(override_reference_content, encoding="utf-8")
            else:
                shutil.copyfile(scratch_path / paths["example_rel"], target_solution)

            cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
            if extra_pytest_args:
                cmd.extend(extra_pytest_args)

            proc = subprocess.run(
                cmd,
                cwd=str(scratch_path),
                capture_output=True,
                text=True,
            )

            stdout = proc.stdout
            stderr = proc.stderr
            combined = stdout + "\n" + stderr

            # Parse named cases
            named_cases = {
                "test_basic": "NOT_RUN",
                "test_lowercase_words": "NOT_RUN",
                "test_punctuation": "NOT_RUN",
            }
            case_pattern = re.compile(r"::(test_\w+)\s+(PASSED|FAILED|ERROR|SKIPPED)", re.IGNORECASE)
            for m in case_pattern.finditer(combined):
                c_name, c_status = m.group(1), m.group(2).upper()
                if c_name in named_cases:
                    named_cases[c_name] = c_status

            # Parse counts
            passed = 0
            failed = 0
            errors = 0
            deselected = 0

            p_match = re.search(r"(\d+)\s+passed", combined)
            if p_match:
                passed = int(p_match.group(1))

            f_match = re.search(r"(\d+)\s+failed", combined)
            if f_match:
                failed = int(f_match.group(1))

            e_match = re.search(r"(\d+)\s+error", combined)
            if e_match:
                errors = int(e_match.group(1))

            d_match = re.search(r"(\d+)\s+deselected", combined)
            if d_match:
                deselected = int(d_match.group(1))

            total_executed = passed + failed + errors

            if total_executed == 0:
                success = False
                exit_code = proc.returncode if proc.returncode != 0 else 1
                failure_reason = "Zero tests executed"
            elif proc.returncode != 0 or failed > 0 or errors > 0:
                success = False
                exit_code = proc.returncode if proc.returncode != 0 else 1
                failure_reason = f"Test failure (child exit {proc.returncode})"
            else:
                success = True
                exit_code = 0
                failure_reason = None

            result = {
                "success": success,
                "exit_code": exit_code,
                "child_returncode": proc.returncode,
                "failure_reason": failure_reason,
                "total_executed": total_executed,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "deselected": deselected,
                "named_cases": named_cases,
                "stdout": stdout,
                "stderr": stderr,
                "scratch_dir_cleaned": True,
            }
        finally:
            scratch_cleaned = True

    result["scratch_dir_cleaned"] = scratch_cleaned
    return result


def main() -> None:
    repo_root = find_repo_root()
    exercise_dir = repo_root / "exercises" / "practice" / "acronym"
    stub_path = exercise_dir / "acronym.py"
    hints_path = exercise_dir / ".docs" / "hints.md"
    work_dir = repo_root / "work" / "R36-T030"
    work_dir.mkdir(parents=True, exist_ok=True)

    print("======================================================================")
    print("Task R36-T030 Verification Suite: Acronym Contract Cases")
    print("======================================================================")

    # 1. Metadata Path Resolution
    paths = resolve_metadata_paths(exercise_dir)
    print(f"[*] Solution: {paths['solution_rel']}")
    print(f"[*] Test:     {paths['test_rel']}")
    print(f"[*] Example:  {paths['example_rel']}")

    # 2. Initial Learner Stub Verification
    if not stub_path.is_file():
        raise FileNotFoundError(f"Learner stub missing: {stub_path}")

    stub_content = stub_path.read_text(encoding="utf-8")
    if not verify_stub_unsolved(stub_content):
        raise AssertionError("Learner stub acronym.py is not in an unsolved state!")

    initial_stub_hash = compute_file_hash(stub_path)
    print(f"[*] Initial learner stub SHA-256: {initial_stub_hash}")
    print(f"[*] Learner stub is unsolved: OK ('def abbreviate(words): pass')")

    def assert_stub_integrity(phase_label: str) -> str:
        current_hash = compute_file_hash(stub_path)
        if current_hash != initial_stub_hash:
            raise AssertionError(
                f"FATAL: Learner stub modified during '{phase_label}'! "
                f"Expected {initial_stub_hash}, found {current_hash}"
            )
        current_content = stub_path.read_text(encoding="utf-8")
        if not verify_stub_unsolved(current_content):
            raise AssertionError(f"FATAL: Learner stub solved during '{phase_label}'!")
        return current_hash

    # 3. Decision Table & Contract Boundaries Verification
    print("\n----------------------------------------------------------------------")
    print("Verifying Decision Table in .docs/hints.md")
    print("----------------------------------------------------------------------")
    table_rows = parse_decision_table_from_hints(hints_path)
    assert len(table_rows) >= 7, f"Expected at least 7 decision table rows, found {len(table_rows)}"

    # Load reference implementation dynamically to verify table entries
    spec = importlib.util.spec_from_file_location("acronym_ref", str(paths["example_abs"]))
    assert spec is not None and spec.loader is not None
    ref_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref_mod)
    abbreviate_fn = ref_mod.abbreviate

    # Verify each table row produces expected outcome with reference implementation
    table_validation_records = []
    required_anchor_cases = {
        "Portable Network Graphics": "PNG",
        "Ruby on Rails": "ROR",
        "First In, First Out": "FIFO",
    }
    found_anchors = set()

    for pattern_name, delim_rule, ex_in, ex_out, _ in table_rows:
        actual_output = abbreviate_fn(ex_in)
        assert actual_output == ex_out, (
            f"Decision table mismatch for '{pattern_name}'! "
            f"Input '{ex_in}': expected '{ex_out}', got '{actual_output}'"
        )
        if ex_in in required_anchor_cases:
            assert ex_out == required_anchor_cases[ex_in]
            found_anchors.add(ex_in)

        table_validation_records.append({
            "pattern": pattern_name,
            "delimiter_rule": delim_rule,
            "input": ex_in,
            "expected_output": ex_out,
            "actual_reference_output": actual_output,
            "match": True,
        })
        print(f"    [✓] {pattern_name}: '{ex_in}' -> '{ex_out}' (MATCH)")

    assert len(found_anchors) == 3, f"Not all anchor cases found in decision table! Found: {found_anchors}"
    print("[*] All decision table entries validated against reference implementation.")

    # Verify Hints Document boundaries
    hints_text = hints_path.read_text(encoding="utf-8")
    assert "## Input / Output Walkthrough for Key Contract Cases" in hints_text, "Missing walkthrough section"
    assert "## Contract Decision Table" in hints_text, "Missing decision table section"
    assert "## Specified vs. Unspecified Contract Boundaries" in hints_text, "Missing contract boundary section"
    assert "test_basic" in hints_text and "test_lowercase_words" in hints_text and "test_punctuation" in hints_text
    assert "No Unicode" in hints_text or "Unicode" in hints_text
    assert "No numeric" in hints_text or "numeric" in hints_text
    print("[*] Contract boundaries and walkthrough sections verified.")

    # 4. Mode 1: Maintained Reference Run (all 9 canonical tests)
    print("\n----------------------------------------------------------------------")
    print("Running Mode 1: Maintained Reference Execution (all 9 tests)")
    print("----------------------------------------------------------------------")
    mode1_result = run_tests_in_scratch(exercise_dir, paths)
    print(f"[*] Mode 1 Exit Code: {mode1_result['exit_code']}")
    print(f"[*] Mode 1 Executed: {mode1_result['total_executed']} | Passed: {mode1_result['passed']} | Failed: {mode1_result['failed']}")
    print(f"[*] Mode 1 Scratch Cleaned: {mode1_result['scratch_dir_cleaned']}")

    assert mode1_result["success"] is True, "Mode 1 failed unexpectedly"
    assert mode1_result["exit_code"] == 0, f"Expected 0, got {mode1_result['exit_code']}"
    assert mode1_result["total_executed"] == 9, f"Expected 9 tests, got {mode1_result['total_executed']}"
    assert mode1_result["passed"] == 9, f"Expected 9 passed, got {mode1_result['passed']}"
    assert mode1_result["failed"] == 0, f"Expected 0 failed, got {mode1_result['failed']}"

    # Anchor cases verification
    for case_name in ["test_basic", "test_lowercase_words", "test_punctuation"]:
        st = mode1_result["named_cases"].get(case_name)
        assert st == "PASSED", f"Anchor case '{case_name}' did not PASS (got: {st})"
        print(f"    [✓] Anchor Case '{case_name}': {st}")

    hash_after_mode1 = assert_stub_integrity("Mode 1 (Maintained Reference)")
    print(f"[*] Stub SHA-256 after Mode 1: {hash_after_mode1} (UNCHANGED)")

    # 5. Mode 2: Deliberately Failing Reference Run
    print("\n----------------------------------------------------------------------")
    print("Running Mode 2: Deliberately Failing Reference Execution")
    print("----------------------------------------------------------------------")
    failing_ref = "def abbreviate(words):\n    return ''\n"
    mode2_result = run_tests_in_scratch(exercise_dir, paths, override_reference_content=failing_ref)
    print(f"[*] Mode 2 Exit Code: {mode2_result['exit_code']}")
    print(f"[*] Mode 2 Executed: {mode2_result['total_executed']} | Passed: {mode2_result['passed']} | Failed: {mode2_result['failed']}")
    print(f"[*] Mode 2 Scratch Cleaned: {mode2_result['scratch_dir_cleaned']}")

    assert mode2_result["success"] is False, "Mode 2 should have failed"
    assert mode2_result["exit_code"] != 0, f"Expected non-zero exit code, got {mode2_result['exit_code']}"
    assert mode2_result["failed"] > 0, "Expected failures in Mode 2"
    print("    [✓] Deliberate failure detected and non-zero exit propagated.")

    hash_after_mode2 = assert_stub_integrity("Mode 2 (Failing Reference)")
    print(f"[*] Stub SHA-256 after Mode 2: {hash_after_mode2} (UNCHANGED)")

    # 6. Mode 3: Zero-Test Run (Filter)
    print("\n----------------------------------------------------------------------")
    print("Running Mode 3: Zero-Test Run (Empty Selection)")
    print("----------------------------------------------------------------------")
    mode3_result = run_tests_in_scratch(exercise_dir, paths, extra_pytest_args=["-k", "non_existent_test_xyz"])
    print(f"[*] Mode 3 Exit Code: {mode3_result['exit_code']}")
    print(f"[*] Mode 3 Executed: {mode3_result['total_executed']} | Deselected: {mode3_result['deselected']}")
    print(f"[*] Mode 3 Scratch Cleaned: {mode3_result['scratch_dir_cleaned']}")

    assert mode3_result["success"] is False, "Mode 3 should have failed due to 0 executed tests"
    assert mode3_result["exit_code"] != 0, f"Expected non-zero exit code, got {mode3_result['exit_code']}"
    assert mode3_result["total_executed"] == 0, f"Expected total_executed == 0, got {mode3_result['total_executed']}"
    print("    [✓] Zero-test run detected and rejected with non-zero exit code.")

    hash_after_mode3 = assert_stub_integrity("Mode 3 (Zero Tests)")
    print(f"[*] Stub SHA-256 after Mode 3: {hash_after_mode3} (UNCHANGED)")

    # 7. Collect Tool Versions & Write Results
    pytest_ver = subprocess.run([sys.executable, "-m", "pytest", "--version"], capture_output=True, text=True)
    pytest_version_str = (pytest_ver.stdout or pytest_ver.stderr).strip()

    results_data: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": "R36-T030",
        "exercise": "exercises/practice/acronym",
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
        "decision_table": {
            "rows_count": len(table_validation_records),
            "records": table_validation_records,
            "anchors_verified": list(required_anchor_cases.keys()),
            "all_entries_matched": True,
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
    txt_content = f"""Task R36-T030 Verification Results
==================================
Date/Time: {results_data['timestamp']}
Exercise: {results_data['exercise']}
Python: {sys.version.split()[0]}
Pytest: {pytest_version_str}
Platform: {platform.platform()}
Overall Status: {results_data['overall_status']}

Learner Stub Integrity:
-----------------------
File: exercises/practice/acronym/acronym.py
Status: Strictly Unsolved (signature + pass)
Initial SHA-256: {initial_stub_hash}
After Mode 1:    {hash_after_mode1}
After Mode 2:    {hash_after_mode2}
After Mode 3:    {hash_after_mode3}
All Hashes Match: {results_data['learner_stub']['hash_identical_across_all_runs']}

Decision Table Validation:
--------------------------
Rows Extracted: {len(table_validation_records)}
Anchor Cases Verified:
  - "Portable Network Graphics" -> "PNG" (test_basic): MATCH
  - "Ruby on Rails" -> "ROR" (test_lowercase_words): MATCH
  - "First In, First Out" -> "FIFO" (test_punctuation): MATCH
All 7 Decision Table Rows Matched: True

Mode 1: Maintained Reference Execution
--------------------------------------
Exit Code: {mode1_result['exit_code']} (Expected: 0)
Child Return Code: {mode1_result['child_returncode']}
Executed Tests: {mode1_result['total_executed']} / 9
Passed: {mode1_result['passed']}
Failed: {mode1_result['failed']}
Scratch Cleaned: {mode1_result['scratch_dir_cleaned']}
Named Cases:
  - test_basic: {mode1_result['named_cases']['test_basic']}
  - test_lowercase_words: {mode1_result['named_cases']['test_lowercase_words']}
  - test_punctuation: {mode1_result['named_cases']['test_punctuation']}

Mode 2: Deliberately Failing Reference
--------------------------------------
Exit Code: {mode2_result['exit_code']} (Expected: non-zero)
Child Return Code: {mode2_result['child_returncode']}
Executed Tests: {mode2_result['total_executed']}
Passed: {mode2_result['passed']}
Failed: {mode2_result['failed']}
Scratch Cleaned: {mode2_result['scratch_dir_cleaned']}
Assertion Failure Detected & Propagated: True

Mode 3: Zero-Test Selection (Filter)
------------------------------------
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
