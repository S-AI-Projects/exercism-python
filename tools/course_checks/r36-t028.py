#!/usr/bin/env python3
"""
Metadata path and configuration checker for Task R36-T028:
Validates exercises/practice/luhn/.meta/config.json and verifies rejection
of deliberately invalid metadata fixtures.

Checks:
1. Parse the 'files' mapping in config.json.
2. Resolve each declared path strictly inside the exercise directory.
3. Reject parent directory traversal ('..') or absolute paths.
4. Verify every declared file physically exists.
5. Test three deliberately invalid metadata fixtures:
   - Missing reference (declared example file does not exist)
   - Missing test (declared test file does not exist)
   - Outside-exercise path traversal (declared path escapes exercise directory)
6. Assert that all three invalid fixtures fail for their intended reasons
   while the real metadata configuration passes.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


REQUIRED_ROLES = ["solution", "test", "example"]


def validate_exercise_config(config_dict: dict[str, Any], exercise_dir: Path) -> tuple[bool, str]:
    """
    Validate the 'files' object in an exercise configuration.
    
    Returns (True, "OK") if all declared files exist inside exercise_dir without traversal.
    Returns (False, error_message) on any mismatch, missing file, or path violation.
    """
    if "files" not in config_dict:
        return False, "Configuration missing required 'files' mapping"

    files_obj = config_dict["files"]
    base_resolved = exercise_dir.resolve()

    for role in REQUIRED_ROLES:
        if role not in files_obj:
            return False, f"Missing required file role: '{role}'"

        declared_files = files_obj[role]
        if not isinstance(declared_files, list) or len(declared_files) == 0:
            return False, f"Role '{role}' must be a non-empty list of file paths"

        for file_str in declared_files:
            file_path = Path(file_str)

            # Reject absolute paths
            if file_path.is_absolute() or file_str.startswith("/"):
                return False, f"Illegal absolute path for role '{role}': '{file_str}'"

            # Reject parent traversal ('..')
            if ".." in file_path.parts:
                return False, f"Illegal parent traversal in path for role '{role}': '{file_str}'"

            # Resolve target and ensure it stays within exercise_dir
            resolved_target = (exercise_dir / file_path).resolve()
            try:
                resolved_target.relative_to(base_resolved)
            except ValueError:
                return False, f"Path for role '{role}' resolves outside exercise boundary: '{file_str}'"

            # Check that declared file physically exists
            if not resolved_target.is_file():
                return False, f"Declared file for role '{role}' does not exist: '{file_str}' (resolved to {resolved_target})"

    return True, "Valid metadata configuration"


def run_checks() -> dict[str, Any]:
    script_path = Path(__file__).resolve()
    # Script located at tools/course_checks/r36-t028.py -> repo_root is parents[2]
    repo_root = script_path.parents[2]
    exercise_dir = repo_root / "exercises" / "practice" / "luhn"
    config_file = exercise_dir / ".meta" / "config.json"

    print(f"[*] Repository root: {repo_root}")
    print(f"[*] Target exercise directory: {exercise_dir}")
    print(f"[*] Target config file: {config_file}")

    assert config_file.is_file(), f"Target config file missing at {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        real_config = json.load(f)

    # 1. Validate real metadata configuration
    real_valid, real_msg = validate_exercise_config(real_config, exercise_dir)
    print(f"[*] Real configuration validation: valid={real_valid}, msg='{real_msg}'")
    assert real_valid, f"Real configuration failed validation: {real_msg}"

    # 2. Test Fixture 1: Missing reference file
    fixture_missing_ref = json.loads(json.dumps(real_config))
    fixture_missing_ref["files"]["example"] = [".meta/non_existent_example.py"]
    ref_valid, ref_msg = validate_exercise_config(fixture_missing_ref, exercise_dir)
    print(f"[*] Fixture 1 (Missing Reference) validation: valid={ref_valid}, msg='{ref_msg}'")
    assert not ref_valid, "Fixture 1 should have failed for missing reference, but passed!"
    assert "example" in ref_msg and "does not exist" in ref_msg, f"Unexpected error message for Fixture 1: {ref_msg}"

    # 3. Test Fixture 2: Missing test file
    fixture_missing_test = json.loads(json.dumps(real_config))
    fixture_missing_test["files"]["test"] = ["non_existent_luhn_test.py"]
    test_valid, test_msg = validate_exercise_config(fixture_missing_test, exercise_dir)
    print(f"[*] Fixture 2 (Missing Test) validation: valid={test_valid}, msg='{test_msg}'")
    assert not test_valid, "Fixture 2 should have failed for missing test, but passed!"
    assert "test" in test_msg and "does not exist" in test_msg, f"Unexpected error message for Fixture 2: {test_msg}"

    # 4. Test Fixture 3: Outside-exercise path traversal
    fixture_traversal = json.loads(json.dumps(real_config))
    fixture_traversal["files"]["solution"] = ["../outside_solution.py"]
    trav_valid, trav_msg = validate_exercise_config(fixture_traversal, exercise_dir)
    print(f"[*] Fixture 3 (Path Traversal) validation: valid={trav_valid}, msg='{trav_msg}'")
    assert not trav_valid, "Fixture 3 should have failed for path traversal, but passed!"
    assert ("parent traversal" in trav_msg or "outside" in trav_msg), f"Unexpected error message for Fixture 3: {trav_msg}"

    print("[+] All metadata checks and invalid fixture tests passed successfully.")

    return {
        "real_config_status": {
            "valid": real_valid,
            "message": real_msg,
            "resolved_files": {
                role: [str((exercise_dir / p).resolve().relative_to(repo_root)) for p in real_config["files"][role]]
                for role in REQUIRED_ROLES
            },
        },
        "fixtures": {
            "missing_reference": {
                "rejected": not ref_valid,
                "expected_rejection": True,
                "error_message": ref_msg,
            },
            "missing_test": {
                "rejected": not test_valid,
                "expected_rejection": True,
                "error_message": test_msg,
            },
            "path_traversal": {
                "rejected": not trav_valid,
                "expected_rejection": True,
                "error_message": trav_msg,
            },
        },
    }


def main() -> int:
    try:
        run_checks()
        return 0
    except AssertionError as e:
        print(f"[!] Verification failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[!] Unexpected error during verification: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
