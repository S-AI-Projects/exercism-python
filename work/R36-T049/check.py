"""Exercise Camicia runner success, failure, empty-selection, and cleanup paths."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "exercises/practice/camicia"
TOOL = ROOT / "tools/course_checks/r36-t049.py"
FAILING_REFERENCE = ROOT / "work/R36-T049/failing_reference.py"
EXPECTED_CASES = 28
ANCHORS = ("test_two_cards_one_trick", "test_three_cards_one_trick", "test_four_cards_one_trick")


def hashes() -> dict[str, str]:
    config = json.loads((SOURCE / ".meta/config.json").read_text())
    return {
        name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
        for name in config["files"]["solution"]
    }


def run(label: str, reference: Path | None = None, filter_value: str | None = None) -> dict[str, object]:
    before = hashes()
    with tempfile.TemporaryDirectory(prefix=f"r36-t049-{label}-") as temp:
        parent = Path(temp)
        command = [sys.executable, str(TOOL), "--exercise-root", str(SOURCE), "--temp-parent", str(parent)]
        if reference:
            command.extend(("--reference-source", str(reference)))
        if filter_value is not None:
            command.extend(("--pytest-filter", filter_value))
        child = subprocess.run(command, capture_output=True, text=True, check=False)
        assert list(parent.iterdir()) == [], f"temporary exercise copy was not cleaned for {label}"
    after = hashes()
    assert before == after, f"learner solution changed during {label} run"
    result = json.loads(child.stdout)
    assert result["learner_hashes_before"] == result["learner_hashes_after"]
    assert result["temporary_copy_removed"] is True
    assert not Path(temp).exists(), f"temporary parent was not removed for {label}"
    result["task_checker_exit_status"] = child.returncode
    result["task_checker_hashes_before_after"] = [before, after]
    result["temporary_parent_removed"] = not Path(temp).exists()
    return result


def interrupted_run() -> dict[str, object]:
    before = hashes()
    module_spec = importlib.util.spec_from_file_location("r36_t049_runner", TOOL)
    module = importlib.util.module_from_spec(module_spec)
    assert module_spec and module_spec.loader
    module_spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="r36-t049-interrupt-") as temp:
        parent = Path(temp)
        interrupted = False
        try:
            with patch.object(module.subprocess, "run", side_effect=KeyboardInterrupt):
                module.run_isolated(SOURCE, temp_parent=parent)
        except KeyboardInterrupt:
            interrupted = True
        assert interrupted, "simulated interrupt did not propagate"
        assert list(parent.iterdir()) == [], "scratch copy leaked after interruption"
    after = hashes()
    assert before == after, "learner solution changed during interrupted run"
    return {
        "expected": "KeyboardInterrupt propagates and scratch copy is removed",
        "actual": "KeyboardInterrupt propagated; no scratch children remained",
        "learner_hashes_before_after": [before, after],
        "temporary_parent_removed": not Path(temp).exists(),
    }


def summarize_output(result: dict[str, object]) -> None:
    output = str(result.pop("output", ""))
    lines = output.splitlines()
    excerpt = lines[:18]
    if len(lines) > 24:
        excerpt.extend(["... output excerpt omitted ..."] + lines[-6:])
    result["output_bytes"] = len(output.encode())
    result["output_sha256"] = hashlib.sha256(output.encode()).hexdigest()
    result["output_excerpt"] = "\n".join(excerpt)


def main() -> None:
    tests = SOURCE / json.loads((SOURCE / ".meta/config.json").read_text())["files"]["test"][0]
    test_source = tests.read_text()
    for anchor in ANCHORS:
        assert f"def {anchor}(" in test_source, f"missing anchor {anchor}"

    success = run("reference")
    assert success["task_checker_exit_status"] == 0
    assert success["executed_cases"] == EXPECTED_CASES
    assert success["child_exit_status"] == 0

    failing = run("failing-reference", FAILING_REFERENCE)
    assert failing["task_checker_exit_status"] != 0
    assert failing["child_exit_status"] != 0
    assert failing["executed_cases"] == EXPECTED_CASES

    empty = run("empty-selection", filter_value="r36_t049_no_such_test_case")
    assert empty["task_checker_exit_status"] != 0
    assert empty["child_exit_status"] != 0
    assert empty["executed_cases"] == 0
    assert empty["failure_reason"] == "pytest selected zero tests"
    interrupted = interrupted_run()

    for run_result in (success, failing, empty):
        summarize_output(run_result)

    results = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "anchors": list(ANCHORS),
        "expected_real_case_count": EXPECTED_CASES,
        "real_reference_run": success,
        "failing_reference_run": failing,
        "empty_selection_run": empty,
        "interrupted_run": interrupted,
        "all_runs_preserved_learner_hashes": True,
        "all_temporary_directories_removed": True,
    }
    (ROOT / "work/R36-T049/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print("PASS: runner success, failing-reference propagation, zero-test rejection, and cleanup verified.")


if __name__ == "__main__":
    main()
