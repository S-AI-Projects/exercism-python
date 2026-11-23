#!/usr/bin/env python3
"""
Verification check for Task R36-T031:
Explain canonical-case decisions for minesweeper [exercises/practice/minesweeper]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "minesweeper")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T031")
    os.makedirs(work_dir, exist_ok=True)

    # 1. Parse config.json to resolve solution/test/example paths
    config_file = os.path.join(exercise_dir, ".meta", "config.json")
    assert os.path.exists(config_file), f"Missing config file: {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    orig_solution_path = os.path.join(exercise_dir, solution_rel)
    orig_test_path = os.path.join(exercise_dir, test_rel)
    orig_example_path = os.path.join(exercise_dir, example_rel)

    assert os.path.exists(orig_solution_path), f"Missing solution stub: {orig_solution_path}"
    assert os.path.exists(orig_test_path), f"Missing test file: {orig_test_path}"
    assert os.path.exists(orig_example_path), f"Missing example file: {orig_example_path}"

    # Verify learner stub is unsolved
    with open(orig_solution_path, "r", encoding="utf-8") as f:
        stub_code = f.read()
    assert "pass" in stub_code, "Learner stub must remain unsolved!"

    # 2. Parse and validate tests.toml
    tests_toml_path = os.path.join(exercise_dir, ".meta", "tests.toml")
    assert os.path.exists(tests_toml_path), f"Missing tests.toml: {tests_toml_path}"
    with open(tests_toml_path, "rb") as f:
        toml_data = tomllib.load(f)

    target_uuids = [
        "0c5ec4bd-dea7-4138-8651-1203e1cb9f44",
        "650ac4c0-ad6b-4b41-acde-e4ea5852c3b8",
        "6fbf8f6d-a03b-42c9-9a58-b489e9235478",
    ]

    total_cases = len(toml_data)
    included_count = sum(1 for v in toml_data.values() if v.get("include", True))
    excluded_count = sum(1 for v in toml_data.values() if not v.get("include", True))

    for uuid in target_uuids:
        assert uuid in toml_data, f"Target UUID {uuid} missing in tests.toml"
        entry = toml_data[uuid]
        assert "comment" in entry, f"Missing rationale comment key for UUID {uuid}"
        assert len(entry["comment"].strip()) > 10, f"Rationale comment too short for {uuid}"

    # 3. Verify documentation in docs/maintenance/minesweeper.md
    docs_maintenance = os.path.join(repo_root, "docs", "maintenance", "minesweeper.md")
    assert os.path.exists(docs_maintenance), f"Missing docs: {docs_maintenance}"
    with open(docs_maintenance, "r", encoding="utf-8") as f:
        docs_text = f.read()
    for uuid in target_uuids:
        assert uuid in docs_text, f"UUID {uuid} not mentioned in {docs_maintenance}"

    # 4. Copy exercise to scratch temp directory and run pytest
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = os.path.join(tmp_dir, "minesweeper")
        shutil.copytree(exercise_dir, scratch_exercise, symlinks=True)

        # Substitute the reference implementation into the solution filename
        scratch_solution = os.path.join(scratch_exercise, solution_rel)
        scratch_example = os.path.join(scratch_exercise, example_rel)
        shutil.copyfile(scratch_example, scratch_solution)

        # Run pytest
        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(
            cmd,
            cwd=scratch_exercise,
            capture_output=True,
            text=True
        )

        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode

        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        assert exit_code == 0, f"pytest run failed with exit code {exit_code}"
        assert "passed" in stdout, "pytest output did not report passed tests"

        # Check that named test cases executed and passed
        test_py = os.path.join(scratch_exercise, test_rel)
        with open(test_py, "r", encoding="utf-8") as f:
            test_content = f.read()
        assert "def test_no_rows" in test_content
        assert "def test_no_columns" in test_content
        assert "def test_no_mines" in test_content

        # Count total passed tests from output (e.g. "15 passed")
        words = stdout.split()
        passed_count = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed_count = int(words[i - 1])
                except ValueError:
                    pass
        assert passed_count >= 15, f"Expected at least 15 passing tests, got {passed_count}"

    # 5. Record results and tool versions
    results = {
        "task_id": "R36-T031",
        "exercise": "exercises/practice/minesweeper",
        "target_uuids": target_uuids,
        "total_canonical_cases": total_cases,
        "included_cases": included_count,
        "excluded_cases": excluded_count,
        "tests_passed": passed_count,
        "exit_code": exit_code,
        "python_version": sys.version,
        "pytest_version": subprocess.check_output([sys.executable, "-m", "pytest", "--version"]).decode().strip(),
        "learner_stub_unsolved": True,
        "toml_valid": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T031 Verification Report\n")
        f.write(f"Status: PASS\n")
        f.write(f"Total Canonical Cases: {total_cases} (Included: {included_count}, Excluded: {excluded_count})\n")
        f.write(f"Tests Passed: {passed_count}\n")
        f.write(f"Python: {sys.version}\n")

    print("\nCheck R36-T031 successfully passed all assertions!")


if __name__ == "__main__":
    main()
