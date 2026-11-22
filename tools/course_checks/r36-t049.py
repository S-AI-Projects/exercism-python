"""Run the Camicia reference safely in a disposable copy of the exercise."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXERCISE = ROOT / "exercises/practice/camicia"


def resolve(exercise: Path, config: dict[str, object], role: str) -> Path:
    files = config.get("files")
    if not isinstance(files, dict) or not isinstance(files.get(role), list) or not files[role]:
        raise ValueError(f"missing files.{role} entry in config")
    entry = files[role][0]
    if not isinstance(entry, str) or Path(entry).is_absolute() or ".." in Path(entry).parts:
        raise ValueError(f"invalid files.{role} path: {entry}")
    root = exercise.resolve()
    target = (root / entry).resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValueError(f"files.{role} resolves outside the exercise: {entry}") from error
    if not target.is_file():
        raise ValueError(f"files.{role} file is missing: {entry}")
    return target


def learner_hashes(exercise: Path) -> dict[str, str]:
    config = json.loads((exercise / ".meta/config.json").read_text())
    files = config["files"]["solution"]
    return {
        name: hashlib.sha256(resolve(exercise, config, "solution").read_bytes()).hexdigest()
        for name in files
    }


def executed_count(output: str) -> int:
    counts = [int(value) for value in re.findall(r"\b(\d+) (?:passed|failed|skipped|xfailed|xpassed|error|errors)\b", output)]
    return sum(counts)


def run_isolated(
    exercise_source: Path = DEFAULT_EXERCISE,
    reference_source: Path | None = None,
    pytest_filter: str | None = None,
    temp_parent: Path | None = None,
) -> dict[str, object]:
    source_config = json.loads((exercise_source / ".meta/config.json").read_text())
    source_solution = resolve(exercise_source, source_config, "solution")
    reference = reference_source or resolve(exercise_source, source_config, "example")
    hashes_before = learner_hashes(exercise_source)

    with tempfile.TemporaryDirectory(prefix="r36-t049-run-", dir=temp_parent) as temp:
        scratch = Path(temp) / "camicia"
        shutil.copytree(exercise_source, scratch)  # Hidden .meta/.docs files are included.
        config = json.loads((scratch / ".meta/config.json").read_text())
        solution = resolve(scratch, config, "solution")
        test_file = resolve(scratch, config, "test")
        shutil.copy2(reference, solution)

        command = [sys.executable, "-m", "pytest", "-q", str(test_file)]
        if pytest_filter is not None:
            command.extend(("-k", pytest_filter))
        child = subprocess.run(command, cwd=scratch, capture_output=True, text=True, check=False)
        output = child.stdout + child.stderr
        cases = executed_count(output)
        runner_status = 0 if child.returncode == 0 and cases > 0 else 1
        if cases == 0:
            failure_reason = "pytest selected zero tests"
        elif child.returncode != 0:
            failure_reason = "pytest child exited nonzero"
        else:
            failure_reason = None

    hashes_after = learner_hashes(exercise_source)
    assert hashes_before == hashes_after, "learner solution changed during isolated run"
    return {
        "command": command,
        "child_exit_status": child.returncode,
        "runner_exit_status": runner_status,
        "failure_reason": failure_reason,
        "executed_cases": cases,
        "output": output.strip(),
        "learner_hashes_before": hashes_before,
        "learner_hashes_after": hashes_after,
        "temporary_copy_removed": not scratch.exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exercise-root", type=Path, default=DEFAULT_EXERCISE)
    parser.add_argument("--reference-source", type=Path)
    parser.add_argument("--pytest-filter")
    parser.add_argument("--temp-parent", type=Path)
    args = parser.parse_args()
    try:
        result = run_isolated(args.exercise_root, args.reference_source, args.pytest_filter, args.temp_parent)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(json.dumps({"runner_exit_status": 1, "error": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return int(result["runner_exit_status"])


if __name__ == "__main__":
    raise SystemExit(main())
