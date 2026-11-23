#!/usr/bin/env python3
"""
Verification check for Task R36-T035:
Measure the scaling of the variable-length-quantity reference [exercises/practice/variable-length-quantity]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "variable-length-quantity")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T035")
    os.makedirs(work_dir, exist_ok=True)

    # 1. Config paths
    config_file = os.path.join(exercise_dir, ".meta", "config.json")
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    orig_solution_path = os.path.join(exercise_dir, solution_rel)
    orig_test_path = os.path.join(exercise_dir, test_rel)
    orig_example_path = os.path.join(exercise_dir, example_rel)

    # Verify learner stub is unsolved
    with open(orig_solution_path, "r", encoding="utf-8") as f:
        stub_code = f.read()
    assert "pass" in stub_code, "Learner stub must remain unsolved!"

    # Verify complexity comment
    with open(orig_example_path, "r", encoding="utf-8") as f:
        example_code = f.read()
    assert "Complexity & Invariant for encode_single" in example_code
    assert "O(log N)" in example_code or "O(log" in example_code

    # Verify documentation
    docs_path = os.path.join(repo_root, "docs", "maintenance", "variable-length-quantity.md")
    assert os.path.exists(docs_path), f"Missing {docs_path}"
    with open(docs_path, "r", encoding="utf-8") as f:
        docs_text = f.read()
    assert "0x40" in docs_text
    assert "0x2000" in docs_text
    assert "0x100000" in docs_text

    # 2. Test in scratch directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = os.path.join(tmp_dir, "vlq")
        shutil.copytree(exercise_dir, scratch_exercise, symlinks=True)
        shutil.copyfile(orig_example_path, os.path.join(scratch_exercise, solution_rel))

        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(cmd, cwd=scratch_exercise, capture_output=True, text=True)
        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode

        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

        assert exit_code == 0, f"pytest run failed with exit code {exit_code}"
        assert "passed" in stdout, "pytest output did not report passed tests"

        words = stdout.split()
        passed_count = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed_count = int(words[i - 1])
                except ValueError:
                    pass
        assert passed_count >= 30, f"Expected at least 30 passed tests, got {passed_count}"

    results = {
        "task_id": "R36-T035",
        "exercise": "exercises/practice/variable-length-quantity",
        "tests_passed": passed_count,
        "exit_code": exit_code,
        "complexity_documented": True,
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T035 Verification Report\nStatus: PASS\nTests Passed: {passed_count}\n")

    print("\nCheck R36-T035 successfully passed all assertions!")


if __name__ == "__main__":
    main()
