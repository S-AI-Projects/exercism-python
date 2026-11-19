#!/usr/bin/env python3
"""Run the house reference tests in a disposable exercise copy."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/house"
CONFIG = EXERCISE / ".meta/config.json"


def configured_path(exercise_copy: Path, name: str) -> Path:
    values = json.loads(CONFIG.read_text(encoding="utf-8"))["files"][name]
    if len(values) != 1:
        raise ValueError(f"expected exactly one {name} file in {CONFIG}")
    path = (exercise_copy / values[0]).resolve()
    if not path.is_relative_to(exercise_copy.resolve()):
        raise ValueError(f"configured {name} path escapes the exercise: {values[0]}")
    return path


def executed_count(output: str) -> int:
    """Count pytest outcomes reported in the final summary."""
    summary = re.findall(r"(?:(\d+) )?(?:passed|failed|error|skipped|xfailed|xpassed)", output)
    return sum(int(count or 1) for count in summary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, help="reference source (defaults to config example)")
    parser.add_argument("--python", default=sys.executable, help="Python executable used for pytest")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="extra pytest arguments after --")
    args = parser.parse_args()
    if args.pytest_args[:1] == ["--"]:
        args.pytest_args = args.pytest_args[1:]
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    example_source = EXERCISE / config["files"]["example"][0]
    reference = (args.reference or example_source).resolve()
    if not reference.is_file():
        parser.error(f"reference does not exist: {reference}")

    with tempfile.TemporaryDirectory(prefix="house-check-") as temp:
        scratch_root = Path(temp)
        scratch_exercise = scratch_root / "house"
        shutil.copytree(EXERCISE, scratch_exercise)
        solution = configured_path(scratch_exercise, "solution")
        test_file = configured_path(scratch_exercise, "test")
        shutil.copyfile(reference, solution)
        command = [args.python, "-m", "pytest", "-q", str(test_file), *args.pytest_args]
        result = subprocess.run(command, cwd=scratch_exercise, text=True, capture_output=True)
        output = result.stdout + result.stderr
        print(output, end="" if output.endswith("\n") else "\n")
        count = executed_count(output)
        print(f"Executed cases: {count}")
        if count == 0:
            print("ERROR: pytest executed no cases", file=sys.stderr)
            return 1
        return result.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
