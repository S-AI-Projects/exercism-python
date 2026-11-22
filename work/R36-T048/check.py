"""Validate Food Chain metadata, negative fixtures, and reference tests."""

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
SOURCE = ROOT / "exercises/practice/food-chain"
TOOL = ROOT / "tools/course_checks/r36-t048.py"
EXPECTED_CASES = 10
ANCHORS = ("test_fly", "test_spider", "test_bird")


def validate(config: Path, exercise: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--config", str(config), "--exercise-root", str(exercise)],
        capture_output=True,
        text=True,
        check=False,
    )


def create_fixture(root: Path) -> Path:
    (root / ".meta").mkdir(parents=True)
    (root / "solution.py").write_text("\n")
    (root / "tests.py").write_text("\n")
    (root / ".meta/example.py").write_text("\n")
    config = {
        "files": {
            "solution": ["solution.py"],
            "test": ["tests.py"],
            "example": [".meta/example.py"],
        }
    }
    config_path = root / ".meta/config.json"
    config_path.write_text(json.dumps(config))
    return config_path


def negative_fixtures(temp_root: Path) -> list[dict[str, object]]:
    cases = []
    definitions = (
        ("missing-reference", ".meta/example.py", "missing_reference.py", "missing file"),
        ("missing-test", "tests.py", "missing_test.py", "missing file"),
        ("outside-exercise", ".meta/example.py", "../outside.py", "parent traversal"),
    )
    for name, role, replacement, expected_reason in definitions:
        root = temp_root / name
        config_path = create_fixture(root)
        if name == "outside-exercise":
            (root.parent / "outside.py").write_text("\n")
        config = json.loads(config_path.read_text())
        role_name = "example" if name != "missing-test" else "test"
        config["files"][role_name] = [replacement]
        config_path.write_text(json.dumps(config))
        result = validate(config_path, root)
        diagnostic = result.stderr.strip()
        assert result.returncode != 0, f"{name} fixture unexpectedly passed"
        assert expected_reason in diagnostic, f"{name}: wrong rejection: {diagnostic}"
        cases.append({"name": name, "expected": f"reject with {expected_reason}", "actual_exit_status": result.returncode, "actual_diagnostic": diagnostic})
    return cases


def main() -> None:
    config_path = SOURCE / ".meta/config.json"
    metadata = validate(config_path, SOURCE)
    assert metadata.returncode == 0, metadata.stderr
    role_map = json.loads(metadata.stdout)
    expected_names = {
        "solution": ["food_chain.py"],
        "test": ["food_chain_test.py"],
        "example": [".meta/example.py"],
    }
    for role, names in expected_names.items():
        actual = [Path(path).relative_to(SOURCE).as_posix() for path in role_map[role]]
        assert actual == names, f"{role}: expected {names}, got {actual}"

    learner = SOURCE / expected_names["solution"][0]
    before = hashlib.sha256(learner.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="r36-t048-") as temp:
        negative = negative_fixtures(Path(temp))
        exercise = Path(temp) / "food-chain-reference"
        shutil.copytree(SOURCE, exercise)
        cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / cfg["files"]["solution"][0]
        reference = exercise / cfg["files"]["example"][0]
        test_file = exercise / cfg["files"]["test"][0]
        test_source = test_file.read_text()
        for anchor in ANCHORS:
            assert f"def {anchor}(" in test_source, f"missing anchor {anchor}"
        shutil.copy2(reference, solution)
        args = [sys.executable, "-m", "pytest", "-q"]
        tests = subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)
        output = tests.stdout + tests.stderr
        count_match = re.search(r"(\d+) passed(?:,|\s)", output)
        count = int(count_match.group(1)) if count_match else 0
        assert tests.returncode == 0, f"reference tests exited {tests.returncode}:\n{output}"
        assert count == EXPECTED_CASES, f"expected {EXPECTED_CASES}, got {count}:\n{output}"

    after = hashlib.sha256(learner.read_bytes()).hexdigest()
    assert before == after, "learner solution changed"
    result = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "metadata_validation_exit_status": metadata.returncode,
        "resolved_paths": {role: [Path(path).relative_to(SOURCE).as_posix() for path in paths] for role, paths in role_map.items()},
        "editor_role_declared": "editor" in role_map,
        "negative_fixtures": negative,
        "test_command": args,
        "anchors": list(ANCHORS),
        "expected_cases": EXPECTED_CASES,
        "actual_cases": count,
        "test_exit_status": tests.returncode,
        "test_output": output.strip(),
        "learner_solution_sha256_before_after": [before, after],
    }
    (ROOT / "work/R36-T048/results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: metadata resolves; 3 invalid fixtures rejected; reference passes {count}/{EXPECTED_CASES} tests.")


if __name__ == "__main__":
    main()
