"""Check the bottle-song reference and a deliberately wrong singular rule."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "exercises/practice/bottle-song"
EXPECTED_ALL_CASES = 7
FOCUSED_CASE = "BottleSongTest::test_verse_with_2_bottles"
EXPECTED_FINAL_LINE = "There'll be one green bottle hanging on the wall."
MUTANT_FINAL_LINE = "There'll be one green bottles hanging on the wall."


def run_pytest(exercise: Path, selector: str | None = None) -> subprocess.CompletedProcess[str]:
    config = json.loads((exercise / ".meta/config.json").read_text())
    test_file = config["files"]["test"][0]
    args = [sys.executable, "-m", "pytest", "-q"]
    if selector:
        args.append(f"{test_file}::{selector}")
    return subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)


def passed_count(output: str) -> int:
    match = re.search(r"(\d+) passed(?:,|\s)", output)
    return int(match.group(1)) if match else 0


def main() -> None:
    cfg = json.loads((SOURCE / ".meta/config.json").read_text())
    solution = SOURCE / cfg["files"]["solution"][0]
    before_hash = hashlib.sha256(solution.read_bytes()).hexdigest()

    with tempfile.TemporaryDirectory(prefix="r36-t043-") as temp:
        exercise = Path(temp) / "bottle-song"
        shutil.copytree(SOURCE, exercise)  # copytree includes .docs and .meta.
        scratch_cfg = json.loads((exercise / ".meta/config.json").read_text())
        scratch_solution = exercise / scratch_cfg["files"]["solution"][0]
        reference = exercise / scratch_cfg["files"]["example"][0]
        shutil.copy2(reference, scratch_solution)

        baseline = run_pytest(exercise)
        baseline_output = baseline.stdout + baseline.stderr
        assert baseline.returncode == 0, f"reference suite failed ({baseline.returncode}):\n{baseline_output}"
        assert passed_count(baseline_output) == EXPECTED_ALL_CASES, baseline_output

        original_source = reference.read_text()
        old_condition = "if number -1 == 1:"
        new_condition = "if number == 1:"
        assert old_condition in original_source, "expected reference condition has changed"
        mutant_source = original_source.replace(old_condition, new_condition, 1)
        assert mutant_source != original_source
        reference.write_text(mutant_source)
        shutil.copy2(reference, scratch_solution)

        mutant = run_pytest(exercise, FOCUSED_CASE)
        mutant_output = mutant.stdout + mutant.stderr
        assert mutant.returncode != 0, "the focused case unexpectedly accepted the mutant"
        assert passed_count(mutant_output) == 0 and "1 failed" in mutant_output, mutant_output
        assert EXPECTED_FINAL_LINE in mutant_output and MUTANT_FINAL_LINE in mutant_output, mutant_output

        actual_line = subprocess.run(
            [sys.executable, "-c", "from bottle_song import recite; print(recite(start=2)[-1])"],
            cwd=exercise,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert actual_line == MUTANT_FINAL_LINE

    after_hash = hashlib.sha256(solution.read_bytes()).hexdigest()
    assert before_hash == after_hash, "working learner solution changed"
    results = {
        "python": sys.version.split()[0],
        "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        "commands": {
            "reference": f"{sys.executable} -m pytest -q",
            "mutant": f"{sys.executable} -m pytest -q bottle_song_test.py::{FOCUSED_CASE}",
        },
        "input": {"call": "recite(start=2)", "case": FOCUSED_CASE},
        "mutation": {"from": old_condition, "to": new_condition},
        "reference": {"exit_status": baseline.returncode, "expected_cases": EXPECTED_ALL_CASES, "actual_cases": passed_count(baseline_output), "output": baseline_output.strip()},
        "mutant": {"exit_status": mutant.returncode, "expected_final_line": EXPECTED_FINAL_LINE, "actual_final_line": actual_line, "output": mutant_output.strip()},
        "learner_solution_sha256_before_after": [before_hash, after_hash],
    }
    (ROOT / "work/R36-T043/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print("PASS: reference passes 7 cases; the two-bottle case rejects the mutant.")


if __name__ == "__main__":
    main()
