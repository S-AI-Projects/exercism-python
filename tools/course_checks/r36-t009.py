#!/usr/bin/env python3
"""Isolated test runner for exercises/practice/reverse-string.

Tests the reference implementation from .meta/example.py in an isolated
temporary directory copy, leaving repository learner stubs completely untouched.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/reverse-string"
EXPECTED_TESTS = 7


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_isolated(exercise_path: Path = EXERCISE, python_bin: str = sys.executable) -> tuple[int, int, str]:
    """Run reverse-string tests against .meta/example.py in a tempdir.

    Returns:
        tuple of (exit_code, passed_count, stdout_text)
    """
    config_path = exercise_path / ".meta/config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing config.json at {config_path}")

    config = json.loads(config_path.read_text(encoding="utf-8"))
    files = config.get("files", {})
    solution_files = files.get("solution", [])
    example_files = files.get("example", [])
    test_files = files.get("test", [])

    if not solution_files or not example_files or not test_files:
        raise ValueError("config.json missing required solution, example, or test file mappings")

    solution_name = solution_files[0]
    example_rel = example_files[0]
    test_name = test_files[0]

    learner_file = exercise_path / solution_name
    example_file = exercise_path / example_rel
    test_file = exercise_path / test_name

    for f in (learner_file, example_file, test_file):
        if not f.exists():
            raise FileNotFoundError(f"Required exercise file not found: {f}")

    hash_before = sha256(learner_file)

    temp_dir = tempfile.mkdtemp(prefix="reverse_string_test_")
    try:
        temp_path = Path(temp_dir)
        # Copy exercise directory contents into temporary workspace
        for item in exercise_path.iterdir():
            dest = temp_path / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest)

        # Replace learner stub with the reference implementation inside the temp workspace
        shutil.copy2(example_file, temp_path / solution_name)

        # Run pytest inside the temporary workspace
        cmd = [python_bin, "-m", "pytest", str(temp_path / test_name), "-v"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse test count
        match = re.search(r"(\d+)\s+passed", result.stdout)
        passed_count = int(match.group(1)) if match else 0

        return result.returncode, passed_count, result.stdout
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        hash_after = sha256(learner_file)
        if hash_before != hash_after:
            raise RuntimeError("Learner solution file was modified during test run!")


def main() -> None:
    exit_code, count, output = run_isolated()
    print(output)
    if exit_code == 0:
        print(f"PASS: {count} tests executed in isolation; learner stub unchanged.")
        sys.exit(0)
    else:
        print(f"FAIL: pytest exited with code {exit_code}")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
