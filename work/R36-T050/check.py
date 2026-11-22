"""Verify Dominoes contract examples and all tests against the reference."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "exercises/practice/dominoes"
EXPECTED_CASES = 13
CASES = {
    "test_empty_input_empty_output": ([], "valid"),
    "test_singleton_input_singleton_output": ([(1, 1)], "valid"),
    "test_singleton_that_can_t_be_chained": ([(1, 2)], "none"),
}
EXPECTED_REFERENCE_OUTPUTS = ("[]", "[(1, 1)]", "None")


def selected_cases(test_source: str) -> list[tuple[str, list[tuple[int, int]], str]]:
    tree = ast.parse(test_source)
    class_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DominoesTest")
    found = []
    for name, (expected_input, expected_kind) in CASES.items():
        method = next(node for node in class_node.body if isinstance(node, ast.FunctionDef) and node.name == name)
        input_value = None
        assertion = None
        for node in ast.walk(method):
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "input_dominoes" for target in node.targets):
                input_value = ast.literal_eval(node.value)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("assert_correct_chain", "refute_correct_chain"):
                assertion = node.func.attr
        expected_assertion = "assert_correct_chain" if expected_kind == "valid" else "refute_correct_chain"
        assert input_value == expected_input, f"{name}: input changed: {input_value!r}"
        assert assertion == expected_assertion, f"{name}: expected {expected_assertion}, got {assertion}"
        found.append((name, input_value, expected_kind))
    return found


def main() -> None:
    cfg = json.loads((SOURCE / ".meta/config.json").read_text())
    learner = SOURCE / cfg["files"]["solution"][0]
    before = hashlib.sha256(learner.read_bytes()).hexdigest()
    test_source = (SOURCE / cfg["files"]["test"][0]).read_text()
    cases = selected_cases(test_source)

    with tempfile.TemporaryDirectory(prefix="r36-t050-") as temp:
        exercise = Path(temp) / "dominoes"
        shutil.copytree(SOURCE, exercise)
        scratch_cfg = json.loads((exercise / ".meta/config.json").read_text())
        solution = exercise / scratch_cfg["files"]["solution"][0]
        reference = exercise / scratch_cfg["files"]["example"][0]
        test_file = exercise / scratch_cfg["files"]["test"][0]
        shutil.copy2(reference, solution)

        test_args = [sys.executable, "-m", "pytest", "-q", str(test_file)]
        tests = subprocess.run(test_args, cwd=exercise, capture_output=True, text=True, check=False)
        output = tests.stdout + tests.stderr
        match = re.search(r"(\d+) passed(?:,|\s)", output)
        actual_count = int(match.group(1)) if match else 0
        assert tests.returncode == 0, f"reference tests exited {tests.returncode}:\n{output}"
        assert actual_count == EXPECTED_CASES, f"expected {EXPECTED_CASES}, got {actual_count}:\n{output}"

        python_code = "from dominoes import can_chain\n" + "\n".join(
            f"print(repr(can_chain({dominoes!r})))" for _, dominoes, _ in cases
        )
        examples = subprocess.run([sys.executable, "-c", python_code], cwd=exercise, capture_output=True, text=True, check=False)
        assert examples.returncode == 0, examples.stderr
        actual_outputs = tuple(examples.stdout.splitlines())
        assert actual_outputs == EXPECTED_REFERENCE_OUTPUTS, f"expected {EXPECTED_REFERENCE_OUTPUTS}, got {actual_outputs}"

    after = hashlib.sha256(learner.read_bytes()).hexdigest()
    assert before == after, "learner starter changed"
    results = {
        "tool_versions": {
            "python": sys.version.split()[0],
            "pytest": subprocess.run([sys.executable, "-m", "pytest", "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        },
        "test_command": test_args,
        "expected_test_count": EXPECTED_CASES,
        "actual_test_count": actual_count,
        "test_exit_status": tests.returncode,
        "test_output": output.strip(),
        "selected_cases": [
            {"test": name, "input": dominoes, "contract_outcome": kind, "expected_reference_repr": expected, "actual_reference_repr": actual}
            for (name, dominoes, kind), expected, actual in zip(cases, EXPECTED_REFERENCE_OUTPUTS, actual_outputs)
        ],
        "expected_example_outputs": EXPECTED_REFERENCE_OUTPUTS,
        "actual_example_outputs": actual_outputs,
        "example_exit_status": examples.returncode,
        "learner_solution_sha256_before_after": [before, after],
    }
    (ROOT / "work/R36-T050/results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS: selected examples match; reference passes {actual_count}/{EXPECTED_CASES} cases.")


if __name__ == "__main__":
    main()
