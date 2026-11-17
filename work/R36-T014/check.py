#!/usr/bin/env python3
"""Run point-mutations tests against original and refactored references."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXERCISE = REPO / "exercises/practice/point-mutations"
CONFIG_PATH = EXERCISE / ".meta/config.json"
EVIDENCE = Path(__file__).resolve().parent
BASELINE_REFERENCE = """def hamming_distance(strand1, strand2):
    return sum(idx != edx for (idx, edx) in zip(strand1, strand2))
"""


def run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(
            f"Command exited {result.returncode}: {command!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def test_count(output: str) -> int:
    summaries = re.findall(r"(?m)^(\d+) passed(?:,|\s|$)", output)
    if not summaries:
        raise AssertionError(f"pytest reported no passed-test count:\n{output}")
    count = int(summaries[-1])
    if count == 0:
        raise AssertionError("pytest collected zero tests")
    return count


def run_reference(label: str, reference: str, solution_name: str, test_name: str) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"point-mutations-{label}-") as temp:
        scratch = Path(temp) / "exercise"
        shutil.copytree(EXERCISE, scratch)
        if not (scratch / test_name).is_file():
            raise AssertionError(f"test path from config does not exist: {test_name}")
        (scratch / solution_name).write_text(reference)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=scratch,
            text=True,
            capture_output=True,
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            raise AssertionError(
                f"{label} pytest exit {result.returncode}:\n{output}"
            )
        return {"returncode": result.returncode, "tests": test_count(output), "output": output.strip()}


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text())
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_name = config["files"]["example"][0]
    original = BASELINE_REFERENCE
    refactored = (EXERCISE / example_name).read_text()

    before = run_reference("before", original, solution_name, test_name)
    after = run_reference("after", refactored, solution_name, test_name)
    assert before["tests"] == after["tests"], (
        f"enabled case count changed: before={before['tests']} after={after['tests']}"
    )

    cases = [
        {"name": "test_no_difference_between_empty_strands", "inputs": ["", ""], "expected": 0},
        {"name": "test_no_difference_between_identical_strands", "inputs": ["GGACTGA", "GGACTGA"], "expected": 0},
        {"name": "test_complete_hamming_distance_in_small_strand", "inputs": ["ACT", "GGA"], "expected": 3},
    ]
    probe_code = (
        "import json, point_mutations; "
        "cases=json.loads(%r); "
        "print(json.dumps([point_mutations.hamming_distance(*c['inputs']) for c in cases]))"
    ) % json.dumps(cases)
    actuals = {}
    for label, reference in (("before", original), ("after", refactored)):
        with tempfile.TemporaryDirectory(prefix="point-mutations-cases-") as temp:
            scratch = Path(temp) / "exercise"
            shutil.copytree(EXERCISE, scratch)
            (scratch / solution_name).write_text(reference)
            result = run([sys.executable, "-c", probe_code], cwd=scratch)
            actuals[label] = json.loads(result.stdout)
    for index, case in enumerate(cases):
        assert actuals["before"][index] == case["expected"], case
        assert actuals["after"][index] == case["expected"], case
    assert actuals["before"] == actuals["after"]

    py_version = run([sys.executable, "--version"]).stdout.strip()
    pytest_version = run([sys.executable, "-m", "pytest", "--version"]).stdout.strip()
    report = {
        "inputs": cases,
        "named_case_results": {
            label: [
                {**case, "actual": actuals[label][i]}
                for i, case in enumerate(cases)
            ]
            for label in ("before", "after")
        },
        "enabled_test_cases": {"before": before["tests"], "after": after["tests"]},
        "pytest_runs": {"before": before, "after": after},
        "tool_versions": {"python": py_version, "pytest": pytest_version},
    }
    (EVIDENCE / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {after['tests']} enabled tests; named case outputs match before and after")
    print(f"Evidence: {EVIDENCE / 'results.json'}")


if __name__ == "__main__":
    main()
