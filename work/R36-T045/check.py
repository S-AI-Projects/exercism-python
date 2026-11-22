"""Test and measure the maintained Anagram reference on increasing valid inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "exercises/practice/anagram"
EXPECTED_TESTS = 18
REPETITIONS = 7
SIZES = ((8, 100), (32, 300), (128, 900))
ANCHORS = ("test_no_matches", "test_detects_two_anagrams", "test_does_not_detect_anagram_subsets")


def benchmark(function, length: int, candidate_count: int) -> dict[str, object]:
    word = "a" * (length - 1) + "b"
    candidates: list[str] = []
    expected: list[str] = []
    for index in range(candidate_count):
        if index % 2 == 0:
            rotation = index % (length - 1) + 1
            candidate = word[rotation:] + word[:rotation]
            expected.append(candidate)
        else:
            candidate = "a" * (length - 1) + "c"
        candidates.append(candidate)

    samples_ns = []
    actual = None
    for _ in range(REPETITIONS):
        started = time.perf_counter_ns()
        actual = function(word, candidates)
        samples_ns.append(time.perf_counter_ns() - started)
    assert actual == expected, f"size {length}, {candidate_count} candidates: wrong result"
    return {
        "input": {"target": word, "target_length": len(word), "candidate_count": len(candidates), "expected_match_count": len(expected)},
        "expected_matches": expected,
        "actual_matches": actual,
        "repetitions": REPETITIONS,
        "samples_ms": [round(value / 1_000_000, 6) for value in samples_ns],
        "median_ms": round(statistics.median(samples_ns) / 1_000_000, 6),
    }


def main() -> None:
    cfg = json.loads((SOURCE / ".meta/config.json").read_text())
    learner_solution = SOURCE / cfg["files"]["solution"][0]
    before = hashlib.sha256(learner_solution.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="r36-t045-") as temp:
        exercise = Path(temp) / "anagram"
        shutil.copytree(SOURCE, exercise)
        scratch_cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / scratch_cfg["files"]["solution"][0]
        test_file = exercise / scratch_cfg["files"]["test"][0]
        reference = exercise / scratch_cfg["files"]["example"][0]
        tests = test_file.read_text()
        for name in ANCHORS:
            assert f"def {name}(" in tests, f"missing anchor case {name}"
        shutil.copy2(reference, solution)

        args = [sys.executable, "-m", "pytest", "-q"]
        run = subprocess.run(args, cwd=exercise, capture_output=True, text=True, check=False)
        output = run.stdout + run.stderr
        match = re.search(r"(\d+) passed(?:,|\s)", output)
        actual_count = int(match.group(1)) if match else 0
        assert run.returncode == 0, f"reference tests failed ({run.returncode}):\n{output}"
        assert actual_count == EXPECTED_TESTS, f"expected {EXPECTED_TESTS}, got {actual_count}:\n{output}"

        module_spec = importlib.util.spec_from_file_location("anagram_reference", reference)
        module = importlib.util.module_from_spec(module_spec)
        assert module_spec and module_spec.loader
        module_spec.loader.exec_module(module)
        measurements = [benchmark(module.find_anagrams, length, count) for length, count in SIZES]

    after = hashlib.sha256(learner_solution.read_bytes()).hexdigest()
    assert before == after, "working learner solution changed"
    results = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "test_command": [sys.executable, "-m", "pytest", "-q"],
        "expected_test_count": EXPECTED_TESTS,
        "actual_test_count": actual_count,
        "test_exit_status": run.returncode,
        "test_output": output.strip(),
        "anchors": list(ANCHORS),
        "benchmark_method": f"{REPETITIONS} perf_counter_ns repetitions; median per input; no timing threshold",
        "measurements": measurements,
        "learner_solution_sha256_before_after": [before, after],
    }
    (ROOT / "work/R36-T045/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: {actual_count}/{EXPECTED_TESTS} reference tests; measured three sizes, {REPETITIONS} repetitions each.")


if __name__ == "__main__":
    main()
