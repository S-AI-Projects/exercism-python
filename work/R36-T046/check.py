"""Compare the reference and cached-set Allergies approaches on all cases."""

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
SOURCE = ROOT / "exercises/practice/allergies"
ALTERNATIVE = ROOT / "work/R36-T046/approach_set.py"
EXPECTED_CASES = 50
ANCHORS = (
    "test_eggs_not_allergic_to_anything",
    "test_allergic_only_to_eggs",
    "test_allergic_to_eggs_and_something_else",
)
EXAMPLE_START = "<!-- approach-example-start -->"
EXAMPLE_END = "<!-- approach-example-end -->"


def run_cases(implementation: Path, label: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix=f"r36-t046-{label}-") as temp:
        exercise = Path(temp) / "allergies"
        shutil.copytree(SOURCE, exercise)
        cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / cfg["files"]["solution"][0]
        test_file = exercise / cfg["files"]["test"][0]
        test_source = test_file.read_text()
        for name in ANCHORS:
            assert f"def {name}(" in test_source, f"missing anchor case {name}"
        shutil.copy2(implementation, solution)

        args = [sys.executable, "-m", "pytest", "-q"]
        process = subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)
        output = process.stdout + process.stderr
        match = re.search(r"(\d+) passed(?:,|\s)", output)
        count = int(match.group(1)) if match else 0
        assert process.returncode == 0, f"{label} tests exited {process.returncode}:\n{output}"
        assert count == EXPECTED_CASES, f"{label}: expected {EXPECTED_CASES}, got {count}:\n{output}"
        return {"exit_status": process.returncode, "expected_cases": EXPECTED_CASES, "actual_cases": count, "output": output.strip()}


def main() -> None:
    starter = SOURCE / json.loads((SOURCE / ".meta/config.json").read_text())["files"]["solution"][0]
    starter_before = hashlib.sha256(starter.read_bytes()).hexdigest()
    hints = (SOURCE / ".docs/hints.md").read_text()
    snippet = hints.split(EXAMPLE_START, 1)[1].split(EXAMPLE_END, 1)[0]
    code_match = re.search(r"```python\s*([\s\S]*?)```", snippet)
    assert code_match, "approach micro-example is missing"
    example_code = code_match.group(1).strip()
    expected_example = "True\n['eggs', 'shellfish']"
    example = subprocess.run([sys.executable, "-c", example_code], capture_output=True, text=True, check=False)
    assert example.returncode == 0, example.stderr
    assert example.stdout.strip() == expected_example, example.stdout

    reference_result = run_cases(SOURCE / ".meta/example.py", "reference")
    alternative_result = run_cases(ALTERNATIVE, "set")
    starter_after = hashlib.sha256(starter.read_bytes()).hexdigest()
    assert starter_before == starter_after, "working learner starter changed"

    results = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "commands": ["python -m pytest -q"],
        "anchors": list(ANCHORS),
        "reference": reference_result,
        "alternative": alternative_result,
        "worked_input": {"score": 5, "expected": expected_example, "actual": example.stdout.strip(), "exit_status": example.returncode},
        "learner_solution_sha256_before_after": [starter_before, starter_after],
    }
    (ROOT / "work/R36-T046/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: reference and set approach each pass {EXPECTED_CASES}/{EXPECTED_CASES}; worked example matches.")


if __name__ == "__main__":
    main()
