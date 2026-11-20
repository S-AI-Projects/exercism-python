#!/usr/bin/env python3
"""Regenerate rna-transcription tests twice and compare stable output."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TIMESTAMP = re.compile(r"(?m)^# File last updated on \d{4}-\d{2}-\d{2}$")
FOCUSED_CASES = {
    "test_empty_rna_sequence",
    "test_rna_complement_of_cytosine_is_guanine",
    "test_rna_complement_of_guanine_is_cytosine",
}
TOTAL_CASES = 6


def stable(contents: str) -> str:
    return TIMESTAMP.sub("# File last updated on <generated-date>", contents)


def regenerate(repo: Path, spec_path: Path, temp: Path, label: str) -> Path:
    copy = temp / label
    copy.mkdir()
    shutil.copytree(repo / "bin", copy / "bin")
    shutil.copytree(repo / "config", copy / "config")
    shutil.copytree(
        repo / "exercises/practice/rna-transcription",
        copy / "exercises/practice/rna-transcription",
    )
    command = [
        sys.executable,
        "bin/generate_tests.py",
        "rna-transcription",
        "--spec-path",
        str(spec_path),
    ]
    environment = os.environ.copy()
    environment["PATH"] = (
        str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    )
    result = subprocess.run(
        command, cwd=copy, text=True, capture_output=True, env=environment
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"generation {label} failed ({result.returncode}):\n"
            f"{result.stdout}{result.stderr}"
        )
    return copy / "exercises/practice/rna-transcription/rna_transcription_test.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-path",
        type=Path,
        default=Path(".problem-specifications"),
        help="Path to problem-specifications clone",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write verification results JSON",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    spec_path = args.spec_path if args.spec_path.is_absolute() else (repo / args.spec_path).resolve()

    if not spec_path.exists():
        print(f"FAIL: spec-path not found: {spec_path}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        try:
            first_path = regenerate(repo, spec_path, temp, "run-1")
            second_path = regenerate(repo, spec_path, temp, "run-2")
        except RuntimeError as err:
            print(f"FAIL: {err}", file=sys.stderr)
            return 1

        first_text = first_path.read_text()
        second_text = second_path.read_text()

        first_stable = stable(first_text)
        second_stable = stable(second_text)

        failures = []
        if first_stable != second_stable:
            failures.append("test outputs differ between two fresh generations")

        # Verify all focused cases exist
        found_focused = set()
        for case in FOCUSED_CASES:
            if f"def {case}(" in first_stable:
                found_focused.add(case)
            else:
                failures.append(f"focused case {case} missing from generated output")

        all_methods = re.findall(r"def (test_[a-zA-Z0-9_]+)\(", first_stable)
        if len(all_methods) != TOTAL_CASES:
            failures.append(f"expected {TOTAL_CASES} test methods, found {len(all_methods)}")

        payload = {
            "exercise": "exercises/practice/rna-transcription",
            "spec_path": str(spec_path),
            "focused_cases_found": sorted(found_focused),
            "total_methods_found": len(all_methods),
            "generations_reproducible": first_stable == second_stable,
            "status": "passed" if not failures else "failed",
            "failures": failures,
        }

        if args.json_out:
            args.json_out.write_text(json.dumps(payload, indent=2) + "\n")

        if failures:
            for f in failures:
                print(f"FAIL: {f}", file=sys.stderr)
            return 1

        print(
            f"PASS: 2 generations matched stably; {len(all_methods)} methods generated "
            f"including all {len(FOCUSED_CASES)} focused cases."
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
