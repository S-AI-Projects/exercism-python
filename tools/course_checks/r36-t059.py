#!/usr/bin/env python3
"""
Isolated test runner for exercises/practice/say (R36-T059).
Tests the reference implementation in an isolated temporary scratch copy,
protecting learner files and verifying SHA-256 integrity before and after runs.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Optional, Tuple


def compute_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_say_test(repo_root: Optional[str] = None, override_ref_code: Optional[str] = None, test_filter: Optional[str] = None) -> Tuple[int, int, str]:
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    exercise_dir = os.path.join(repo_root, "exercises", "practice", "say")
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    learner_path = os.path.join(exercise_dir, solution_rel)
    hash_before = compute_file_hash(learner_path)

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dest_exercise = os.path.join(tmp_dir, "say")
            shutil.copytree(exercise_dir, dest_exercise, dirs_exist_ok=True)

            sol_dest = os.path.join(dest_exercise, solution_rel)
            if override_ref_code is not None:
                with open(sol_dest, "w", encoding="utf-8") as f:
                    f.write(override_ref_code)
            else:
                ref_src = os.path.join(dest_exercise, example_rel)
                shutil.copyfile(ref_src, sol_dest)

            cmd = [sys.executable, "-m", "pytest", "-v"]
            if test_filter:
                cmd.extend(["-k", test_filter])
            cmd.append(test_rel)

            proc = subprocess.run(cmd, cwd=dest_exercise, capture_output=True, text=True)
            output = proc.stdout + "\n" + proc.stderr
            test_count = output.count(" PASSED")

            # Check if zero tests ran
            if "collected 0 items" in output or test_count == 0 and proc.returncode == 0:
                return 1, 0, "Zero tests collected/executed."

            return proc.returncode, test_count, output
    finally:
        hash_after = compute_file_hash(learner_path)
        if hash_before != hash_after:
            raise RuntimeError("CRITICAL INTEGRITY FAILURE: Learner file was modified during test run!")


def main():
    retcode, count, out = run_say_test()
    if retcode == 0:
        print(f"say isolated runner passed: {count} tests executed successfully.")
        return 0
    else:
        print(f"say isolated runner failed with code {retcode}:\n{out}", file=sys.stderr)
        return retcode


if __name__ == "__main__":
    sys.exit(main())
