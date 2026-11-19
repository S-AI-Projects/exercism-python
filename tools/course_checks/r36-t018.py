#!/usr/bin/env python3
"""Validate nth-prime metadata paths and their resolution in the exercise runner."""

from __future__ import annotations

import json
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/nth-prime"
ROLES = ("solution", "test", "example", "editor")


class ConfigError(ValueError):
    """A declared exercise file is invalid or unavailable."""


def resolve_files(config: dict, exercise: Path) -> dict[str, list[Path]]:
    """Resolve declared file-role paths, rejecting traversal and missing files."""
    files = config.get("files")
    if not isinstance(files, dict):
        raise ConfigError("files must be an object")

    root = exercise.resolve(strict=True)
    resolved: dict[str, list[Path]] = {}
    for role in ROLES:
        if role not in files:
            continue
        names = files[role]
        if not isinstance(names, list) or not names:
            raise ConfigError(f"files.{role} must be a non-empty list")
        paths = []
        for name in names:
            if not isinstance(name, str) or not name:
                raise ConfigError(f"files.{role} entries must be non-empty strings")
            relative = Path(name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ConfigError(f"files.{role} path escapes exercise: {name}")
            target = (root / relative).resolve(strict=False)
            if not target.is_relative_to(root):
                raise ConfigError(f"files.{role} path escapes exercise: {name}")
            if not target.is_file():
                raise ConfigError(f"files.{role} file does not exist: {name}")
            paths.append(target)
        resolved[role] = paths
    for required in ("solution", "test", "example"):
        if required not in resolved:
            raise ConfigError(f"files.{required} is required")
    return resolved


def load_and_resolve(config_path: Path, exercise: Path) -> tuple[dict, dict[str, list[Path]]]:
    config = json.loads(config_path.read_text())
    return config, resolve_files(config, exercise)


def write_fixture(directory: Path, label: str, config: dict, exercise: Path,
                  mutate: str) -> tuple[Path, Path]:
    fixture = directory / label
    shutil.copytree(exercise, fixture)
    broken = json.loads(json.dumps(config))
    if mutate == "missing-reference":
        broken["files"]["example"] = [".meta/absent_reference.py"]
    elif mutate == "missing-test":
        broken["files"]["test"] = ["absent_test.py"]
    elif mutate == "outside-exercise":
        broken["files"]["example"] = ["../outside.py"]
    else:
        raise ValueError(mutate)
    config_path = fixture / ".meta/config.json"
    config_path.write_text(json.dumps(broken, indent=2) + "\n")
    return config_path, fixture


def exercise_metadata_checks(config: dict) -> list[dict]:
    results = []
    with tempfile.TemporaryDirectory(prefix="nth-prime-config-fixtures-") as temp:
        temp_root = Path(temp)
        for label in ("missing-reference", "missing-test", "outside-exercise"):
            fixture_config, fixture_exercise = write_fixture(
                temp_root, label, config, EXERCISE, label
            )
            try:
                load_and_resolve(fixture_config, fixture_exercise)
            except ConfigError as error:
                intended = {
                    "missing-reference": "file does not exist",
                    "missing-test": "file does not exist",
                    "outside-exercise": "escapes exercise",
                }[label]
                if intended not in str(error):
                    raise AssertionError(f"{label}: unexpected rejection: {error}")
                results.append({"fixture": label, "expected": intended,
                                "actual": str(error), "passed": True})
            else:
                raise AssertionError(f"{label}: invalid metadata unexpectedly passed")
    return results


def pytest_run(solution: Path, solution_name: str, scratch: Path) -> dict:
    shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copy2(solution, scratch / solution_name)
    command = [sys.executable, "-m", "pytest", "-q"]
    result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
    output = result.stdout + result.stderr
    match = re.search(r"(?m)(\d+) passed(?:,|\s|$)", output)
    count = int(match.group(1)) if match else 0
    return {"command": ["python3", "-m", "pytest", "-q"],
            "return_code": result.returncode, "executed": count,
            "output": output}


def main() -> None:
    evidence = ROOT / "work/R36-T018"
    evidence.mkdir(parents=True, exist_ok=True)
    config_path = EXERCISE / ".meta/config.json"
    config, paths = load_and_resolve(config_path, EXERCISE)
    required_cases = ("test_first_prime", "test_second_prime", "test_sixth_prime")
    test_source = paths["test"][0].read_text()
    missing_cases = [case for case in required_cases if f"def {case}(" not in test_source]
    if missing_cases:
        raise AssertionError(f"required test cases missing: {missing_cases}")

    expected_count = len(re.findall(r"(?m)^\s+def test_[A-Za-z0-9_]+\(", test_source))
    if expected_count == 0:
        raise AssertionError("test file contains no test cases")
    with tempfile.TemporaryDirectory(prefix="nth-prime-reference-") as temporary:
        scratch = Path(temporary) / "nth-prime"
        outcome = pytest_run(paths["example"][0], paths["solution"][0].relative_to(EXERCISE).as_posix(), scratch)

    if outcome["return_code"] != 0:
        raise AssertionError(f"pytest exited {outcome['return_code']}\n{outcome['output']}")
    if outcome["executed"] == 0:
        raise AssertionError("pytest ran zero tests")
    if outcome["executed"] != expected_count:
        raise AssertionError(f"pytest ran {outcome['executed']} tests; expected {expected_count}")

    fixtures = exercise_metadata_checks(config)
    named_inputs = {
        "test_first_prime": {"argument": 1, "expected": 2},
        "test_second_prime": {"argument": 2, "expected": 3},
        "test_sixth_prime": {"argument": 6, "expected": 13},
    }
    reference_prime = runpy.run_path(str(paths["example"][0]))["prime"]
    named_results = {}
    for name, values in named_inputs.items():
        actual = reference_prime(values["argument"])
        named_results[name] = {"input": f"prime({values['argument']})",
                               "expected": values["expected"], "actual": actual,
                               "passed": actual == values["expected"]}
        if actual != values["expected"]:
            raise AssertionError(f"{name}: expected {values['expected']}, got {actual}")
    resolved_display = {
        role: [str(path.relative_to(EXERCISE)) for path in role_paths]
        for role, role_paths in paths.items()
    }
    (evidence / "inputs.json").write_text(json.dumps({
        "exercise": "exercises/practice/nth-prime",
        "config": "exercises/practice/nth-prime/.meta/config.json",
        "files": config["files"],
        "resolved_inside_exercise": resolved_display,
        "editor_role_declared": "editor" in config["files"],
        "required_cases": list(required_cases),
        "named_case_inputs": {name: result["input"] for name, result in named_results.items()},
        "pytest_command": ["python3", "-m", "pytest", "-q"],
    }, indent=2) + "\n")
    (evidence / "pytest-output.txt").write_text(outcome["output"])
    result_data = {
        "expected": {"pytest_return_code": 0, "executed_tests": expected_count,
                     "invalid_fixtures_rejected": 3},
        "actual": {"pytest_return_code": outcome["return_code"],
                   "executed_tests": outcome["executed"],
                   "named_case_results": named_results,
                   "invalid_fixtures": fixtures},
    }
    (evidence / "results.json").write_text(json.dumps(result_data, indent=2) + "\n")
    versions = {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"],
                                  check=True, capture_output=True, text=True).stdout.strip(),
        "pytest-subtests": __import__("importlib.metadata", fromlist=["version"]).version(
            "pytest-subtests"
        ),
        "configlet": "not used; the config was unchanged",
    }
    (evidence / "versions.json").write_text(json.dumps(versions, indent=2) + "\n")
    print(f"Reference: {outcome['executed']}/{expected_count} tests passed (exit 0).")
    for fixture in fixtures:
        print(f"{fixture['fixture']}: rejected as expected ({fixture['actual']}).")
    print("PASS: metadata paths are valid and all checks passed.")


if __name__ == "__main__":
    main()
