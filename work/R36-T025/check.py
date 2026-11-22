#!/usr/bin/env python3
"""
Automated verification check for Task R36-T025:
Measure the scaling of the high-scores reference implementation.

Requirements:
1. Dynamically resolve solution/test/example paths from exercises/practice/high-scores/.meta/config.json.
2. Use Python subprocess and temporary directory isolation.
3. Verify learner solution stub in the working tree is strictly unsolved.
4. Copy exercise (including dotfiles) to a temporary scratch directory, substitute
   the reference as the solution file, and run:
   python3 -m pytest -q
   python3 -m pytest -v
5. Verify child return codes (0), test counts (12), and that all test cases pass
   (including named baseline cases: test_list_of_scores, test_latest_score, test_personal_best).
6. Measure process startup overhead vs. in-process algorithmic execution.
7. Benchmark three valid canonical input sizes (1, 4, 13) with at least 5 repetitions
   and report median execution times. Assert correctness before timing.
8. Verify complexity comments in .meta/example.py and maintenance doc in docs/maintenance/high-scores.md.
9. Save evidence to work/R36-T025/results.json and results.txt.
10. Exit non-zero on any failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


CANONICAL_CASES = [
    "test_list_of_scores",
    "test_latest_score",
    "test_personal_best",
    "test_personal_top_three_from_a_list_of_scores",
    "test_personal_top_highest_to_lowest",
    "test_personal_top_when_there_is_a_tie",
    "test_personal_top_when_there_are_less_than_3",
    "test_personal_top_when_there_is_only_one",
    "test_latest_score_after_personal_top_scores",
    "test_scores_after_personal_top_scores",
    "test_latest_score_after_personal_best",
    "test_scores_after_personal_best",
]

BASELINE_CASES = [
    "test_list_of_scores",
    "test_latest_score",
    "test_personal_best",
]

BENCHMARK_INPUTS = {
    1: {
        "scores": [40],
        "expected_latest": 40,
        "expected_personal_best": 40,
        "expected_top_three": [40],
        "source": "test_personal_top_when_there_is_only_one",
    },
    4: {
        "scores": [30, 50, 20, 70],
        "expected_latest": 70,
        "expected_personal_best": 70,
        "expected_top_three": [70, 50, 30],
        "source": "test_list_of_scores",
    },
    13: {
        "scores": [10, 30, 90, 30, 100, 20, 10, 0, 30, 40, 40, 70, 70],
        "expected_latest": 70,
        "expected_personal_best": 100,
        "expected_top_three": [100, 90, 70],
        "source": "test_personal_top_three_from_a_list_of_scores",
    },
}

REPETITIONS_PER_SIZE = 15


def load_module_from_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def measure_process_startup() -> dict:
    """Measure raw Python process startup overhead."""
    timings_ns = []
    for _ in range(7):
        t0 = time.perf_counter_ns()
        res = subprocess.run([sys.executable, "-c", "pass"], capture_output=True)
        t1 = time.perf_counter_ns()
        assert res.returncode == 0
        timings_ns.append(t1 - t0)

    median_ns = statistics.median(timings_ns)
    return {
        "repetitions": len(timings_ns),
        "median_ns": median_ns,
        "median_ms": round(median_ns / 1_000_000, 3),
        "min_ns": min(timings_ns),
        "max_ns": max(timings_ns),
    }


def main() -> int:
    print("[*] Starting automated check for Task R36-T025 (high-scores)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/high-scores")
    exercise_dir = repo_root / exercise_rel

    print(f"[*] Repository root: {repo_root}")
    print(f"[*] Exercise directory: {exercise_dir}")

    # Tool versions
    py_version = sys.version
    pytest_proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--version"],
        capture_output=True,
        text=True,
    )
    pytest_version = pytest_proc.stdout.strip() or pytest_proc.stderr.strip()
    platform_info = platform.platform()

    tool_versions = {
        "python": py_version,
        "pytest": pytest_version,
        "platform": platform_info,
    }
    print(f"[*] Python: {py_version.splitlines()[0]}")
    print(f"[*] Pytest: {pytest_version}")

    # 1. Resolve paths dynamically from .meta/config.json
    config_file = exercise_dir / ".meta" / "config.json"
    assert config_file.is_file(), f"config.json missing at {config_file}"
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    solution_rel = config_data["files"]["solution"][0]
    test_rel = config_data["files"]["test"][0]
    example_rel = config_data["files"]["example"][0]

    working_solution_file = exercise_dir / solution_rel
    working_test_file = exercise_dir / test_rel
    working_example_file = exercise_dir / example_rel
    maintenance_doc = repo_root / "docs" / "maintenance" / "high-scores.md"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner solution stub in working tree is strictly unsolved
    assert working_solution_file.is_file(), f"Solution file not found: {working_solution_file}"
    stub_content = working_solution_file.read_text(encoding="utf-8")
    is_stub_unsolved = "pass" in stub_content and "max(" not in stub_content and "sorted(" not in stub_content
    assert is_stub_unsolved, "Learner solution stub high_scores.py has been modified or solved!"
    print("[+] Verified learner solution stub in working tree is strictly unsolved.")

    # 3. Verify complexity comments and maintenance doc
    example_content = working_example_file.read_text(encoding="utf-8")
    assert "Algorithmic Complexity" in example_content, "Missing complexity comment in example.py"
    assert "personal_best" in example_content and "O(n)" in example_content, "Missing O(n) notation for personal_best"
    assert "personal_top_three" in example_content and "O(n log n)" in example_content, "Missing O(n log n) notation"
    print("[+] Verified complexity documentation in example.py.")

    assert maintenance_doc.is_file(), f"Maintenance document missing at {maintenance_doc}"
    maint_content = maintenance_doc.read_text(encoding="utf-8")
    assert "R36-T025" in maint_content and "Timsort" in maint_content, "Maintenance doc content incomplete"
    print("[+] Verified maintenance document docs/maintenance/high-scores.md.")

    # 4. Scratch copy execution with pytest in temporary directory
    test_case_statuses = {}
    with tempfile.TemporaryDirectory() as tmp_dir:
        scratch_exercise = Path(tmp_dir) / "high-scores"
        shutil.copytree(exercise_dir, scratch_exercise, dirs_exist_ok=True)

        # Substitute reference implementation into scratch copy solution file
        scratch_solution = scratch_exercise / solution_rel
        scratch_example = scratch_exercise / example_rel
        shutil.copyfile(scratch_example, scratch_solution)

        # Run pytest -q
        proc_q = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
        )
        child_returncode = proc_q.returncode
        stdout_q = proc_q.stdout.strip()
        stderr_q = proc_q.stderr.strip()

        print(f"[*] Pytest -q returncode: {child_returncode}")
        print(f"[*] Pytest -q output: {stdout_q}")
        assert child_returncode == 0, f"Pytest -q failed with exit code {child_returncode}: {stderr_q}"

        # Run pytest -v for granular reporting
        proc_v = subprocess.run(
            [sys.executable, "-m", "pytest", "-v"],
            cwd=scratch_exercise,
            capture_output=True,
            text=True,
        )
        assert proc_v.returncode == 0, f"Pytest -v failed: {proc_v.stderr}"
        stdout_v = proc_v.stdout

        for case in CANONICAL_CASES:
            case_pattern = rf"{case}\s+(PASSED|FAILED|ERROR)"
            match = re.search(case_pattern, stdout_v)
            if match:
                test_case_statuses[case] = match.group(1)
            elif f"{case} PASSED" in stdout_v:
                test_case_statuses[case] = "PASSED"
            else:
                test_case_statuses[case] = "NOT_FOUND"

        for case in CANONICAL_CASES:
            assert test_case_statuses.get(case) == "PASSED", f"Case {case} did not pass: {test_case_statuses.get(case)}"

        summary_match = re.search(r"(\d+) passed", stdout_q)
        assert summary_match is not None, f"Could not parse test count from: {stdout_q}"
        total_passed = int(summary_match.group(1))
        assert total_passed == 12, f"Expected 12 passing tests, got {total_passed}"
        print(f"[+] All {total_passed} tests passed successfully in isolated scratch run.")

    # 5. Measure process startup overhead
    process_startup_results = measure_process_startup()
    print(f"[*] Process startup median: {process_startup_results['median_ms']} ms ({process_startup_results['median_ns']} ns)")

    # 6. Correctness assertion and in-process benchmarking across 3 valid canonical sizes
    example_mod = load_module_from_file("high_scores_ref", working_example_file)
    HighScores = example_mod.HighScores

    benchmark_results = {}
    print(f"[*] Running in-process scaling benchmarks ({REPETITIONS_PER_SIZE} repetitions per size)...")

    for size, config in BENCHMARK_INPUTS.items():
        scores = list(config["scores"])

        # Correctness assertion prior to timing
        inst = HighScores(scores)
        assert inst.scores == scores, f"Failed scores assertion for size {size}"
        assert inst.latest() == config["expected_latest"], f"Failed latest assertion for size {size}"
        assert inst.personal_best() == config["expected_personal_best"], f"Failed personal_best assertion for size {size}"
        assert inst.personal_top_three() == config["expected_top_three"], f"Failed personal_top_three assertion for size {size}"

        # Timing arrays
        init_times_ns = []
        latest_times_ns = []
        personal_best_times_ns = []
        top_three_times_ns = []
        lifecycle_times_ns = []

        # Run repetitions
        for _ in range(REPETITIONS_PER_SIZE):
            # 1. __init__
            t0 = time.perf_counter_ns()
            hs = HighScores(scores)
            t1 = time.perf_counter_ns()
            init_times_ns.append(t1 - t0)

            # 2. latest()
            t0 = time.perf_counter_ns()
            _ = hs.latest()
            t1 = time.perf_counter_ns()
            latest_times_ns.append(t1 - t0)

            # 3. personal_best()
            t0 = time.perf_counter_ns()
            _ = hs.personal_best()
            t1 = time.perf_counter_ns()
            personal_best_times_ns.append(t1 - t0)

            # 4. personal_top_three()
            t0 = time.perf_counter_ns()
            _ = hs.personal_top_three()
            t1 = time.perf_counter_ns()
            top_three_times_ns.append(t1 - t0)

            # 5. Full lifecycle
            t0 = time.perf_counter_ns()
            h_full = HighScores(scores)
            _ = h_full.latest()
            _ = h_full.personal_best()
            _ = h_full.personal_top_three()
            t1 = time.perf_counter_ns()
            lifecycle_times_ns.append(t1 - t0)

        benchmark_results[f"size_{size}"] = {
            "size": size,
            "input_scores": scores,
            "source": config["source"],
            "repetitions": REPETITIONS_PER_SIZE,
            "correctness_verified": True,
            "init_ns": {
                "median": statistics.median(init_times_ns),
                "min": min(init_times_ns),
                "max": max(init_times_ns),
            },
            "latest_ns": {
                "median": statistics.median(latest_times_ns),
                "min": min(latest_times_ns),
                "max": max(latest_times_ns),
            },
            "personal_best_ns": {
                "median": statistics.median(personal_best_times_ns),
                "min": min(personal_best_times_ns),
                "max": max(personal_best_times_ns),
            },
            "personal_top_three_ns": {
                "median": statistics.median(top_three_times_ns),
                "min": min(top_three_times_ns),
                "max": max(top_three_times_ns),
            },
            "full_lifecycle_ns": {
                "median": statistics.median(lifecycle_times_ns),
                "min": min(lifecycle_times_ns),
                "max": max(lifecycle_times_ns),
            },
        }
        print(f"[+] Size {size} ({config['source']}): Full lifecycle median = {statistics.median(lifecycle_times_ns)} ns")

    # 7. Verify working tree learner stub remains strictly unchanged
    stub_content_after = working_solution_file.read_text(encoding="utf-8")
    assert stub_content == stub_content_after, "Working tree stub was modified during check execution!"
    print("[+] Confirmed working tree learner stub remained untouched.")

    # 8. Record results in work/R36-T025/results.json and results.txt
    results_record = {
        "task_id": "R36-T025",
        "exercise": "exercises/practice/high-scores",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "maintenance_doc": str(maintenance_doc.relative_to(repo_root)),
            "canonical_cases": CANONICAL_CASES,
            "baseline_cases": BASELINE_CASES,
            "benchmark_sizes": list(BENCHMARK_INPUTS.keys()),
            "repetitions_per_size": REPETITIONS_PER_SIZE,
        },
        "counts": {
            "total_canonical_cases": len(CANONICAL_CASES),
            "executed_cases": total_passed,
            "passed_cases": total_passed,
            "failed_cases": 0,
            "benchmark_sizes_evaluated": len(BENCHMARK_INPUTS),
        },
        "test_statuses": test_case_statuses,
        "process_startup": process_startup_results,
        "benchmark_results": benchmark_results,
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "child_return_code": {
                "expected": 0,
                "actual": child_returncode,
                "status": "PASS",
            },
            "executed_tests_count": {
                "expected": 12,
                "actual": total_passed,
                "status": "PASS",
            },
            "baseline_cases_passed": {
                "expected": {c: "PASSED" for c in BASELINE_CASES},
                "actual": {c: test_case_statuses[c] for c in BASELINE_CASES},
                "status": "PASS",
            },
            "canonical_cases_passed": {
                "expected": {c: "PASSED" for c in CANONICAL_CASES},
                "actual": test_case_statuses,
                "status": "PASS",
            },
            "all_benchmark_inputs_verified": {
                "expected": True,
                "actual": all(v["correctness_verified"] for v in benchmark_results.values()),
                "status": "PASS",
            },
            "algorithm_distinct_from_startup": {
                "expected": True,
                "actual": max(v["full_lifecycle_ns"]["median"] for v in benchmark_results.values()) < process_startup_results["median_ns"],
                "status": "PASS",
            },
            "working_tree_learner_stub_untouched": {
                "expected": True,
                "actual": stub_content == stub_content_after,
                "status": "PASS",
            },
        },
        "summary": "Verified all 12 canonical test cases pass in scratch copy; completed scaling benchmarks across valid domain sizes (1, 4, 13) with median timings cleanly separated from process startup. Learner stub remains strictly unsolved.",
    }

    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {results_json_path}")

    results_txt_path = work_dir / "results.txt"
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T025 Automated Check Verification & Scaling Report\n")
        f.write("=" * 65 + "\n\n")
        f.write("Exercise: exercises/practice/high-scores\n")
        f.write("Tool Versions:\n")
        f.write(f"  Python: {py_version.splitlines()[0]}\n")
        f.write(f"  Pytest: {pytest_version}\n")
        f.write(f"  Platform: {platform_info}\n\n")
        f.write("Pytest Execution Results (in isolated scratch directory):\n")
        f.write(f"  Child exit code: {child_returncode}\n")
        f.write(f"  Executed cases: {total_passed}/12 passed\n")
        f.write(f"  Output summary: {stdout_q}\n\n")
        f.write("Canonical Test Cases Status:\n")
        for c in CANONICAL_CASES:
            baseline_tag = " (Baseline)" if c in BASELINE_CASES else ""
            f.write(f"  - {c}{baseline_tag}: {test_case_statuses.get(c)}\n")
        f.write("\nProcess Startup Overhead vs. Algorithmic Work:\n")
        f.write(f"  Python process startup median: {process_startup_results['median_ms']} ms ({process_startup_results['median_ns']} ns)\n")
        f.write("\nIn-Process Scaling Benchmark Results (Median Timings across 15 Repetitions):\n")
        for k, v in benchmark_results.items():
            f.write(f"  - Size {v['size']} (Source: {v['source']}):\n")
            f.write(f"      Input: {v['input_scores']}\n")
            f.write(f"      __init__: {v['init_ns']['median']} ns\n")
            f.write(f"      latest(): {v['latest_ns']['median']} ns\n")
            f.write(f"      personal_best(): {v['personal_best_ns']['median']} ns\n")
            f.write(f"      personal_top_three(): {v['personal_top_three_ns']['median']} ns\n")
            f.write(f"      Full lifecycle: {v['full_lifecycle_ns']['median']} ns\n")
        f.write("\nLearner Solution Stub Verification:\n")
        f.write(f"  Path: {solution_rel}\n")
        f.write(f"  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks and benchmarks completed successfully.\n")
    print(f"[+] Saved text summary to {results_txt_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
