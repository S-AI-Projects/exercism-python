#!/usr/bin/env python3
"""Validate crypto-square metadata paths and their resolution in the exercise runner."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/crypto-square"
ROLES = ("solution", "test", "example", "editor")
EXPECTED_TESTS = 8


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
            if not str(target).startswith(str(root)):
                raise ConfigError(f"files.{role} path escapes exercise: {name}")
            if not target.is_file():
                raise ConfigError(f"files.{role} file does not exist: {name}")
            paths.append(target)
        resolved[role] = paths
    for required in ("solution", "test", "example"):
        if required not in resolved:
            raise ConfigError(f"files.{required} is required")
    return resolved


def main() -> int:
    config_path = EXERCISE / ".meta/config.json"
    config = json.loads(config_path.read_text())

    # 1. Real config must pass
    try:
        resolved = resolve_files(config, EXERCISE)
    except ConfigError as err:
        print(f"FAIL: real config rejected: {err}", file=sys.stderr)
        return 1

    # 2. Test 3 deliberately invalid metadata fixtures
    # Fixture A: missing reference
    bad_config_a = json.loads(json.dumps(config))
    bad_config_a["files"]["example"] = [".meta/non_existent_example.py"]
    try:
        resolve_files(bad_config_a, EXERCISE)
        print("FAIL: fixture with missing example unexpectedly passed", file=sys.stderr)
        return 1
    except ConfigError:
        pass

    # Fixture B: missing test
    bad_config_b = json.loads(json.dumps(config))
    bad_config_b["files"]["test"] = ["non_existent_test.py"]
    try:
        resolve_files(bad_config_b, EXERCISE)
        print("FAIL: fixture with missing test unexpectedly passed", file=sys.stderr)
        return 1
    except ConfigError:
        pass

    # Fixture C: path traversal
    bad_config_c = json.loads(json.dumps(config))
    bad_config_c["files"]["example"] = ["../outside_example.py"]
    try:
        resolve_files(bad_config_c, EXERCISE)
        print("FAIL: fixture with path traversal unexpectedly passed", file=sys.stderr)
        return 1
    except ConfigError:
        pass

    # 3. Run pytest against reference in a scratch copy
    with tempfile.TemporaryDirectory() as temp_dir:
        scratch = Path(temp_dir) / "exercise"
        shutil.copytree(EXERCISE, scratch)
        solution_name = config["files"]["solution"][0]
        example_rel = config["files"]["example"][0]
        shutil.copy2(EXERCISE / example_rel, scratch / solution_name)

        pytest_cmd = [sys.executable, "-m", "pytest", "-q"]
        child = subprocess.run(
            pytest_cmd,
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        if child.returncode != 0:
            print(f"FAIL: pytest exited non-zero ({child.returncode}):\n{child.stdout}{child.stderr}", file=sys.stderr)
            return 1

        passed_match = re.search(r"(\d+) passed", child.stdout)
        executed = int(passed_match.group(1)) if passed_match else 0
        if executed != EXPECTED_TESTS:
            print(f"FAIL: expected {EXPECTED_TESTS} tests, got {executed}", file=sys.stderr)
            return 1

    print(f"PASS: metadata validated, 3 invalid fixtures rejected, {executed} tests passed on reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
