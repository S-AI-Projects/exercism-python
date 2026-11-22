#!/usr/bin/env python3
"""
Automated verification check for Task R36-T026:
Compare the reference technique in roman-numerals with an independent alternative.

Requirements:
1. Dynamically resolve solution/test/example paths from exercises/practice/roman-numerals/.meta/config.json.
2. Use Python subprocess and temporary scratch directory isolation.
3. Verify learner solution stub in the working tree is strictly unsolved ('pass').
4. Verify approach selection documentation in .docs/hints.md exists with worked example (27 -> XXVII).
5. Implement independent Positional Table Lookup approach in scratch environment.
6. Run pytest -q and pytest -v on both implementations in isolated scratch copies:
   - Approach 1: Maintained Reference (Greedy Subtraction Loop)
   - Approach 2: Alternative (Positional Table Lookup)
7. Verify all 27 canonical test cases pass on BOTH approaches (including named anchor cases:
   test_1_is_i, test_2_is_ii, test_3_is_iii).
8. Assert 100% output parity between both approaches across all 27 canonical cases.
9. Save evidence to work/R36-T026/results.json and results.txt.
10. Exit non-zero on any failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CANONICAL_CASES = [
    "test_1_is_i",
    "test_2_is_ii",
    "test_3_is_iii",
    "test_4_is_iv",
    "test_5_is_v",
    "test_6_is_vi",
    "test_9_is_ix",
    "test_16_is_xvi",
    "test_27_is_xxvii",
    "test_48_is_xlviii",
    "test_49_is_xlix",
    "test_59_is_lix",
    "test_66_is_lxvi",
    "test_93_is_xciii",
    "test_141_is_cxli",
    "test_163_is_clxiii",
    "test_166_is_clxvi",
    "test_402_is_cdii",
    "test_575_is_dlxxv",
    "test_666_is_dclxvi",
    "test_911_is_cmxi",
    "test_1024_is_mxxiv",
    "test_1666_is_mdclxvi",
    "test_3000_is_mmm",
    "test_3001_is_mmmi",
    "test_3888_is_mmmdccclxxxviii",
    "test_3999_is_mmmcmxcix",
]

NAMED_ANCHOR_CASES = [
    "test_1_is_i",
    "test_2_is_ii",
    "test_3_is_iii",
]

CANONICAL_TEST_INPUTS = {
    "test_1_is_i": 1,
    "test_2_is_ii": 2,
    "test_3_is_iii": 3,
    "test_4_is_iv": 4,
    "test_5_is_v": 5,
    "test_6_is_vi": 6,
    "test_9_is_ix": 9,
    "test_16_is_xvi": 16,
    "test_27_is_xxvii": 27,
    "test_48_is_xlviii": 48,
    "test_49_is_xlix": 49,
    "test_59_is_lix": 59,
    "test_66_is_lxvi": 66,
    "test_93_is_xciii": 93,
    "test_141_is_cxli": 141,
    "test_163_is_clxiii": 163,
    "test_166_is_clxvi": 166,
    "test_402_is_cdii": 402,
    "test_575_is_dlxxv": 575,
    "test_666_is_dclxvi": 666,
    "test_911_is_cmxi": 911,
    "test_1024_is_mxxiv": 1024,
    "test_1666_is_mdclxvi": 1666,
    "test_3000_is_mmm": 3000,
    "test_3001_is_mmmi": 3001,
    "test_3888_is_mmmdccclxxxviii": 3888,
    "test_3999_is_mmmcmxcix": 3999,
}

ALTERNATIVE_SOLUTION_SOURCE = '''\
# Independent alternative approach: Positional Table Lookup (Place-Value Decomposition)
THOUSANDS = ("", "M", "MM", "MMM")
HUNDREDS = ("", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM")
TENS = ("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC")
ONES = ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")


def roman(number):
    thousands = THOUSANDS[number // 1000]
    hundreds = HUNDREDS[(number % 1000) // 100]
    tens = TENS[(number % 100) // 10]
    ones = ONES[number % 10]
    return thousands + hundreds + tens + ones
'''


def load_module_from_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_pytest_in_dir(exercise_dir: Path) -> tuple[int, str, dict[str, str], int]:
    """Run pytest -q and pytest -v in directory, returning status, summary, and test map."""
    proc_q = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=exercise_dir,
        capture_output=True,
        text=True,
    )
    assert proc_q.returncode == 0, f"Pytest -q failed: {proc_q.stderr}"
    stdout_q = proc_q.stdout.strip()

    proc_v = subprocess.run(
        [sys.executable, "-m", "pytest", "-v"],
        cwd=exercise_dir,
        capture_output=True,
        text=True,
    )
    assert proc_v.returncode == 0, f"Pytest -v failed: {proc_v.stderr}"
    stdout_v = proc_v.stdout

    test_statuses = {}
    for case in CANONICAL_CASES:
        pattern = rf"{case}\s+(PASSED|FAILED|ERROR)"
        match = re.search(pattern, stdout_v)
        if match:
            test_statuses[case] = match.group(1)
        elif f"{case} PASSED" in stdout_v:
            test_statuses[case] = "PASSED"
        else:
            test_statuses[case] = "NOT_FOUND"

    match_count = re.search(r"(\d+) passed", stdout_q)
    assert match_count is not None, f"Could not parse test count from: {stdout_q}"
    total_passed = int(match_count.group(1))

    return proc_q.returncode, stdout_q, test_statuses, total_passed


def main() -> int:
    print("[*] Starting automated check for Task R36-T026 (roman-numerals)...")

    script_path = Path(__file__).resolve()
    work_dir = script_path.parent
    repo_root = work_dir.parent.parent
    exercise_rel = Path("exercises/practice/roman-numerals")
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
    hints_file = exercise_dir / ".docs" / "hints.md"

    print(f"[*] Resolved solution file: {solution_rel}")
    print(f"[*] Resolved test file: {test_rel}")
    print(f"[*] Resolved example file: {example_rel}")

    # 2. Verify learner stub in working tree is strictly unsolved
    assert working_solution_file.is_file(), f"Solution file missing at {working_solution_file}"
    stub_content = working_solution_file.read_text(encoding="utf-8")
    is_stub_unsolved = "pass" in stub_content and "return" not in stub_content and "for" not in stub_content
    assert is_stub_unsolved, "Working tree learner stub roman_numerals.py has been modified or solved!"
    print("[+] Verified learner solution stub in working tree is strictly unsolved.")

    # 3. Verify hints.md documentation
    assert hints_file.is_file(), f"hints.md missing at {hints_file}"
    hints_text = hints_file.read_text(encoding="utf-8")
    assert "Approach Selection" in hints_text, "Missing Approach Selection section in hints.md"
    assert "Greedy Subtraction" in hints_text and "Positional Table Lookup" in hints_text, "Missing approach names in hints.md"
    assert "27" in hints_text and "XXVII" in hints_text, "Missing worked example for 27 -> XXVII in hints.md"
    print("[+] Verified hints.md contains approach comparison and worked example.")

    # 4. Scratch copy test execution: Approach 1 (Maintained Reference: Greedy Subtraction)
    with tempfile.TemporaryDirectory() as tmp_dir_ref:
        scratch_ref = Path(tmp_dir_ref) / "roman-numerals"
        shutil.copytree(exercise_dir, scratch_ref, dirs_exist_ok=True)
        shutil.copyfile(scratch_ref / example_rel, scratch_ref / solution_rel)

        code_ref, summary_ref, statuses_ref, count_ref = run_pytest_in_dir(scratch_ref)
        print(f"[*] Approach 1 (Greedy Subtraction) pytest: {count_ref}/27 passed, exit code {code_ref}")
        assert code_ref == 0 and count_ref == 27, "Reference approach failed unit tests!"
        for anc in NAMED_ANCHOR_CASES:
            assert statuses_ref.get(anc) == "PASSED", f"Anchor case {anc} failed on Reference!"

    # 5. Scratch copy test execution: Approach 2 (Alternative: Positional Table Lookup)
    with tempfile.TemporaryDirectory() as tmp_dir_alt:
        scratch_alt = Path(tmp_dir_alt) / "roman-numerals"
        shutil.copytree(exercise_dir, scratch_alt, dirs_exist_ok=True)
        (scratch_alt / solution_rel).write_text(ALTERNATIVE_SOLUTION_SOURCE, encoding="utf-8")

        code_alt, summary_alt, statuses_alt, count_alt = run_pytest_in_dir(scratch_alt)
        print(f"[*] Approach 2 (Positional Table Lookup) pytest: {count_alt}/27 passed, exit code {code_alt}")
        assert code_alt == 0 and count_alt == 27, "Alternative approach failed unit tests!"
        for anc in NAMED_ANCHOR_CASES:
            assert statuses_alt.get(anc) == "PASSED", f"Anchor case {anc} failed on Alternative!"

    # 6. Direct output parity verification across all 27 canonical cases
    ref_mod = load_module_from_file("roman_reference", working_example_file)
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as alt_tmp:
        alt_tmp.write(ALTERNATIVE_SOLUTION_SOURCE)
        alt_tmp_path = Path(alt_tmp.name)

    alt_mod = load_module_from_file("roman_alternative", alt_tmp_path)
    alt_tmp_path.unlink()

    parity_results = {}
    for case_name, input_val in CANONICAL_TEST_INPUTS.items():
        ref_out = ref_mod.roman(input_val)
        alt_out = alt_mod.roman(input_val)
        assert ref_out == alt_out, f"Output mismatch for {case_name} (input {input_val}): ref='{ref_out}', alt='{alt_out}'"
        parity_results[case_name] = {
            "input": input_val,
            "output": ref_out,
            "match": True,
        }
    print("[+] Verified 100% output parity between both approaches across all 27 canonical cases.")

    # 7. Verify working tree learner stub remains strictly unchanged
    stub_content_after = working_solution_file.read_text(encoding="utf-8")
    assert stub_content == stub_content_after, "Working tree stub was modified during check execution!"
    print("[+] Confirmed working tree learner stub remained untouched.")

    # 8. Record results in work/R36-T026/results.json and results.txt
    results_record = {
        "task_id": "R36-T026",
        "exercise": "exercises/practice/roman-numerals",
        "tool_versions": tool_versions,
        "inputs": {
            "config_path": str(config_file.relative_to(repo_root)),
            "solution_file": solution_rel,
            "test_file": test_rel,
            "example_file": example_rel,
            "hints_file": str(hints_file.relative_to(repo_root)),
            "canonical_cases": CANONICAL_CASES,
            "named_anchor_cases": NAMED_ANCHOR_CASES,
        },
        "approaches_compared": {
            "approach_1_reference": {
                "name": "Greedy Subtraction Loop (loop-over-romans)",
                "data_structure": "Descending list of 13 Arabic-Roman threshold tuples",
                "control_flow": "Outer for-loop over 13 thresholds with inner while-subtraction loop",
                "time_complexity": "O(digits), variable subtractions (1 to 15 steps)",
                "space_complexity": "O(1) auxiliary, 13 tuples static storage",
                "test_results": {
                    "exit_code": code_ref,
                    "passed": count_ref,
                    "total": len(CANONICAL_CASES),
                },
            },
            "approach_2_alternative": {
                "name": "Positional Table Lookup (table-lookup)",
                "data_structure": "Four decimal place lookup tuples (Thousands, Hundreds, Tens, Ones)",
                "control_flow": "Zero loops; 4 integer divisions/modulos and 4 direct table index lookups",
                "time_complexity": "Deterministic O(1) time",
                "space_complexity": "O(1) auxiliary, 34 precomputed strings static storage",
                "test_results": {
                    "exit_code": code_alt,
                    "passed": count_alt,
                    "total": len(CANONICAL_CASES),
                },
            },
        },
        "counts": {
            "total_canonical_cases": len(CANONICAL_CASES),
            "reference_passed": count_ref,
            "alternative_passed": count_alt,
            "parity_matches": len(parity_results),
        },
        "named_anchors_status": {
            "reference": {anc: statuses_ref[anc] for anc in NAMED_ANCHOR_CASES},
            "alternative": {anc: statuses_alt[anc] for anc in NAMED_ANCHOR_CASES},
        },
        "parity_verification": parity_results,
        "expected_vs_actual": {
            "learner_stub_unsolved": {
                "expected": True,
                "actual": is_stub_unsolved,
                "status": "PASS",
            },
            "reference_exit_code": {
                "expected": 0,
                "actual": code_ref,
                "status": "PASS",
            },
            "reference_test_count": {
                "expected": 27,
                "actual": count_ref,
                "status": "PASS",
            },
            "alternative_exit_code": {
                "expected": 0,
                "actual": code_alt,
                "status": "PASS",
            },
            "alternative_test_count": {
                "expected": 27,
                "actual": count_alt,
                "status": "PASS",
            },
            "all_anchors_passed_both": {
                "expected": True,
                "actual": all(statuses_ref[a] == "PASSED" and statuses_alt[a] == "PASSED" for a in NAMED_ANCHOR_CASES),
                "status": "PASS",
            },
            "output_parity_100_percent": {
                "expected": True,
                "actual": all(v["match"] for v in parity_results.values()),
                "status": "PASS",
            },
            "working_tree_learner_stub_untouched": {
                "expected": True,
                "actual": stub_content == stub_content_after,
                "status": "PASS",
            },
        },
        "summary": "Both Greedy Subtraction (reference) and Positional Table Lookup (alternative) pass all 27 canonical test cases with 100% output parity. Learner stub remains strictly unsolved.",
    }

    results_json_path = work_dir / "results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(results_record, f, indent=2)
    print(f"[+] Saved structured results to {results_json_path}")

    results_txt_path = work_dir / "results.txt"
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("Task R36-T026 Automated Check & Approach Comparison Report\n")
        f.write("=" * 65 + "\n\n")
        f.write("Exercise: exercises/practice/roman-numerals\n")
        f.write("Tool Versions:\n")
        f.write(f"  Python: {py_version.splitlines()[0]}\n")
        f.write(f"  Pytest: {pytest_version}\n")
        f.write(f"  Platform: {platform_info}\n\n")
        f.write("Approaches Evaluated:\n")
        f.write("  1. Maintained Reference: Greedy Subtraction Loop (loop-over-romans)\n")
        f.write(f"     - Pytest exit code: {code_ref}\n")
        f.write(f"     - Executed cases: {count_ref}/27 passed\n")
        f.write("  2. Alternative: Positional Table Lookup (table-lookup)\n")
        f.write(f"     - Pytest exit code: {code_alt}\n")
        f.write(f"     - Executed cases: {count_alt}/27 passed\n\n")
        f.write("Named Anchor Cases Status:\n")
        for anc in NAMED_ANCHOR_CASES:
            f.write(f"  - {anc}: Reference={statuses_ref.get(anc)}, Alternative={statuses_alt.get(anc)}\n")
        f.write(f"\nOutput Parity Across All 27 Cases: 100% IDENTICAL MATCH\n")
        for case, data in parity_results.items():
            f.write(f"  - {case} ({data['input']}): '{data['output']}' [MATCH]\n")
        f.write("\nLearner Solution Stub Verification:\n")
        f.write(f"  Path: {solution_rel}\n")
        f.write("  Unsolved stub preserved: PASS\n")
        f.write("\nAll checks and approach comparisons passed successfully.\n")
    print(f"[+] Saved text summary to {results_txt_path}")

    print("[✓] ALL CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
