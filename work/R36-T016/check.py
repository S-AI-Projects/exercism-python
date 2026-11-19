#!/usr/bin/env python3
"""Run the reference and digit-vector alternative against the same exercise tests."""

from __future__ import annotations

import json
import importlib.metadata
import platform
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/all-your-base"
EVIDENCE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_copy(label: str, implementation: Path, solution_name: str, test_name: str,
             scratch_root: Path, enabled_cases: int) -> dict:
    scratch = scratch_root / label
    shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copy2(implementation, scratch / solution_name)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=scratch,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    (EVIDENCE / f"{label}-pytest-output.txt").write_text(output)
    summaries = re.findall(r"(?m)(\d+) passed(?:,|\s|$)", output)
    executed = int(summaries[-1]) if summaries else 0
    return {
        "implementation": label,
        "return_code": result.returncode,
        "enabled_cases_expected": enabled_cases,
        "passed_cases_actual": executed,
        "tests_passed": result.returncode == 0 and executed == enabled_cases,
        "output_file": f"{label}-pytest-output.txt",
        "output": output,
    }


def main() -> None:
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_name = config["files"]["example"][0]
    tests_toml = tomllib.loads((EXERCISE / ".meta/tests.toml").read_text())
    enabled_cases = sum(case.get("include") is not False for case in tests_toml.values())
    test_source = (EXERCISE / test_name).read_text()
    named_cases = (
        "test_single_bit_one_to_decimal",
        "test_binary_to_single_decimal",
        "test_single_decimal_to_binary",
    )
    require(all(f"def {case}(" in test_source for case in named_cases), "a required named case is missing")
    require(enabled_cases > 0, "tests.toml enables zero cases")

    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "pytest": subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "pytest-subtests": importlib.metadata.version("pytest-subtests"),
    }
    (EVIDENCE / "versions.json").write_text(json.dumps(versions, indent=2) + "\n")

    outcomes = []
    named_inputs = (
        ("test_single_bit_one_to_decimal", 2, [1], 10, [1]),
        ("test_binary_to_single_decimal", 2, [1, 0, 1], 10, [5]),
        ("test_single_decimal_to_binary", 10, [5], 2, [1, 0, 1]),
    )
    named_results = []
    for label, implementation in (("reference", EXERCISE / example_name),
                                  ("digit-vector", EVIDENCE / "alternative.py")):
        rebase = runpy.run_path(str(implementation))["rebase"]
        for case, from_base, digits, to_base, expected in named_inputs:
            actual = rebase(from_base, digits, to_base)
            named_results.append({
                "implementation": label,
                "case": case,
                "input": {"from_base": from_base, "digits": digits, "to_base": to_base},
                "expected": expected,
                "actual": actual,
                "passed": actual == expected,
            })

    with tempfile.TemporaryDirectory(prefix="all-your-base-approaches-") as temporary:
        scratch_root = Path(temporary)
        outcomes.append(run_copy("reference", EXERCISE / example_name, solution_name, test_name,
                                 scratch_root, enabled_cases))
        outcomes.append(run_copy("digit-vector", EVIDENCE / "alternative.py", solution_name, test_name,
                                 scratch_root, enabled_cases))

    results = {
        "input": {
            "exercise": "exercises/practice/all-your-base",
            "command": "python3 -m pytest -q",
            "case_count_from_tests_toml": enabled_cases,
            "required_cases": list(named_cases),
            "dotfiles_copied": True,
            "reference_example_copied_to_solution_only_in_temporary_copy": True,
            "alternative_source": "work/R36-T016/alternative.py",
            "named_case_inputs_expected_actual": named_results,
        },
        "expected": {"each_implementation_passes": enabled_cases, "zero_test_run_is_failure": True},
        "actual": [
            {key: value for key, value in outcome.items() if key != "output"}
            for outcome in outcomes
        ],
    }
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    (EVIDENCE / "comparison-output.txt").write_text(
        "\n".join(f"--- {item['implementation']} ---\n{item['output']}" for item in outcomes)
    )

    for outcome in outcomes:
        print(f"{outcome['implementation']}: {outcome['passed_cases_actual']}/"
              f"{outcome['enabled_cases_expected']} passed (exit {outcome['return_code']}).")
    require(all(outcome["return_code"] == 0 for outcome in outcomes), "a pytest child exited non-zero")
    require(all(outcome["passed_cases_actual"] > 0 for outcome in outcomes), "a pytest child ran zero tests")
    require(all(outcome["passed_cases_actual"] == enabled_cases for outcome in outcomes),
            "an implementation did not pass every enabled case")
    require(all(result["passed"] for result in named_results),
            "a required named case did not match its expected result")
    print(f"PASS: both implementations passed all {enabled_cases} enabled cases.")


if __name__ == "__main__":
    main()
