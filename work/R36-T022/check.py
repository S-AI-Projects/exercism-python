#!/usr/bin/env python3
"""
Automated verification check for Task R36-T022:
Make the space-age test-generation path reproducible.

Requirements:
1. Resolve solution/test/example paths from exercises/practice/space-age/.meta/config.json.
2. Use Python subprocess and a temporary directory.
3. Copy exercise including dotfiles, substitute the reference implementation only
   in that copy, and run: python3 -m pytest -q.
4. Check child return codes and test counts; ensure the working tree is not rewritten.
5. Verify named cases (test_age_on_earth, test_age_on_mercury, test_age_on_venus)
   and all enabled cases pass; verify learner stub in working tree remains unsolved.
6. Check reports number of executed cases and fails on zero-test run, non-zero exit or assertion failure.
7. Verify two generations yield the same tests after documented timestamp normalization;
   verify no case is silently dropped.
8. Save inputs, expected vs actual results, and tool versions in work/R36-T022/.
9. Exit non-zero on any failure or assertion error.
"""

from __future__ import annotations

import difflib
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


ANCHORED_CASES = [
    "test_age_on_earth",
    "test_age_on_mercury",
    "test_age_on_venus",
]

ALL_ENABLED_CASES = [
    "test_age_on_earth",
    "test_age_on_mercury",
    "test_age_on_venus",
    "test_age_on_mars",
    "test_age_on_jupiter",
    "test_age_on_saturn",
    "test_age_on_uranus",
    "test_age_on_neptune",
]


def find_spec_path(repo_root: Path) -> Path | None:
    candidates = [
        repo_root / ".problem-specifications",
        Path("/tmp/problem-specifications"),
        Path.home() / ".cache/exercism/problem-specifications",
    ]
    for c in candidates:
        if (c / "exercises/space-age/canonical-data.json").is_file():
            return c
    return None


def run_single_generation(repo_root: Path, target_dir: Path, spec_path: Path | None) -> Path:
    shutil.copytree(repo_root / "config", target_dir / "config")
    shutil.copytree(repo_root / "bin", target_dir / "bin")
    exercise_dest = target_dir / "exercises/practice/space-age"
    shutil.copytree(repo_root / "exercises/practice/space-age", exercise_dest)

    cmd = [sys.executable, "bin/generate_tests.py"]
    if spec_path:
        cmd.extend(["-p", str(spec_path)])
    cmd.append("space-age")

    proc = subprocess.run(cmd, cwd=str(target_dir), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Generation failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

    out_file = exercise_dest / "space_age_test.py"
    assert out_file.is_file(), f"Generated test file not found at {out_file}"
    return out_file


def normalize_header(lines: list[str]) -> list[str]:
    # Skip lines 1-3 which contain the dynamically generated date timestamp
    if len(lines) >= 3 and lines[0].startswith("# These tests are auto-generated"):
        return lines[3:]
    return lines


def main() -> int:
    print("[*] Starting automated check for Task R36-T022 (space-age)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/space-age")
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

    # 2. Verify working tree learner stub is unsolved
    assert working_solution_file.is_file(), "Learner solution file missing"
    with open(working_solution_file, "r", encoding="utf-8") as f:
        stub_content = f.read()

    is_stub_unsolved = "pass" in stub_content and "31558149" not in stub_content
    assert is_stub_unsolved, "Working tree learner stub has been modified or solved!"
    print("[+] Verified learner stub in working tree is unsolved.")

    # 3. Verify tests.toml parsing and inclusion counts
    assert tests_toml_file.is_file(), f"tests.toml missing at {tests_toml_file}"
    with open(tests_toml_file, "rb") as f:
        toml_data = tomllib.load(f)

    total_cases = len(toml_data)
    included_count = sum(1 for entry in toml_data.values() if entry.get("include") is not False)
    excluded_count = sum(1 for entry in toml_data.values() if entry.get("include") is False)

    print(f"[*] Canonical cases in tests.toml: total={total_cases}, included={included_count}, excluded={excluded_count}")
    assert total_cases == 9, f"Expected 9 canonical cases in tests.toml, found {total_cases}"
    assert included_count == 8, f"Expected 8 included cases, found {included_count}"
    assert excluded_count == 1, f"Expected 1 excluded case, found {excluded_count}"

    # Verify excluded case is invalid planet
    excluded_entries = [u for u, e in toml_data.items() if e.get("include") is False]
    assert len(excluded_entries) == 1, "Expected exactly 1 excluded entry"
    assert "57b96e2a-1178-40b7-b34d-f3c9c34e4bf4" in excluded_entries
    print("[+] Verified canonical test counts: 8 included, 1 excluded (invalid planet).")

    # 4. Scratch Test Execution against Reference Solution
    with tempfile.TemporaryDirectory() as scratch_tmp_str:
        scratch_tmp = Path(scratch_tmp_str)
        scratch_exercise = scratch_tmp / "exercise"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        scratch_sol = scratch_exercise / solution_rel
        scratch_ex = scratch_exercise / example_rel

        # Substitute reference into scratch solution file only
        shutil.copyfile(scratch_ex, scratch_sol)

        print("[*] Running pytest against reference implementation in scratch copy...")
        proc_pytest = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )

        child_exit_code = proc_pytest.returncode
        child_stdout = proc_pytest.stdout
        child_stderr = proc_pytest.stderr

        print(f"[*] Child return code: {child_exit_code}")
        print(f"[*] Pytest stdout:\n{child_stdout.strip()}")
        if child_stderr:
            print(f"[*] Pytest stderr:\n{child_stderr.strip()}")

        assert child_exit_code == 0, f"pytest run failed with exit code {child_exit_code}"

        # Parse test count from stdout
        match = re.search(r"(\d+)\s+passed", child_stdout)
        assert match is not None, f"Could not parse passed test count from stdout:\n{child_stdout}"
        passed_count = int(match.group(1))

        print(f"[+] Reported executed cases: {passed_count}")
        assert passed_count > 0, "Zero tests executed!"
        assert passed_count == 8, f"Expected 8 passed tests, got {passed_count}"

        # Run with -v to verify individual test cases
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=str(scratch_exercise),
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, "pytest -v run failed"

        test_run_details = {}
        for c in ALL_ENABLED_CASES:
            assert f"{c} PASSED" in proc_v.stdout, f"Case {c} did not pass!"
            test_run_details[c] = "PASSED"

        print("[+] Verified all 8 enabled test cases passed against reference.")
        for ac in ANCHORED_CASES:
            print(f"    - Anchored case {ac}: {test_run_details[ac]}")

    # 5. Verify working tree solution file was not modified
    with open(working_solution_file, "r", encoding="utf-8") as f:
        post_test_stub = f.read()
    assert post_test_stub == stub_content, "Working tree solution file was unexpectedly modified!"
    print("[+] Confirmed working tree learner stub was untouched.")

    # 6. Two Fresh Generations Round-Trip & Reproducibility Check
    spec_path = find_spec_path(repo_root)
    print(f"[*] Spec path for regeneration check: {spec_path or 'auto-clone'}")

    with tempfile.TemporaryDirectory() as gen_tmp1_str, tempfile.TemporaryDirectory() as gen_tmp2_str:
        gen_tmp1 = Path(gen_tmp1_str)
        gen_tmp2 = Path(gen_tmp2_str)

        print("[*] Generating run 1 in temporary workspace...")
        g1_path = run_single_generation(repo_root, gen_tmp1, spec_path)
        print("[*] Generating run 2 in temporary workspace...")
        g2_path = run_single_generation(repo_root, gen_tmp2, spec_path)

        content1 = g1_path.read_text(encoding="utf-8")
        content2 = g2_path.read_text(encoding="utf-8")

        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        norm1 = normalize_header(lines1)
        norm2 = normalize_header(lines2)

        generations_identical = (norm1 == norm2)
        assert generations_identical, "Regenerations produced differing test files beyond header timestamp!"
        print("[+] Two generations yield the exact same tests after documented timestamp normalization.")

        # Ensure no cases are silently dropped
        gen_cases = [l.strip() for l in lines1 if l.strip().startswith("def test_")]
        assert len(gen_cases) == 8, f"Expected 8 generated test cases, got {len(gen_cases)}"
        for ac in ANCHORED_CASES:
            assert f"def {ac}(self):" in content1, f"Anchored case {ac} was dropped in generation!"
        print("[+] Verified no test cases were silently dropped.")

    # 7. Save results, expected vs actual, inputs, and tool versions to work/R36-T022/
    results_record = {
        "task_id": "R36-T022",
        "exercise": "exercises/practice/space-age",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "tests_toml_file": str(tests_toml_file.relative_to(repo_root)),
            "template_file": "exercises/practice/space-age/.meta/template.j2",
            "macros_file": "config/generator_macros.j2",
            "anchored_cases": ANCHORED_CASES,
            "enabled_cases": ALL_ENABLED_CASES,
            "spec_path_used": str(spec_path) if spec_path else "auto-clone",
        },
        "counts": {
            "total_canonical_cases": total_cases,
            "included": included_count,
            "excluded": excluded_count,
            "generated_tests_count": len(gen_cases),
        },
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
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
            "executed_test_count": {
                "expected": 8,
                "actual": passed_count,
                "status": "PASS",
            },
            "anchored_cases_passed": {
                "expected": {c: "PASSED" for c in ANCHORED_CASES},
                "actual": {c: test_run_details[c] for c in ANCHORED_CASES},
                "status": "PASS",
            },
            "all_enabled_cases_passed": {
                "expected": {c: "PASSED" for c in ALL_ENABLED_CASES},
                "actual": test_run_details,
                "status": "PASS",
            },
            "two_generations_identical": {
                "expected": True,
                "actual": generations_identical,
                "status": "PASS",
            },
            "no_silent_drop": {
                "expected": True,
                "actual": True,
                "status": "PASS",
            },
            "working_tree_unchanged": {
                "expected": True,
                "actual": True,
                "status": "PASS",
            },
        },
        "summary": "All checks and assertions passed successfully.",
    }

    json_out = work_dir / "results.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {json_out}")

    txt_out = work_dir / "results.txt"
    with open(txt_out, "w", encoding="utf-8") as f:
        f.write("Task R36-T022 Automated Check Verification Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Tool Versions:\n  Python: {py_version.splitlines()[0]}\n  Pytest: {pytest_version}\n  Platform: {platform_info}\n\n")
        f.write(f"Canonical Cases:\n  Total: {total_cases}\n  Included: {included_count}\n  Excluded: {excluded_count}\n\n")
        f.write("Anchored Cases (3/3 Verified):\n")
        for ac in ANCHORED_CASES:
            f.write(f"  - {ac}: {test_run_details[ac]}\n")
        f.write("\nPytest Scratch Execution:\n")
        f.write(f"  Exit code: {child_exit_code}\n")
        f.write(f"  Executed cases: {passed_count}\n")
        f.write(f"  Zero-test run: False\n")
        f.write("\nTwo-Generation Reproducibility:\n")
        f.write(f"  Identical after timestamp normalization: PASS\n")
        f.write(f"  No cases silently dropped: PASS (8/8 generated)\n")
        f.write("\nWorking Tree Learner Stub:\n")
        f.write(f"  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks passed successfully.\n")
    print(f"[+] Saved text summary to {txt_out}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
