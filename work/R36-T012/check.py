#!/usr/bin/env python3
"""Run the generated protein-translation suite against its reference safely."""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

FOCUSED_CASES = {
    "test_methionine_rna_sequence",
    "test_phenylalanine_rna_sequence_1",
    "test_phenylalanine_rna_sequence_2",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(f"$ {' '.join(command)}")
    print(output, end="" if output.endswith("\n") else "\n")
    if result.returncode:
        raise RuntimeError(f"child exited with status {result.returncode}")
    return result


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    exercise = repo / "exercises/practice/protein-translation"
    config_path = exercise / ".meta/config.json"
    config = json.loads(config_path.read_text())
    solution_files = config["files"]["solution"]
    test_files = config["files"]["test"]
    example_files = config["files"]["example"]
    if len(solution_files) != 1 or len(test_files) != 1 or len(example_files) != 1:
        raise ValueError("expected one configured solution, test, and example file")

    learner_solution = exercise / solution_files[0]
    reference = exercise / example_files[0]
    if learner_solution.exists():
        learner_before = learner_solution.read_bytes()
    else:
        learner_before = None

    with tempfile.TemporaryDirectory(prefix="r36-t012-reference-") as directory:
        scratch = Path(directory) / exercise.name
        shutil.copytree(exercise, scratch)  # copytree includes .meta and other dotfiles
        shutil.copy2(reference, scratch / solution_files[0])
        test_path = scratch / test_files[0]
        text = test_path.read_text()
        method_names = set(re.findall(r"^    def (test_\w+)\(", text, re.M))
        missing = FOCUSED_CASES - method_names
        if missing:
            raise AssertionError(f"required generated cases absent: {sorted(missing)}")
        expected_count = len(method_names)
        if expected_count == 0:
            raise AssertionError("generated suite contains zero test methods")

        pytest_version = run([sys.executable, "-m", "pytest", "--version"], scratch)
        result = run([sys.executable, "-m", "pytest", "-q"], scratch)
        output = result.stdout + result.stderr
        summary = re.search(r"(?m)^((?:\d+ [a-z]+(?:, )?)+) in [\d.]+s$", output)
        if not summary:
            raise AssertionError("pytest output did not contain a test-count summary")
        counts = {
            label: int(count)
            for count, label in re.findall(r"(\d+) ([a-z]+)", summary.group(1))
        }
        executed = sum(counts.values())
        if counts.get("passed", 0) != expected_count or executed != expected_count:
            raise AssertionError(
                f"expected {expected_count} passing cases with no skips or failures, "
                f"got {counts}"
            )

    if learner_solution.exists() and learner_solution.read_bytes() != learner_before:
        raise AssertionError("learner solution changed during scratch verification")
    evidence = Path(__file__).resolve().parent
    (evidence / "inputs.json").write_text(
        f"{json.dumps(
            {
                "exercise": "protein-translation",
                "config": str(config_path),
                "solution_from_config": solution_files[0],
                "test_from_config": test_files[0],
                "reference_from_config": example_files[0],
                "focused_cases": sorted(FOCUSED_CASES),
                "expected_case_count": expected_count,
                "pytest_command": [sys.executable, "-m", "pytest", "-q"],
            },
            indent=2,
        )}\n"
    )
    (evidence / "pytest-output.txt").write_text(result.stdout + result.stderr)
    (evidence / "tool-versions.txt").write_text(
        f"Python: {platform.python_version()} ({sys.executable})\n"
        f"{pytest_version.stdout.strip()}\n"
        f"pytest-subtests: {version('pytest-subtests')}\n"
    )
    (evidence / "results.json").write_text(
        f"{json.dumps(
            {
                "expected": {"executed_cases": expected_count, "status": "all passed"},
                "actual": {
                    "executed_cases": executed,
                    "status": "passed",
                    "return_code": 0,
                    "pytest_counts": counts,
                },
                "focused_cases_present": sorted(FOCUSED_CASES),
                "learner_solution_unchanged": True,
            },
            indent=2,
        )}\n"
    )
    print(f"PASS: {executed} generated cases executed; learner solution unchanged.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # keep assertion and child failures nonzero with context
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
