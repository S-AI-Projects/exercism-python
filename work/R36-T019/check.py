#!/usr/bin/env python3
"""Acceptance checks for the house isolated reference runner."""

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "tools/course_checks/r36-t019.py"
VENV_PYTHON = Path(__file__).resolve().parent / ".venv/bin/python"
PYTHON = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
LEARNER = ROOT / "exercises/practice/house/house.py"
EVIDENCE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    original_hash = sha256(LEARNER)
    with tempfile.TemporaryDirectory(prefix="house-check-inputs-") as directory:
        bad_reference = Path(directory) / "bad_reference.py"
        bad_reference.write_text("def recite(start_verse, end_verse):\n    return []\n", encoding="utf-8")
        cases = [
            ("reference", ["--python", str(PYTHON)], 0, 14),
            ("assertion_failure", ["--python", str(PYTHON), "--reference", str(bad_reference)], 1, 14),
            ("zero_tests", ["--python", str(PYTHON), "--", "-k", "definitely_no_house_case_matches"], 1, 0),
        ]
        results = []
        for name, arguments, expected_status, expected_count in cases:
            completed = subprocess.run(
                [sys.executable, str(RUNNER), *arguments],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            after_hash = sha256(LEARNER)
            status_ok = completed.returncode == expected_status
            count_line = next((line for line in completed.stdout.splitlines() if line.startswith("Executed cases:")), "")
            try:
                actual_count = int(count_line.partition(":")[2].strip())
            except ValueError:
                actual_count = None
            count_ok = actual_count == expected_count
            hash_ok = after_hash == original_hash
            results.append({
                "case": name,
                "expected_exit": expected_status,
                "actual_exit": completed.returncode,
                "expected_cases": expected_count,
                "actual_cases": actual_count,
                "learner_sha256_before": original_hash,
                "learner_sha256_after": after_hash,
                "learner_unchanged": hash_ok,
                "exit_matches": status_ok,
                "count_matches": count_ok,
                "assertions_passed": status_ok and count_ok and hash_ok,
                "output": completed.stdout,
            })
            if not status_ok or not count_ok or not hash_ok:
                print(f"FAIL {name}: expected exit/count {expected_status}/{expected_count}; got {completed.returncode}/{actual_count}")
            else:
                print(f"PASS {name}: exit {completed.returncode}, {actual_count} cases, learner hash unchanged")

    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    inputs = {
        "runner": "tools/course_checks/r36-t019.py",
        "learner": "exercises/practice/house/house.py",
        "reference_command": ["python3", "tools/course_checks/r36-t019.py", "--python", "work/R36-T019/.venv/bin/python"],
        "failure_command": ["python3", "tools/course_checks/r36-t019.py", "--python", "work/R36-T019/.venv/bin/python", "--reference", "<temporary bad_reference.py>"],
        "zero_test_command": ["python3", "tools/course_checks/r36-t019.py", "--python", "work/R36-T019/.venv/bin/python", "--", "-k", "definitely_no_house_case_matches"],
        "expected_cases": 14,
        "bad_reference_source": "def recite(start_verse, end_verse): return []",
    }
    (EVIDENCE / "inputs.json").write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
    versions = {
        "python": sys.version,
        "platform": platform.platform(),
        "pytest": subprocess.run([str(PYTHON), "-m", "pytest", "--version"], text=True, capture_output=True).stdout.strip(),
        "pytest_subtests": subprocess.run([str(PYTHON), "-m", "pip", "show", "pytest-subtests"], text=True, capture_output=True).stdout.split("Version: ", 1)[-1].splitlines()[0],
    }
    (EVIDENCE / "tool-versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    return 0 if all(result["assertions_passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
