#!/usr/bin/env python3
"""
Verification check for Task R36-T037:
Add Python-specific guidance for circular-buffer [exercises/practice/circular-buffer]
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_rel = os.path.join("exercises", "practice", "circular-buffer")
    exercise_dir = os.path.join(repo_root, exercise_rel)
    work_dir = os.path.join(repo_root, "work", "R36-T037")
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

    # Verify hints.md guidance and micro-example
    hints_path = os.path.join(exercise_dir, ".docs", "hints.md")
    assert os.path.exists(hints_path), f"Missing {hints_path}"
    with open(hints_path, "r", encoding="utf-8") as f:
        hints_text = f.read()
    assert "TinyRing" in hints_text
    assert "Expected Output:" in hints_text
    assert "https://docs.python.org" in hints_text

    # 2. Test micro-example execution
    code_lines = []
    capture = False
    in_micro = False
    for line in hints_text.splitlines():
        if "### Runnable Micro-Example" in line:
            in_micro = True
            continue
        if in_micro and line.strip() == "```python":
            capture = True
            continue
        elif capture and line.strip() == "```":
            break
        elif capture:
            code_lines.append(line)
    micro_code = "\n".join(code_lines)
    proc_micro = subprocess.run([sys.executable, "-c", micro_code], capture_output=True, text=True)
    assert proc_micro.returncode == 0, f"Micro-example failed to execute: {proc_micro.stderr}"
    assert "A B" in proc_micro.stdout.strip(), f"Micro-example output mismatch: {proc_micro.stdout}"

    # 3. Test reference implementation in scratch directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = os.path.join(tmp_dir, "circular_buffer")
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
        assert passed_count >= 14, f"Expected at least 14 passed tests, got {passed_count}"

    results = {
        "task_id": "R36-T037",
        "exercise": "exercises/practice/circular-buffer",
        "tests_passed": passed_count,
        "exit_code": exit_code,
        "micro_example_verified": True,
        "learner_stub_unsolved": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write(f"Task R36-T037 Verification Report\nStatus: PASS\nTests Passed: {passed_count}\n")

    print(f"\nCheck R36-T037 successfully passed all assertions! ({passed_count} tests passed)")


if __name__ == "__main__":
    main()
