#!/usr/bin/env python3
"""
Verification check for Task R36-T032:
Make the etl test-generation path reproducible [exercises/practice/etl]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "etl")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T032")
    os.makedirs(work_dir, exist_ok=True)

    # 1. Check paths from config.json
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

    # Verify learner stub is unsolved
    with open(orig_solution_path, "r", encoding="utf-8") as f:
        stub_code = f.read()
    assert "pass" in stub_code, "Learner stub must remain unsolved!"

    # 2. Run reusable check tools/course_checks/r36-t032.py
    course_check_script = os.path.join(repo_root, "tools", "course_checks", "r36-t032.py")
    assert os.path.exists(course_check_script), f"Missing {course_check_script}"
    res = subprocess.run([sys.executable, course_check_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Course check failed: {res.stderr}\n{res.stdout}"

    # 3. Verify documentation in docs/maintenance/etl.md
    docs_maintenance = os.path.join(repo_root, "docs", "maintenance", "etl.md")
    assert os.path.exists(docs_maintenance), f"Missing docs: {docs_maintenance}"
    with open(docs_maintenance, "r", encoding="utf-8") as f:
        docs_text = f.read()
    assert "bin/generate_tests.py" in docs_text
    assert "test_single_letter" in docs_text
    assert "test_single_score_with_multiple_letters" in docs_text
    assert "test_multiple_scores_with_multiple_letters" in docs_text

    # 4. Copy exercise to scratch temp directory and run pytest
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = os.path.join(tmp_dir, "etl")
        shutil.copytree(exercise_dir, scratch_exercise, symlinks=True)

        scratch_solution = os.path.join(scratch_exercise, solution_rel)
        scratch_example = os.path.join(scratch_exercise, example_rel)
        shutil.copyfile(scratch_example, scratch_solution)

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

        test_py = os.path.join(scratch_exercise, test_rel)
        with open(test_py, "r", encoding="utf-8") as f:
            test_content = f.read()
        assert "def test_single_letter" in test_content
        assert "def test_single_score_with_multiple_letters" in test_content
        assert "def test_multiple_scores_with_multiple_letters" in test_content

        words = stdout.split()
        passed_count = 0
        for i, w in enumerate(words):
            if "passed" in w and i > 0:
                try:
                    passed_count = int(words[i - 1])
                except ValueError:
                    pass
        assert passed_count >= 4, f"Expected at least 4 passing tests, got {passed_count}"

    results = {
        "task_id": "R36-T032",
        "exercise": "exercises/practice/etl",
        "tests_passed": passed_count,
        "exit_code": exit_code,
        "regeneration_check_passed": True,
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T032 Verification Report\nStatus: PASS\nTests Passed: {passed_count}\n")

    print("\nCheck R36-T032 successfully passed all assertions!")


if __name__ == "__main__":
    main()
