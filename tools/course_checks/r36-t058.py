#!/usr/bin/env python3
"""
Path and configuration checker for exercises/practice/change/.meta/config.json (R36-T058).
Verifies that all declared file roles resolve safely inside the exercise directory
and detects path traversal or missing files.
"""
import json
import os
import sys
from typing import Dict, Tuple


def validate_config(config_dict: dict, exercise_dir: str) -> Tuple[bool, str]:
    if "files" not in config_dict:
        return False, "Missing 'files' section in config"

    files_obj = config_dict["files"]
    required_roles = ["solution", "test", "example"]
    for role in required_roles:
        if role not in files_obj or not files_obj[role]:
            return False, f"Missing required file role: {role}"

    exercise_dir_real = os.path.realpath(exercise_dir)

    for role, file_list in files_obj.items():
        for rel_path in file_list:
            # Check for illegal path traversal syntax
            if ".." in rel_path.split(os.sep) or rel_path.startswith("/") or rel_path.startswith("\\"):
                return False, f"outside-exercise: illegal path traversal detected in '{rel_path}' for role '{role}'"

            resolved = os.path.realpath(os.path.join(exercise_dir, rel_path))
            if not resolved.startswith(exercise_dir_real + os.sep):
                return False, f"outside-exercise: resolved path '{resolved}' escapes exercise directory"

            if not os.path.isfile(resolved):
                if role == "example":
                    return False, f"missing-reference: example file does not exist at '{rel_path}'"
                elif role == "test":
                    return False, f"missing-test: test file does not exist at '{rel_path}'"
                else:
                    return False, f"missing-file: declared file does not exist at '{rel_path}'"

    return True, "All files resolved and validated successfully."


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_dir = os.path.join(repo_root, "exercises", "practice", "change")
    config_path = os.path.join(exercise_dir, ".meta", "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    valid, msg = validate_config(config_data, exercise_dir)
    if not valid:
        print(f"Validation failed: {msg}", file=sys.stderr)
        return 1

    print(f"Validation passed: {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
