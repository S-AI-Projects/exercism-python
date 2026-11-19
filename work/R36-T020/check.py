#!/usr/bin/env python3
"""Run the secret-handshake reference and tests in an isolated exercise copy."""

from __future__ import annotations

import ast
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/secret-handshake"
EVIDENCE = Path(__file__).resolve().parent
SELECTED_TESTS = (
    "test_wink_for_1",
    "test_double_blink_for_10",
    "test_close_your_eyes_for_100",
)


def configured_path(config: dict, key: str) -> Path:
    paths = config["files"][key]
    if len(paths) != 1:
        raise ValueError(f"Expected one configured {key} file; found {paths!r}")
    path = Path(paths[0])
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe configured {key} path: {path}")
    return path


def selected_cases(test_path: Path) -> tuple[list[str], list[dict]]:
    tree = ast.parse(test_path.read_text(encoding="utf-8"))
    names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]
    cases = []
    for name in SELECTED_TESTS:
        function = next(
            (
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name == name
            ),
            None,
        )
        if function is None:
            raise AssertionError(f"Required test is missing: {name}")
        assertions = [
            node
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "assertEqual"
        ]
        if len(assertions) != 1 or len(assertions[0].args) != 2:
            raise AssertionError(f"Could not identify one assertEqual in {name}")
        actual_expr, expected_expr = assertions[0].args
        if (
            not isinstance(actual_expr, ast.Call)
            or not isinstance(actual_expr.func, ast.Name)
            or actual_expr.func.id != "commands"
            or len(actual_expr.args) != 1
            or not isinstance(actual_expr.args[0], ast.Constant)
            or not isinstance(actual_expr.args[0].value, str)
        ):
            raise AssertionError(f"Could not identify commands input in {name}")
        try:
            expected = ast.literal_eval(expected_expr)
        except (ValueError, TypeError) as error:
            raise AssertionError(f"Could not read expected value in {name}") from error
        cases.append(
            {"test": name, "input": actual_expr.args[0].value, "expected": expected}
        )
    return names, cases


def command_version(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return (result.stdout + result.stderr).strip() or f"unavailable (exit {result.returncode})"


def main() -> int:
    config_path = EXERCISE / ".meta/config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    solution_rel = configured_path(config, "solution")
    test_rel = configured_path(config, "test")
    example_rel = configured_path(config, "example")
    test_path = EXERCISE / test_rel
    test_names, cases = selected_cases(test_path)

    try:
        subtests_version = importlib.metadata.version("pytest-subtests")
    except importlib.metadata.PackageNotFoundError:
        subtests_version = "not installed"
    configlet = shutil.which("configlet")
    configlet_version = (
        command_version([configlet, "--version"]) if configlet else "not installed"
    )
    versions = {
        "python": command_version([sys.executable, "--version"]),
        "pytest": command_version([sys.executable, "-m", "pytest", "--version"]),
        "pytest_subtests": subtests_version,
        "configlet": configlet_version,
    }

    status = 0
    suite_stdout = ""
    suite_stderr = ""
    suite_returncode = None
    selected_actuals = []
    executed_count = 0
    errors = []

    with tempfile.TemporaryDirectory(prefix="secret-handshake-") as temp_dir:
        scratch_exercise = Path(temp_dir) / "secret-handshake"
        shutil.copytree(EXERCISE, scratch_exercise)
        shutil.copy2(EXERCISE / example_rel, scratch_exercise / solution_rel)

        payload = json.dumps([case["input"] for case in cases])
        evaluate_reference = (
            "import importlib.util, json, pathlib, sys; "
            "path = pathlib.Path(sys.argv[1]); "
            "spec = importlib.util.spec_from_file_location('scratch_solution', path); "
            "module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); "
            "print(json.dumps([module.commands(value) for value in json.loads(sys.argv[2])]))"
        )
        actual_process = subprocess.run(
            [sys.executable, "-c", evaluate_reference, str(solution_rel), payload],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
            check=False,
        )
        if actual_process.returncode != 0:
            errors.append(
                f"Reference evaluation exited {actual_process.returncode}: "
                f"{actual_process.stderr.strip()}"
            )
        else:
            try:
                values = json.loads(actual_process.stdout)
                for case, actual in zip(cases, values, strict=True):
                    selected_actuals.append({**case, "actual": actual, "passed": actual == case["expected"]})
                    if actual != case["expected"]:
                        errors.append(
                            f"{case['test']}: expected {case['expected']!r}, got {actual!r}"
                        )
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                errors.append(f"Could not decode reference results: {error}")

        suite = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
            check=False,
        )
        suite_returncode = suite.returncode
        suite_stdout = suite.stdout
        suite_stderr = suite.stderr
        summary = suite_stdout + "\n" + suite_stderr
        outcome_counts = [
            int(count)
            for count in re.findall(
                r"\b(\d+)\s+(?:passed|failed|skipped|error|errors|xfailed|xpassed)\b",
                summary,
            )
        ]
        executed_count = sum(outcome_counts)
        if suite_returncode != 0:
            errors.append(f"pytest exited with status {suite_returncode}")
        if executed_count == 0:
            errors.append("pytest reported zero executed cases")
        if executed_count != len(test_names):
            errors.append(
                f"Expected {len(test_names)} test cases from the configured test file, "
                f"but pytest reported {executed_count}"
            )

    inputs = {
        "exercise": "exercises/practice/secret-handshake",
        "test_file": str(test_rel),
        "test_cases_in_file": len(test_names),
        "selected_cases": cases,
        "contract_note": (
            "The instructions state 1 through 31, and an enabled test explicitly specifies "
            "00000 as an empty list. Beyond that zero case, behavior for malformed strings, "
            "non-string values, and values outside the stated range is unspecified."
        ),
    }
    results = {
        "reference_evaluation_returncode": actual_process.returncode,
        "selected_results": selected_actuals,
        "pytest_command": [sys.executable, "-m", "pytest", "-q"],
        "pytest_returncode": suite_returncode,
        "executed_cases": executed_count,
        "expected_cases": len(test_names),
        "errors": errors,
    }
    (EVIDENCE / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "tool-versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    (EVIDENCE / "pytest-output.txt").write_text(suite_stdout + suite_stderr, encoding="utf-8")

    print(f"Executed {executed_count} test cases (expected {len(test_names)}).")
    for item in selected_actuals:
        print(f"{item['test']}: expected {item['expected']!r}; actual {item['actual']!r}")
    if errors:
        print("CHECK FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("All selected results and the full reference suite passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
