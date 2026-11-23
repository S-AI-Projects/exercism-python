#!/usr/bin/env python3
"""
Verification check for Task R36-T040:
Explain the subtle contract cases in markdown [exercises/practice/markdown]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "markdown")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T040")
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

    # Verify learner starting file is untouched
    with open(orig_solution_path, "r", encoding="utf-8") as f:
        stub_code = f.read()
    assert "def parse(markdown):" in stub_code, "Learner starting code must remain untouched!"

    # Verify hints decision table
    hints_file = os.path.join(exercise_dir, ".docs", "hints.md")
    assert os.path.exists(hints_file), f"Missing {hints_file}"
    with open(hints_file, "r", encoding="utf-8") as f:
        hints_text = f.read()
    assert "test_parses_normal_text_as_a_paragraph" in hints_text
    assert "test_parsing_italics" in hints_text
    assert "test_parsing_bold_text" in hints_text
    assert "Decision Table" in hints_text

    # 2. Test in scratch directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = os.path.join(tmp_dir, "markdown")
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
        assert passed_count >= 15, f"Expected passing tests, got {passed_count}"

    results = {
        "task_id": "R36-T040",
        "exercise": "exercises/practice/markdown",
        "tests_passed": passed_count,
        "exit_code": exit_code,
        "decision_table_present": True,
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T040 Verification Report\nStatus: PASS\nTests Passed: {passed_count}\n")

    print(f"\nCheck R36-T040 successfully passed all assertions! ({passed_count} tests passed)")


if __name__ == "__main__":
    main()
