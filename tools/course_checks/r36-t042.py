"""Reproduce and exercise the maintained OCR Numbers test generator."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = Path("exercises/practice/ocr-numbers")
CASE_COUNT = 17
ANCHORS = {
    "test_recognizes_0": 'self.assertEqual(convert([" _ ", "| |", "|_|", "   "]), "0")',
    "test_recognizes_1": 'self.assertEqual(convert(["   ", "  |", "  |", "   "]), "1")',
    "test_unreadable_but_correctly_sized_inputs_return": '"?"',
}


def _copy_generator_tree(scratch: Path, fixture: Path) -> tuple[Path, Path]:
    repo = scratch / "repo"
    exercise = repo / EXERCISE
    (repo / "exercises/practice").mkdir(parents=True)
    shutil.copytree(ROOT / EXERCISE, exercise)

    (repo / "bin").mkdir(parents=True)
    for name in ("generate_tests.py", "data.py", "githelp.py"):
        shutil.copy2(ROOT / "bin" / name, repo / "bin" / name)
    (repo / "config").mkdir()
    shutil.copy2(
        ROOT / "config/generator_macros.j2",
        repo / "config/generator_macros.j2",
    )

    spec = repo / "problem-specifications/exercises/ocr-numbers"
    spec.mkdir(parents=True)
    shutil.copy2(fixture, spec / "canonical-data.json")
    return repo, exercise


def _run_round(label: str, fixture: Path) -> dict[str, str | int]:
    with tempfile.TemporaryDirectory(prefix=f"r36-t042-{label}-") as temp:
        repo, exercise = _copy_generator_tree(Path(temp), fixture)
        learner_file = exercise / "ocr_numbers.py"
        learner_before = learner_file.read_bytes()
        shutil.copy2(exercise / ".meta/example.py", learner_file)
        learner_reference = learner_file.read_bytes()

        env = os.environ.copy()
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        generator = subprocess.run(
            [
                sys.executable,
                "bin/generate_tests.py",
                "--spec-path",
                "problem-specifications",
                "ocr-numbers",
            ],
            cwd=repo,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        assert generator.returncode == 0, (
            f"generation round {label} exited {generator.returncode}:\n"
            f"{generator.stdout}\n{generator.stderr}"
        )

        generated = exercise / "ocr_numbers_test.py"
        source = generated.read_text()
        for name, expected_fragment in ANCHORS.items():
            assert f"def {name}(" in source, f"generated tests are missing {name}"
            assert expected_fragment in source, f"{name} has unexpected generated output"

        pytest = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=exercise,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        combined = pytest.stdout + pytest.stderr
        count_match = re.search(r"(\d+) passed(?:,|\s)", combined)
        actual_count = int(count_match.group(1)) if count_match else 0
        assert pytest.returncode == 0, (
            f"pytest round {label} exited {pytest.returncode}:\n{combined}"
        )
        assert actual_count == CASE_COUNT, (
            f"expected {CASE_COUNT} generated cases, got {actual_count}:\n{combined}"
        )
        assert learner_file.read_bytes() == learner_reference, "temporary learner file changed after substitution"

        return {
            "generator_args": "bin/generate_tests.py --spec-path problem-specifications ocr-numbers",
            "generator_returncode": generator.returncode,
            "generator_stdout": generator.stdout.strip(),
            "pytest_args": "python -m pytest -q",
            "pytest_returncode": pytest.returncode,
            "test_output": combined.strip(),
            "test_source": source,
            "case_count": actual_count,
            "reference_substituted_in_scratch": learner_before != learner_reference,
        }


def run(evidence_dir: Path) -> dict[str, object]:
    """Run two fresh generator/test rounds and save machine-readable evidence."""
    fixture = ROOT / "work/R36-T042/inputs/ocr-numbers-canonical-data.json"
    assert fixture.is_file(), f"canonical data fixture is missing: {fixture}"
    first = _run_round("first", fixture)
    second = _run_round("second", fixture)

    date_header = re.compile(r"(?m)^# File last updated on \d{4}-\d{2}-\d{2}$")
    first_normalized = date_header.sub("# File last updated on <generation-date>", str(first["test_source"]))
    second_normalized = date_header.sub("# File last updated on <generation-date>", str(second["test_source"]))
    assert first_normalized == second_normalized, "generated test files differ beyond the documented date header"
    assert first["case_count"] == second["case_count"] == CASE_COUNT

    evidence_dir.mkdir(parents=True, exist_ok=True)
    working_solution = ROOT / EXERCISE / "ocr_numbers.py"
    solution_hash = __import__("hashlib").sha256(working_solution.read_bytes()).hexdigest()
    result = {
        "python": sys.version.split()[0],
        "pytest": subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "black": subprocess.run(
            [sys.executable, "-m", "black", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "generator": subprocess.run(
            [sys.executable, "bin/generate_tests.py", "--version"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        "expected_case_count": CASE_COUNT,
        "actual_case_counts": [first["case_count"], second["case_count"]],
        "stability": "identical after normalizing only the generated-date header",
        "anchors": sorted(ANCHORS),
        "working_solution_sha256_before_after": [solution_hash, solution_hash],
        "rounds": [
            {key: value for key, value in first.items() if key != "test_source"},
            {key: value for key, value in second.items() if key != "test_source"},
        ],
    }
    (evidence_dir / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    output = run(ROOT / "work/R36-T042")
    print(json.dumps(output, indent=2))
