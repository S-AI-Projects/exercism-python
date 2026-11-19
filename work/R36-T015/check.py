#!/usr/bin/env python3
"""Run the bank-account reference tests in a disposable exercise copy."""

from __future__ import annotations

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
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXERCISE = ROOT / "exercises/practice/bank-account"
EVIDENCE = Path(os.environ.get("R36_EVIDENCE_DIR", Path(__file__).resolve().parent))
EVIDENCE.mkdir(parents=True, exist_ok=True)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    config = json.loads((EXERCISE / ".meta/config.json").read_text())
    solution_name = config["files"]["solution"][0]
    test_name = config["files"]["test"][0]
    example_name = config["files"]["example"][0]
    tests_toml = tomllib.loads((EXERCISE / ".meta/tests.toml").read_text())
    enabled_cases = sum(case.get("include") is not False for case in tests_toml.values())
    test_source = (EXERCISE / test_name).read_text()
    named_cases = (
        "test_newly_opened_account_has_zero_balance",
        "test_single_deposit",
        "test_multiple_deposits",
    )
    require(all(f"def {case}(" in test_source for case in named_cases), "a required named case is missing")

    versions = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "pytest": subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
    }
    (EVIDENCE / "versions.json").write_text(json.dumps(versions, indent=2) + "\n")

    with tempfile.TemporaryDirectory(prefix="bank-account-reference-") as temporary:
        scratch = Path(temporary) / "bank-account"
        shutil.copytree(EXERCISE, scratch, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        shutil.copy2(scratch / example_name, scratch / solution_name)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        (EVIDENCE / "pytest-output.txt").write_text(output)
        require(result.returncode == 0, f"pytest exited {result.returncode}:\n{output}")
        summaries = re.findall(r"(?m)(\d+) passed(?:,|\s|$)", output)
        require(bool(summaries), f"pytest did not report a passed test count:\n{output}")
        executed = int(summaries[-1])
        require(executed > 0, "pytest collected zero tests")
        require(executed == enabled_cases, f"expected {enabled_cases} enabled tests, got {executed}")

        sys.path.insert(0, str(scratch))
        from bank_account import BankAccount  # pylint: disable=import-outside-toplevel

        measurements = []
        batch_histories = 1000
        repetitions = 7
        for transaction_count in (1, 2, 5):
            history = (1,) * transaction_count
            expected_balance = sum(history)

            # Verify each representative history before collecting timings.
            account = BankAccount()
            account.open()
            for amount in history:
                account.deposit(amount)
            actual_balance = account.get_balance()
            require(actual_balance == expected_balance,
                    f"{transaction_count}-deposit history: expected {expected_balance}, got {actual_balance}")

            samples = []
            for _ in range(repetitions):
                accounts = []
                for _ in range(batch_histories):
                    account = BankAccount()
                    account.open()
                    accounts.append(account)
                started = time.perf_counter_ns()
                for account in accounts:
                    for amount in history:
                        account.deposit(amount)
                elapsed_ns = time.perf_counter_ns() - started
                samples.append(elapsed_ns / batch_histories)
                require(all(account.get_balance() == expected_balance for account in accounts),
                        f"post-timing correctness failed for {transaction_count}-deposit history")

            measurements.append({
                "deposit_transactions_per_history": transaction_count,
                "history_amounts": list(history),
                "expected_balance": expected_balance,
                "actual_balance_before_timing": actual_balance,
                "repetitions": repetitions,
                "batch_histories_per_repetition": batch_histories,
                "sample_ns_per_history": [round(sample, 1) for sample in samples],
                "median_ns_per_history": round(statistics.median(samples), 1),
            })

    expected_actual = {
        "input": {
            "exercise": "exercises/practice/bank-account",
            "solution_under_test": f"temporary copy/{solution_name}",
            "reference_source": f"temporary copy/{example_name}",
            "copy_includes_dotfiles": True,
            "command": "python3 -m pytest -q",
            "timed_input": "deposit 1-unit transactions; setup/open excluded from timer",
            "timing_method": "perf_counter_ns; 7 repetitions of batches of 1000 independent histories per size",
        },
        "expected": {"enabled_cases": enabled_cases, "minimum_cases": 1, "return_code": 0},
        "actual": {"executed_cases": executed, "return_code": result.returncode},
        "timings": measurements,
    }
    (EVIDENCE / "results.json").write_text(json.dumps(expected_actual, indent=2) + "\n")
    print(f"PASS: {executed} enabled pytest cases passed against the temporary reference copy.")
    print("Expected vs actual: " + json.dumps(expected_actual["expected"]) + " / " + json.dumps(expected_actual["actual"]))
    for measurement in measurements:
        print(f"{measurement['deposit_transactions_per_history']} deposits: median "
              f"{measurement['median_ns_per_history']} ns/history "
              f"({measurement['repetitions']} repetitions of {batch_histories} histories).")


if __name__ == "__main__":
    main()
