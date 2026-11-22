#!/usr/bin/env python3
"""
Reusable focused regeneration and reproducibility check for space-age (Task R36-T022).

Checks:
1. Performs two independent test generations in fresh scratch directories.
2. Compares the resulting space_age_test.py files after normalizing the generated timestamp.
3. Asserts that no test cases are silently dropped (all 8 enabled cases must be present).
4. Verifies the anchored test cases:
   - test_age_on_earth
   - test_age_on_mercury
   - test_age_on_venus
5. Exits 0 on success, non-zero on failure.
"""

from __future__ import annotations

import difflib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ANCHORED_CASES = [
    "test_age_on_earth",
    "test_age_on_mercury",
    "test_age_on_venus",
]

ALL_ENABLED_CASES = [
    "test_age_on_earth",
    "test_age_on_mercury",
    "test_age_on_venus",
    "test_age_on_mars",
    "test_age_on_jupiter",
    "test_age_on_saturn",
    "test_age_on_uranus",
    "test_age_on_neptune",
]


def find_spec_path(repo_root: Path) -> Path | None:
    candidates = [
        repo_root / ".problem-specifications",
        Path("/tmp/problem-specifications"),
        Path.home() / ".cache/exercism/problem-specifications",
    ]
    for c in candidates:
        if (c / "exercises/space-age/canonical-data.json").is_file():
            return c
    return None


def run_generation(repo_root: Path, target_dir: Path, spec_path: Path | None) -> Path:
    # Setup exercise workspace inside target_dir
    shutil.copytree(repo_root / "config", target_dir / "config")
    shutil.copytree(repo_root / "bin", target_dir / "bin")
    exercise_dest = target_dir / "exercises/practice/space-age"
    shutil.copytree(repo_root / "exercises/practice/space-age", exercise_dest)

    cmd = [sys.executable, "bin/generate_tests.py"]
    if spec_path:
        cmd.extend(["-p", str(spec_path)])
    cmd.append("space-age")

    proc = subprocess.run(cmd, cwd=str(target_dir), capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"Generation failed in {target_dir}:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

    generated_test = exercise_dest / "space_age_test.py"
    if not generated_test.is_file():
        raise FileNotFoundError(f"Generated test file not found at {generated_test}")
    return generated_test


def normalize_lines(lines: list[str]) -> list[str]:
    """
    Normalizes generated test lines by skipping the header timestamp (lines 1-3)
    matching bin/generate_tests.py:check_template behavior.
    """
    # The header occupies lines 1-3:
    # 1: # These tests are auto-generated with test data from:
    # 2: # https://github.com/exercism/problem-specifications/...
    # 3: # File last updated on YYYY-MM-DD
    if len(lines) >= 3 and lines[0].startswith("# These tests are auto-generated"):
        return lines[3:]
    return lines


def main() -> int:
    print("[*] Running reusable focused regeneration check for space-age...")
    repo_root = Path(__file__).resolve().parent.parent.parent
    spec_path = find_spec_path(repo_root)

    if spec_path:
        print(f"[*] Using local problem-specifications: {spec_path}")
    else:
        print("[*] No local problem-specifications found; generate_tests.py will clone if needed.")

    with tempfile.TemporaryDirectory() as tmp1_str, tempfile.TemporaryDirectory() as tmp2_str:
        tmp1 = Path(tmp1_str)
        tmp2 = Path(tmp2_str)

        print("[*] Running Generation 1 in temporary directory...")
        test1_path = run_generation(repo_root, tmp1, spec_path)
        print("[*] Running Generation 2 in temporary directory...")
        test2_path = run_generation(repo_root, tmp2, spec_path)

        content1 = test1_path.read_text(encoding="utf-8")
        content2 = test2_path.read_text(encoding="utf-8")

        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        norm1 = normalize_lines(lines1)
        norm2 = normalize_lines(lines2)

        if norm1 != norm2:
            diff = difflib.unified_diff(
                norm1,
                norm2,
                fromfile="generation_1",
                tofile="generation_2",
                lineterm="",
            )
            print("[-] Error: Generations differ beyond header timestamp:")
            for line in diff:
                print(line)
            return 1

        print("[+] Both generations produced identical code after timestamp normalization.")

        # Verify anchored and enabled cases
        for case in ANCHORED_CASES:
            if f"def {case}(self):" not in content1:
                print(f"[-] Error: Anchored case {case} missing from generated tests!")
                return 1
            print(f"[+] Verified anchored case present: {case}")

        for case in ALL_ENABLED_CASES:
            if f"def {case}(self):" not in content1:
                print(f"[-] Error: Enabled case {case} missing from generated tests!")
                return 1

        # Count test cases
        found_cases = [line.strip() for line in lines1 if line.strip().startswith("def test_")]
        if len(found_cases) != len(ALL_ENABLED_CASES):
            print(f"[-] Error: Expected {len(ALL_ENABLED_CASES)} cases, found {len(found_cases)}")
            return 1

        print(f"[+] All {len(ALL_ENABLED_CASES)} enabled test cases present and verified without omission.")
        print("[✓] Focused regeneration check passed successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
