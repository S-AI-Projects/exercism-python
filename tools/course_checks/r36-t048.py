"""Validate Exercism exercise file roles and paths from .meta/config.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REQUIRED_ROLES = ("solution", "test", "example")


def validate(config_path: Path, exercise_root: Path) -> dict[str, list[str]]:
    root = exercise_root.resolve()
    config = json.loads(config_path.read_text())
    files = config.get("files")
    if not isinstance(files, dict):
        raise ValueError("config must contain a files object")

    for role in REQUIRED_ROLES:
        if role not in files:
            raise ValueError(f"required file role is missing: {role}")

    resolved: dict[str, list[str]] = {}
    for role, entries in files.items():
        if not isinstance(entries, list) or not all(isinstance(item, str) for item in entries):
            raise ValueError(f"file role {role} must be a list of relative paths")
        if role in REQUIRED_ROLES and not entries:
            raise ValueError(f"required file role is empty: {role}")

        resolved[role] = []
        for entry in entries:
            path = Path(entry)
            if path.is_absolute():
                raise ValueError(f"file role {role} uses an absolute path: {entry}")
            if ".." in path.parts:
                raise ValueError(f"file role {role} uses parent traversal: {entry}")
            target = (root / path).resolve()
            try:
                target.relative_to(root)
            except ValueError as error:
                raise ValueError(f"file role {role} resolves outside the exercise: {entry}") from error
            if not target.is_file():
                raise ValueError(f"file role {role} references a missing file: {entry}")
            resolved[role].append(str(target))
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exercise-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.config, args.exercise_root)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
