#!/usr/bin/env python3
"""Check hexadecimal reference tests and the Python hint's micro-example."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
EXERCISE = REPO / "exercises/practice/hexadecimal"
EVIDENCE = Path(__file__).resolve().parent
MICRO_EXAMPLE = '''from functools import reduce

combine = lambda digits: reduce(lambda total, digit: total * 16 + digit, digits, 0)
print(combine([1, 10, 15]))
print(combine([]))
try:
    reduce(lambda total, digit: total * 16 + digit, [])
except TypeError:
    print("TypeError without initializer")
'''
EXPECTED_MICRO_OUTPUT = ["431", "0", "TypeError without initializer"]
REQUIRED_CASES = {"test_valid_hexa1", "test_valid_hexa2", "test_valid_hexa3"}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def configured_path(config: dict, key: str) -> Path:
    files = config["files"][key]
    if len(files) != 1:
        raise AssertionError(f"Expected one configured {key} file, got {files!r}")
    return EXERCISE / files[0]


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    solution_path = configured_path(config, "solution")
    test_path = configured_path(config, "test")
    example_path = configured_path(config, "example")
    if not all(path.is_file() for path in (solution_path, test_path, example_path)):
        raise AssertionError("Configured solution, test, and example files must exist")
    learner_solution = solution_path.read_text()
    if learner_solution.strip() != "def hexa(hex_string):\n    pass":
        raise AssertionError("The learner solution is no longer the expected unsolved stub")

    micro_path = EVIDENCE / "micro_example.py"
    micro_path.write_text(MICRO_EXAMPLE)
    micro = run(["python3", str(micro_path)], cwd=EVIDENCE)
    actual_micro_output = micro.stdout.splitlines()
    if micro.returncode != 0:
        raise AssertionError(f"Micro-example exited {micro.returncode}: {micro.stderr}")
    if actual_micro_output != EXPECTED_MICRO_OUTPUT:
        raise AssertionError(
            f"Micro-example output mismatch: expected {EXPECTED_MICRO_OUTPUT!r}, "
            f"got {actual_micro_output!r}"
        )

    inputs = {
        "exercise": "exercises/practice/hexadecimal",
        "paths_from_config": {
            "solution": str(solution_path.relative_to(REPO)),
            "test": str(test_path.relative_to(REPO)),
            "example": str(example_path.relative_to(REPO)),
        },
        "micro_example_inputs": {"digits": [1, 10, 15], "empty_digits": []},
        "required_test_cases": sorted(REQUIRED_CASES),
        "learner_solution": "def hexa(hex_string):\\n    pass",
    }

    with tempfile.TemporaryDirectory(prefix="hexadecimal-reference-") as tmp:
        scratch = Path(tmp) / "hexadecimal"
        # copytree includes hidden entries such as .meta and .docs by default.
        shutil.copytree(EXERCISE, scratch)
        shutil.copy2(example_path, scratch / solution_path.relative_to(EXERCISE))

        collection = run(["python3", "-m", "pytest", "--collect-only", "-q"], cwd=scratch)
        if collection.returncode != 0:
            raise AssertionError(
                f"Pytest collection exited {collection.returncode}:\n"
                f"{collection.stdout}\n{collection.stderr}"
            )
        collected_names = set(re.findall(r"::(test_[A-Za-z0-9_]+)", collection.stdout))
        missing = REQUIRED_CASES - collected_names
        if missing:
            raise AssertionError(f"Required cases were not collected: {sorted(missing)}")
        count_match = re.search(r"(\d+) tests? collected", collection.stdout)
        if not count_match:
            raise AssertionError(f"Could not read pytest collection count:\n{collection.stdout}")
        collected_count = int(count_match.group(1))
        if collected_count == 0:
            raise AssertionError("Pytest collected zero tests")

        tests = run(["python3", "-m", "pytest", "-q"], cwd=scratch)
        outcome_counts = [
            int(value)
            for value in re.findall(
                r"(\d+) (?:passed|failed|error|errors|skipped|xfailed|xpassed)",
                tests.stdout + tests.stderr,
            )
        ]
        executed_count = sum(outcome_counts)
        if tests.returncode != 0:
            raise AssertionError(
                f"Reference tests exited {tests.returncode}:\n{tests.stdout}\n{tests.stderr}"
            )
        if executed_count == 0:
            raise AssertionError("Pytest executed zero tests")
        if executed_count != collected_count:
            raise AssertionError(
                f"Executed {executed_count} cases, but collected {collected_count}"
            )

    expected = {
        "micro_example_stdout_lines": EXPECTED_MICRO_OUTPUT,
        "reference_test_count": "all collected cases, including the three named cases",
        "reference_test_returncode": 0,
        "learner_solution_modified": False,
    }
    actual = {
        "micro_example_returncode": micro.returncode,
        "micro_example_stdout_lines": actual_micro_output,
        "micro_example_stderr": micro.stderr,
        "reference_pytest_collect_returncode": collection.returncode,
        "reference_pytest_collect_stdout": collection.stdout,
        "reference_pytest_collect_stderr": collection.stderr,
        "reference_pytest_returncode": tests.returncode,
        "reference_pytest_stdout": tests.stdout,
        "reference_pytest_stderr": tests.stderr,
        "collected_case_count": collected_count,
        "executed_case_count": executed_count,
        "required_cases_collected": sorted(REQUIRED_CASES),
        "learner_solution_remains_unsolved": True,
    }
    (EVIDENCE / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")
    (EVIDENCE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    (EVIDENCE / "actual.json").write_text(json.dumps(actual, indent=2) + "\n")

    python_version = run(["python3", "--version"], cwd=REPO)
    pytest_version = run(["python3", "-m", "pytest", "--version"], cwd=REPO)
    for label, result in (("Python", python_version), ("pytest", pytest_version)):
        if result.returncode != 0:
            raise AssertionError(
                f"{label} version probe exited {result.returncode}: "
                f"{result.stdout}{result.stderr}"
            )
    versions = {
        "python": (python_version.stdout + python_version.stderr).strip(),
        "pytest": (pytest_version.stdout + pytest_version.stderr).strip(),
    }
    (EVIDENCE / "tool_versions.json").write_text(json.dumps(versions, indent=2) + "\n")
    print(f"Micro-example: {len(EXPECTED_MICRO_OUTPUT)} expected outputs matched")
    print(f"Reference: {executed_count} tests passed (including the three required cases)")


if __name__ == "__main__":
    main()
