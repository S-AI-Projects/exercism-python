#!/usr/bin/env python3
"""Verify matching-brackets reference behavior and a deliberate scratch mutant."""

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
    "test_paired_square_brackets",
    "test_empty_string",
    "test_unpaired_brackets",
}
MUTATION_CASE = "test_wrong_ordered_brackets"
DIAGNOSTIC_INPUT = "}"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    output = result.stdout + result.stderr
    print(f"$ {' '.join(command)}")
    print(output, end="" if output.endswith("\n") else "\n")
    return result


def pytest_summary(output: str) -> dict[str, int]:
    match = re.search(r"(?m)^((?:\d+ [a-z]+(?:, )?)+) in [\d.]+s$", output)
    if not match:
        raise AssertionError("pytest output did not contain a test-count summary")
    return {
        label: int(count)
        for count, label in re.findall(r"(\d+) ([a-z]+)", match.group(1))
    }


def configured_files(exercise: Path) -> tuple[Path, str, str, str, int]:
    config_path = exercise / ".meta/config.json"
    config = json.loads(config_path.read_text())
    solution = config["files"]["solution"]
    tests = config["files"]["test"]
    examples = config["files"]["example"]
    if len(solution) != 1 or len(tests) != 1 or len(examples) != 1:
        raise ValueError("expected one configured solution, test, and example file")

    test_source = (exercise / tests[0]).read_text()
    methods = set(re.findall(r"^    def (test_\w+)\(", test_source, re.M))
    missing = FOCUSED_CASES - methods
    if missing:
        raise AssertionError(f"required focused cases are missing: {sorted(missing)}")
    if not methods:
        raise AssertionError("generated test module contains zero test cases")
    return config_path, solution[0], tests[0], examples[0], len(methods)


def make_mutant(example_text: str) -> str:
    original = """            if not stack:
                return False
"""
    mutated = """            if not stack:
                return True
"""
    if example_text.count(original) != 1:
        raise AssertionError("could not identify the empty-stack branch uniquely")
    return example_text.replace(original, mutated, 1)


def new_copy(exercise: Path, parent: Path, name: str, solution_file: str) -> Path:
    scratch = parent / name / exercise.name
    scratch.parent.mkdir()
    shutil.copytree(exercise, scratch)  # Includes .docs and .meta dotfiles.
    shutil.copy2(scratch / ".meta/example.py", scratch / solution_file)
    return scratch


def run_suite(
    directory: Path,
) -> tuple[subprocess.CompletedProcess[str], str, dict[str, int]]:
    result = run([sys.executable, "-m", "pytest", "-q"], directory)
    output = result.stdout + result.stderr
    return result, output, pytest_summary(output)


def verify_original(
    result: subprocess.CompletedProcess[str],
    counts: dict[str, int],
    expected_count: int,
) -> None:
    if result.returncode != 0:
        raise AssertionError(f"original reference suite exited {result.returncode}")
    if counts != {"passed": expected_count}:
        raise AssertionError(
            f"expected {expected_count} passing original cases, got {counts}"
        )


def verify_mutant(
    result: subprocess.CompletedProcess[str],
    output: str,
    counts: dict[str, int],
    test_file: str,
    expected_count: int,
) -> None:
    if result.returncode != 1:
        raise AssertionError(
            f"expected assertion failures from mutant (exit 1), got {result.returncode}"
        )
    if sum(counts.values()) != expected_count:
        raise AssertionError(
            f"expected {expected_count} mutant test outcomes, got {counts}"
        )
    failed_case = f"{test_file}::MatchingBracketsTest::{MUTATION_CASE}"
    if failed_case not in output:
        raise AssertionError(f"mutant was not rejected by {MUTATION_CASE}")


def probe_diagnostic(original: Path, mutant: Path) -> tuple[str, str]:
    probe = "from matching_brackets import is_paired; print(is_paired('}'))"
    original_run = run([sys.executable, "-c", probe], original)
    mutant_run = run([sys.executable, "-c", probe], mutant)
    if original_run.returncode or mutant_run.returncode:
        raise AssertionError("diagnostic input subprocess returned nonzero")
    values = original_run.stdout.strip(), mutant_run.stdout.strip()
    if values != ("False", "True"):
        raise AssertionError(f"expected diagnostic result False/True, got {values}")
    return values


def write_evidence(
    config_path: Path,
    solution_file: str,
    test_file: str,
    example_file: str,
    expected_count: int,
    original_run: subprocess.CompletedProcess[str],
    original_counts: dict[str, int],
    mutant_run: subprocess.CompletedProcess[str],
    mutant_counts: dict[str, int],
    original_output: str,
    mutant_output: str,
    diagnostic_values: tuple[str, str],
) -> None:
    evidence = Path(__file__).resolve().parent
    inputs = {
        "exercise": "matching-brackets",
        "config": str(config_path),
        "solution_from_config": solution_file,
        "test_from_config": test_file,
        "reference_from_config": example_file,
        "focused_cases": sorted(FOCUSED_CASES),
        "expected_case_count": expected_count,
        "mutation": "empty-stack unmatched closer returns True instead of False",
        "mutation_rejecting_test": MUTATION_CASE,
        "diagnostic_input": DIAGNOSTIC_INPUT,
        "diagnostic_expected_result": False,
    }
    (evidence / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n")
    (evidence / "pytest-output.txt").write_text(
        f"=== Original reference ===\n{original_output.rstrip()}"
        f"\n=== Mutant reference ===\n{mutant_output.rstrip()}\n"
    )
    pytest_version = run([sys.executable, "-m", "pytest", "--version"], evidence)
    if pytest_version.returncode:
        raise AssertionError("pytest --version returned nonzero")
    (evidence / "tool-versions.txt").write_text(
        f"Python: {platform.python_version()} ({sys.executable})\n"
        f"{pytest_version.stdout.strip()}\n"
        f"pytest-subtests: {version('pytest-subtests')}\n"
    )
    results = {
        "expected": {
            "original": {"passed": expected_count},
            "mutant": {"rejecting_case": MUTATION_CASE},
            "diagnostic_input": {DIAGNOSTIC_INPUT: False},
        },
        "actual": {
            "original_return_code": original_run.returncode,
            "original_counts": original_counts,
            "mutant_return_code": mutant_run.returncode,
            "mutant_counts": mutant_counts,
            "mutant_rejected_by_named_case": MUTATION_CASE in mutant_output,
            "original_diagnostic_value": diagnostic_values[0],
            "mutant_diagnostic_value": diagnostic_values[1],
            "learner_solution_unchanged": True,
        },
    }
    (evidence / "results.json").write_text(json.dumps(results, indent=2) + "\n")


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    exercise = repo / "exercises/practice/matching-brackets"
    config_path, solution_file, test_file, example_file, expected_count = (
        configured_files(exercise)
    )
    learner_solution = exercise / solution_file
    learner_before = (
        learner_solution.read_bytes() if learner_solution.exists() else None
    )
    mutant_example = make_mutant((exercise / example_file).read_text())

    with tempfile.TemporaryDirectory(prefix="r36-t013-mutation-") as directory:
        temp = Path(directory)
        original = new_copy(exercise, temp, "original", solution_file)
        mutant = new_copy(exercise, temp, "mutant", solution_file)
        mutant_reference = mutant / example_file
        mutant_reference.write_text(mutant_example)
        shutil.copy2(mutant_reference, mutant / solution_file)

        original_run, original_output, original_counts = run_suite(original)
        verify_original(original_run, original_counts, expected_count)
        mutant_run, mutant_output, mutant_counts = run_suite(mutant)
        verify_mutant(
            mutant_run, mutant_output, mutant_counts, test_file, expected_count
        )
        diagnostic_values = probe_diagnostic(original, mutant)

    if learner_solution.exists() and learner_solution.read_bytes() != learner_before:
        raise AssertionError("learner solution changed during scratch verification")
    write_evidence(
        config_path,
        solution_file,
        test_file,
        example_file,
        expected_count,
        original_run,
        original_counts,
        mutant_run,
        mutant_counts,
        original_output,
        mutant_output,
        diagnostic_values,
    )
    print(
        f"PASS: {expected_count} original cases; mutant rejected by "
        f"{MUTATION_CASE}; smallest diagnostic input {DIAGNOSTIC_INPUT!r}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
