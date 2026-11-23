#!/usr/bin/env python3
"""
Verification check for Task R36-T036:
Explain two approaches to diffie-hellman in Python [exercises/practice/diffie-hellman]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "diffie-hellman")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T036")
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

    # Verify hints documentation
    hints_file = os.path.join(exercise_dir, ".docs", "hints.md")
    assert os.path.exists(hints_file), f"Missing {hints_file}"
    with open(hints_file, "r", encoding="utf-8") as f:
        hints_text = f.read()
    assert "pow(g, private, p)" in hints_text
    assert "secrets" in hints_text

    # 2. Test reference implementation in scratch dir
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_ref = os.path.join(tmp_dir, "dh_ref")
        shutil.copytree(exercise_dir, scratch_ref, symlinks=True)
        shutil.copyfile(orig_example_path, os.path.join(scratch_ref, solution_rel))

        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(cmd, cwd=scratch_ref, capture_output=True, text=True)
        assert proc.returncode == 0, f"Reference tests failed: {proc.stdout}\n{proc.stderr}"
        ref_stdout = proc.stdout

    # 3. Test alternative implementation in scratch dir
    alt_file = os.path.join(work_dir, "alternative.py")
    assert os.path.exists(alt_file), f"Missing {alt_file}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_alt = os.path.join(tmp_dir, "dh_alt")
        shutil.copytree(exercise_dir, scratch_alt, symlinks=True)
        shutil.copyfile(alt_file, os.path.join(scratch_alt, solution_rel))

        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(cmd, cwd=scratch_alt, capture_output=True, text=True)
        assert proc.returncode == 0, f"Alternative tests failed: {proc.stdout}\n{proc.stderr}"
        alt_stdout = proc.stdout

        words = alt_stdout.split()
        passed_count = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed_count = int(words[i - 1])
                except ValueError:
                    pass
        assert passed_count >= 6, f"Expected at least 6 passed tests, got {passed_count}"

    results = {
        "task_id": "R36-T036",
        "exercise": "exercises/practice/diffie-hellman",
        "reference_passed": True,
        "alternative_passed": True,
        "tests_passed": passed_count,
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T036 Verification Report\nStatus: PASS\nBoth Reference and Alternative Passed {passed_count} tests.\n")

    print(f"\nCheck R36-T036 successfully passed all assertions! ({passed_count} tests passed)")


if __name__ == "__main__":
    main()
