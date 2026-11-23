#!/usr/bin/env python3
"""
Verification check for Task R36-T033:
Find a test that distinguishes a wrong grep implementation [exercises/practice/grep]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def get_mutant_code(orig_code):
    # Introduce deliberate mutant: if '-v' in flags: return pattern in line (instead of pattern not in line)
    target = "return pattern not in line"
    replacement = "return pattern in line"
    assert target in orig_code, f"Target pattern not found in example.py:\n{orig_code}"
    return orig_code.replace(target, replacement, 1)


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "grep")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T033")
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

    with open(orig_example_path, "r", encoding="utf-8") as f:
        reference_code = f.read()

    mutant_code = get_mutant_code(reference_code)

    # 2. Test reference in scratch directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_ref = os.path.join(tmp_dir, "grep_ref")
        shutil.copytree(exercise_dir, scratch_ref, symlinks=True)
        shutil.copyfile(orig_example_path, os.path.join(scratch_ref, solution_rel))

        proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=scratch_ref, capture_output=True, text=True)
        assert proc.returncode == 0, f"Reference implementation failed tests: {proc.stdout}\n{proc.stderr}"
        assert "passed" in proc.stdout, "Reference tests did not pass"
        words = proc.stdout.split()
        passed_count = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed_count = int(words[i - 1])
                except ValueError:
                    pass
        assert passed_count >= 25, f"Expected at least 25 passed tests, got {passed_count}"

    # 3. Test mutant in scratch directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_mutant = os.path.join(tmp_dir, "grep_mutant")
        shutil.copytree(exercise_dir, scratch_mutant, symlinks=True)
        with open(os.path.join(scratch_mutant, solution_rel), "w", encoding="utf-8") as f:
            f.write(mutant_code)

        proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=scratch_mutant, capture_output=True, text=True)
        # Mutant must fail!
        assert proc.returncode != 0, "Mutant unexpectedly passed all tests!"
        assert "FAILED" in proc.stdout or "failed" in proc.stdout, "Mutant must produce failures"
        assert "test_one_file_several_matches_inverted_flag" in proc.stdout or "test_multiple_files_several_matches_inverted_flag" in proc.stdout, (
            "Mutant failure was not caught by inverted flag tests!"
        )
        print(f"Mutant successfully rejected by test suite as expected:\n{proc.stdout.splitlines()[0]}")

    # 4. Verify documentation
    hints_file = os.path.join(exercise_dir, ".docs", "hints.md")
    assert os.path.exists(hints_file), f"Missing {hints_file}"
    docs_file = os.path.join(repo_root, "docs", "maintenance", "grep.md")
    assert os.path.exists(docs_file), f"Missing {docs_file}"

    results = {
        "task_id": "R36-T033",
        "exercise": "exercises/practice/grep",
        "reference_tests_passed": passed_count,
        "mutant_rejected": True,
        "rejecting_test": "test_one_file_several_matches_inverted_flag",
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T033 Verification Report\nStatus: PASS\nReference Tests: {passed_count}\nMutant Rejected: True\n")

    print("\nCheck R36-T033 successfully passed all assertions!")


if __name__ == "__main__":
    main()
