#!/usr/bin/env python3
"""
tools/course_checks/r36-t038.py
Validation checker for diamond file layout and config.json metadata.
"""

import json
import os
import sys


def verify_diamond_configuration():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    exercise_dir = os.path.join(repo_root, "exercises", "practice", "diamond")
    config_file = os.path.join(exercise_dir, ".meta", "config.json")

    assert os.path.exists(config_file), f"Missing config file: {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    files_map = data.get("files", {})
    required_keys = ["solution", "test", "example"]
    for key in required_keys:
        assert key in files_map, f"Missing key '{key}' in files configuration"
        for rel_path in files_map[key]:
            full_path = os.path.join(exercise_dir, rel_path)
            assert os.path.exists(full_path), f"File mapped under '{key}' not found: {full_path}"

    # Verify learner stub is unsolved
    stub_path = os.path.join(exercise_dir, files_map["solution"][0])
    with open(stub_path, "r", encoding="utf-8") as f:
        stub = f.read()
    assert "pass" in stub, "Learner stub must be unsolved!"

    # Verify example exists and has logic
    ex_path = os.path.join(exercise_dir, files_map["example"][0])
    with open(ex_path, "r", encoding="utf-8") as f:
        ex = f.read()
    assert "def rows" in ex and "pass" not in ex, "Example implementation invalid"

    print("Diamond configuration and file-role mapping successfully validated.")
    return True


if __name__ == "__main__":
    verify_diamond_configuration()
