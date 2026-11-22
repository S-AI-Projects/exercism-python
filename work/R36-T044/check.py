"""Run all Series cases against the maintained reference in a scratch copy."""

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
SOURCE = ROOT / "exercises/practice/series"
EXPECTED_CASES = 11
ANCHORS = (
    "test_slices_of_one_from_one",
    "test_slices_of_one_from_two",
    "test_slices_of_two",
)


def main() -> None:
    cfg = json.loads((SOURCE / ".meta/config.json").read_text())
    source_solution = SOURCE / cfg["files"]["solution"][0]
    before = hashlib.sha256(source_solution.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="r36-t044-") as temp:
        exercise = Path(temp) / "series"
        shutil.copytree(SOURCE, exercise)
        scratch_cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / scratch_cfg["files"]["solution"][0]
        reference = exercise / scratch_cfg["files"]["example"][0]
        test_file = exercise / scratch_cfg["files"]["test"][0]
        test_source = test_file.read_text()
        for name in ANCHORS:
            assert f"def {name}(" in test_source, f"missing anchor case {name}"
        shutil.copy2(reference, solution)
        args = [sys.executable, "-m", "pytest", "-q"]
        run = subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)
        output = run.stdout + run.stderr
        match = re.search(r"(\d+) passed(?:,|\s)", output)
        actual_cases = int(match.group(1)) if match else 0
        assert run.returncode == 0, f"pytest exited {run.returncode}:\n{output}"
        assert actual_cases == EXPECTED_CASES, f"expected {EXPECTED_CASES}, got {actual_cases}:\n{output}"

    after = hashlib.sha256(source_solution.read_bytes()).hexdigest()
    assert before == after, "working learner solution changed"
    versions = {
        "python": sys.version.split()[0],
        "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
    }
    results = {
        "commands": ["python -m pytest -q"],
        "expected_cases": EXPECTED_CASES,
        "actual_cases": actual_cases,
        "anchors": list(ANCHORS),
        "exit_status": run.returncode,
        "expected": "all enabled Series examples pass",
        "actual": output.strip(),
        "tool_versions": versions,
        "learner_solution_sha256_before_after": [before, after],
    }
    (ROOT / "work/R36-T044/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: {actual_cases}/{EXPECTED_CASES} Series cases pass against the reference.")


if __name__ == "__main__":
    main()
