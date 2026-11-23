#!/usr/bin/env python3
"""
Verification check for Task R36-T039:
Run isogram without altering its learner files [exercises/practice/isogram]
"""

import json
import os
import subprocess
import sys


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    work_dir = os.path.join(repo_root, "work", "R36-T039")
    os.makedirs(work_dir, exist_ok=True)

    course_check_script = os.path.join(repo_root, "tools", "course_checks", "r36-t039.py")
    assert os.path.exists(course_check_script), f"Missing {course_check_script}"

    proc = subprocess.run([sys.executable, course_check_script], capture_output=True, text=True)
    stdout = proc.stdout
    stderr = proc.stderr
    exit_code = proc.returncode

    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    assert exit_code == 0, f"check failed with code {exit_code}"

    # Verify learner stub is untouched
    stub_file = os.path.join(repo_root, "exercises", "practice", "isogram", "isogram.py")
    with open(stub_file, "r", encoding="utf-8") as f:
        stub_content = f.read()
    assert "pass" in stub_content, "Learner stub was modified!"

    results = {
        "task_id": "R36-T039",
        "exercise": "exercises/practice/isogram",
        "exit_code": exit_code,
        "isolated_runner_passed": True,
        "learner_stub_untouched": True,
        "status": "PASS"
    }

    with open(os.path.join(work_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(work_dir, "results.txt"), "w", encoding="utf-8") as f:
        f.write("Task R36-T039 Verification Report\nStatus: PASS\nIsolated runner passed without modifying learner stub.\n")

    print("\nCheck R36-T039 successfully passed all assertions!")


if __name__ == "__main__":
    main()
