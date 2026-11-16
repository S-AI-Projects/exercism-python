#!/usr/bin/env python3
"""Regenerate protein-translation tests twice and compare stable output."""

from __future__ import annotations

import argparse
from importlib.metadata import version
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TIMESTAMP = re.compile(r"(?m)^# File last updated on \d{4}-\d{2}-\d{2}$")
FOCUSED_CASES = {
    "test_methionine_rna_sequence",
    "test_phenylalanine_rna_sequence_1",
    "test_phenylalanine_rna_sequence_2",
}


def stable(contents: str) -> str:
    return TIMESTAMP.sub("# File last updated on <generated-date>", contents)


def regenerate(repo: Path, spec_path: Path, temp: Path, label: str) -> Path:
    copy = temp / label
    copy.mkdir()
    shutil.copytree(repo / "bin", copy / "bin")
    shutil.copytree(repo / "config", copy / "config")
    shutil.copytree(
        repo / "exercises/practice/protein-translation",
        copy / "exercises/practice/protein-translation",
    )
    command = [
        sys.executable,
        "bin/generate_tests.py",
        "protein-translation",
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
    if result.returncode:
        raise RuntimeError(
            f"generation {label} failed ({result.returncode}):\n"
            f"{result.stdout}{result.stderr}"
        )
    return copy / "exercises/practice/protein-translation/protein_translation_test.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-path",
        type=Path,
        default=Path(".problem-specifications"),
        help="local problem-specifications checkout (default: .problem-specifications)",
    )
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    spec_path = args.spec_path.resolve()
    canonical = spec_path / "exercises/protein-translation/canonical-data.json"
    if not canonical.is_file():
        parser.error(f"canonical data not found: {canonical}")

    config = json.loads(
        (repo / "exercises/practice/protein-translation/.meta/config.json").read_text()
    )
    test_files = config["files"]["test"]
    if test_files != ["protein_translation_test.py"]:
        raise RuntimeError(f"unexpected configured test files: {test_files}")

    with tempfile.TemporaryDirectory(prefix="r36-t012-generation-") as directory:
        temp = Path(directory)
        first = regenerate(repo, spec_path, temp, "copy-one")
        second = regenerate(repo, spec_path, temp, "copy-two")
        first_text = first.read_text()
        second_text = second.read_text()
        if stable(first_text) != stable(second_text):
            raise AssertionError("fresh generations differ beyond the date header")

        generated_methods = set(re.findall(r"^    def (test_\w+)\(", first_text, re.M))
        checked_in_tests = repo.joinpath(
            "exercises/practice/protein-translation/protein_translation_test.py"
        )
        checked_in_text = checked_in_tests.read_text()
        checked_in_methods = set(
            re.findall(r"^    def (test_\w+)\(", checked_in_text, re.M)
        )
        missing = FOCUSED_CASES - generated_methods
        if missing:
            raise AssertionError(
                f"focused cases missing from generation: {sorted(missing)}"
            )
        if generated_methods != checked_in_methods:
            raise AssertionError(
                "generated methods differ from the checked-in test module: "
                f"missing={sorted(checked_in_methods - generated_methods)}, "
                f"unexpected={sorted(generated_methods - checked_in_methods)}"
            )
        if stable(first_text) != stable(checked_in_text):
            raise AssertionError(
                "freshly generated test module differs from the checked-in file "
                "beyond the generated date header"
            )
        if len(generated_methods) != 26:
            raise AssertionError(
                f"expected all 26 enabled canonical cases, got {len(generated_methods)}"
            )
        evidence = repo / "work/R36-T012"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "generation-results.json").write_text(
            f"{json.dumps(
                {
                    "command": [
                        sys.executable,
                        "bin/generate_tests.py",
                        "protein-translation",
                        "--spec-path",
                        str(spec_path),
                    ],
                    "input_files": [
                        "exercises/practice/protein-translation/.meta/tests.toml",
                        "exercises/practice/protein-translation/.meta/template.j2",
                        "config/generator_macros.j2",
                        "problem-specifications/exercises/protein-translation/canonical-data.json",
                    ],
                    "expected": {
                        "enabled_case_count": 26,
                        "focused_cases": sorted(FOCUSED_CASES),
                    },
                    "actual": {
                        "copy_one_case_count": len(generated_methods),
                        "copy_two_case_count": len(generated_methods),
                        "checked_in_case_count": len(checked_in_methods),
                        "focused_cases_present": sorted(FOCUSED_CASES),
                        "same_after_timestamp_normalization": True,
                        "normalization": "replace only '# File last updated on YYYY-MM-DD'",
                        "copy_one_generated_date": re.search(
                            r"(?m)^# File last updated on (\d{4}-\d{2}-\d{2})$",
                            first_text,
                        ).group(1),
                        "copy_two_generated_date": re.search(
                            r"(?m)^# File last updated on (\d{4}-\d{2}-\d{2})$",
                            second_text,
                        ).group(1),
                    },
                },
                indent=2,
            )}\n"
        )
        (evidence / "generation-tool-versions.txt").write_text(
            f"Python: {platform.python_version()} ({sys.executable})\n"
            f"Generator: {subprocess.run([sys.executable, 'bin/generate_tests.py', '--version'], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()}\n"
            f"Jinja2: {version('Jinja2')}\n"
            f"Black: {version('black')}\n"
        )
        print("Generation command:")
        print(
            f"{sys.executable} bin/generate_tests.py protein-translation "
            f"--spec-path {spec_path}"
        )
        print("Generated test methods: 26 (all enabled cases present)")
        print(
            "Fresh copy comparison: identical after normalizing only the generated date"
        )
        print("Focused cases: " + ", ".join(sorted(FOCUSED_CASES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
