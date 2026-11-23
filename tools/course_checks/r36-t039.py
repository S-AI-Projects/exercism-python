#!/usr/bin/env python3
"""
tools/course_checks/r36-t039.py
Isolated runner for exercises/practice/isogram.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def run_isolated_isogram_check():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_dir = os.path.join(repo_root, "exercises", "practice", "isogram")
    config_file = os.path.join(exercise_dir, ".meta", "config.json")

    assert os.path.exists(config_file), f"Missing config file: {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    orig_solution = os.path.join(exercise_dir, solution_rel)
    orig_example = os.path.join(exercise_dir, example_rel)

    # Ensure learner stub is unsolved
    with open(orig_solution, "r", encoding="utf-8") as f:
        assert "pass" in f.read(), "Learner stub must remain unsolved!"

    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch = os.path.join(tmp_dir, "isogram")
        shutil.copytree(exercise_dir, scratch, symlinks=True)
        shutil.copyfile(orig_example, os.path.join(scratch, solution_rel))

        cmd = [sys.executable, "-m", "pytest", "-q"]
        proc = subprocess.run(cmd, cwd=scratch, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise RuntimeError(f"Pytest failed with exit code {proc.returncode}")

        # Check named test cases exist and passed
        test_file = os.path.join(scratch, test_rel)
        with open(test_file, "r", encoding="utf-8") as f:
            t_content = f.read()
        assert "def test_empty_string" in t_content
        assert "def test_isogram_with_only_lower_case_characters" in t_content
        assert "def test_word_with_one_duplicated_character" in t_content

        words = proc.stdout.split()
        passed = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed = int(words[i - 1])
                except ValueError:
                    pass
        assert passed >= 14, f"Expected at least 14 passed tests, got {passed}"

    print(f"Isolated isogram runner passed: {passed} tests verified successfully.")
    return True


if __name__ == "__main__":
    run_isolated_isogram_check()
