# BankAccount cost study

## Input model and scope

For this exercise, input size is the number of deposit transactions in one account history. The specification allows accounts to receive an arbitrary sequence of operations, so history length is not fixed by the test corpus. The measurements use valid histories of 1, 2, and 5 deposits of 1 unit each. The setup (`BankAccount()` and `open()`) happens before timing; the timed work applies those deposits to already-open accounts. The check verifies the balance before timing and again after each timed batch.

## Operation counts

The named canonical cases exercise these histories:

| Test case | Deposits in history | Account calls |
| --- | ---: | --- |
| `test_newly_opened_account_has_zero_balance` | 0 | `open`, `get_balance` |
| `test_single_deposit` | 1 | `open`, `deposit`, `get_balance` |
| `test_multiple_deposits` | 2 | `open`, `deposit`, `deposit`, `get_balance` |

Across all 16 enabled canonical cases, the longest history contains 7 method calls (`test_can_do_multiple_operations_sequentially`); this describes the test corpus, not a limit on valid histories. For an n-transaction history with bounded-size integer balances, algorithm work is Θ(n): each deposit performs a fixed number of checks and attribute accesses plus one lock acquire/release. Lock wait can depend on contention. The account stores no transaction history, so its auxiliary state is O(1), excluding the bit length of the balance. Python integer arithmetic can take time proportional to the integer's digit count as balances grow.

## Measurements

The check used Python 3.13.5, pytest 9.2.0, and macOS 27.2.1 on arm64. For each input size, it measured seven repetitions of 1,000 independent account histories and reports the median nanoseconds per history. Account creation and opening were outside the timed region; iteration, method dispatch, lock use, and deposit arithmetic were included. Correctness was asserted before timing and after each batch.

| Deposits per history | Amounts | Expected/actual balance | Repetitions × histories | Median ns/history |
| ---: | --- | ---: | ---: | ---: |
| 1 | `[1]` | 1 / 1 | 7 × 1,000 | 96.6 |
| 2 | `[1, 1]` | 2 / 2 | 7 × 1,000 | 171.6 |
| 5 | `[1, 1, 1, 1, 1]` | 5 / 5 | 7 × 1,000 | 413.0 |

## Cost conclusion and limits

The measurements support a per-transaction constant-work model for these small balances; they are illustrative microbenchmarks, not a proof of asymptotic behavior or a speedup claim. Batch iteration is included and lock contention is not modeled. The pytest run is a separate correctness check: its process startup, imports, collection, and framework overhead are excluded from operation timings. There is no separate compilation phase in this Python run. `work/R36-T015/check.py` copies the exercise including dotfiles, substitutes the reference only in that copy, verifies all enabled cases, and records inputs, balances, medians, expected/actual test counts, and tool versions.
