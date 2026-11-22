"""Execute the Accumulate hint example and test the reference in isolation."""

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
SOURCE = ROOT / "exercises/practice/accumulate"
EXPECTED_CASES = 6
ANCHORS = ("test_empty_sequence", "test_pow", "test_divmod")
START = "<!-- r36-t047-example-start -->"
END = "<!-- r36-t047-example-end -->"
EXPECTED_EXAMPLE = "[1, 4, 9]\n[1, 2, 3]"


def main() -> None:
    hints = (SOURCE / ".docs/hints.md").read_text()
    fenced = hints.split(START, 1)[1].split(END, 1)[0]
    match = re.search(r"```python\s*([\s\S]*?)```", fenced)
    assert match, "Python example missing from hints"
    code = match.group(1).strip()
    example = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert example.returncode == 0, example.stderr
    assert example.stdout.strip() == EXPECTED_EXAMPLE, example.stdout

    cfg = json.loads((SOURCE / ".meta/config.json").read_text())
    learner = SOURCE / cfg["files"]["solution"][0]
    before = hashlib.sha256(learner.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="r36-t047-") as temp:
        exercise = Path(temp) / "accumulate"
        shutil.copytree(SOURCE, exercise)
        scratch_cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / scratch_cfg["files"]["solution"][0]
        test_file = exercise / scratch_cfg["files"]["test"][0]
        test_source = test_file.read_text()
        for name in ANCHORS:
            assert f"def {name}(" in test_source, f"missing anchor {name}"
        shutil.copy2(exercise / scratch_cfg["files"]["example"][0], solution)

        args = [sys.executable, "-m", "pytest", "-q"]
        run = subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)
        output = run.stdout + run.stderr
        count_match = re.search(r"(\d+) passed(?:,|\s)", output)
        actual_count = int(count_match.group(1)) if count_match else 0
        assert run.returncode == 0, f"reference suite exited {run.returncode}:\n{output}"
        assert actual_count == EXPECTED_CASES, f"expected {EXPECTED_CASES}, got {actual_count}:\n{output}"

    after = hashlib.sha256(learner.read_bytes()).hexdigest()
    assert before == after, "learner starter changed"
    results = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "example": {"expected_stdout": EXPECTED_EXAMPLE, "actual_stdout": example.stdout.strip(), "exit_status": example.returncode},
        "test_command": args,
        "expected_cases": EXPECTED_CASES,
        "actual_cases": actual_count,
        "test_exit_status": run.returncode,
        "test_output": output.strip(),
        "anchors": list(ANCHORS),
        "learner_solution_sha256_before_after": [before, after],
    }
    (ROOT / "work/R36-T047/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: hint example output matches; reference passes {actual_count}/{EXPECTED_CASES} tests.")


if __name__ == "__main__":
    main()
