# Poker Exercise Maintenance & Test Isolation Guide

## 1. Overview

The `poker` practice exercise (`exercises/practice/poker`) requires learners to determine the winning poker hand(s) from a list of 5-card hands according to standard poker rules.

To maintain exercise integrity:
- The learner starter stub (`poker.py`) must remain completely unsolved.
- CI and maintenance tooling must verify that the reference solution (`.meta/example.py`) passes all canonical test cases (`poker_test.py`).
- Any test execution against the reference solution must occur in an **isolated temporary directory**, guaranteeing that working-tree files are never overwritten or altered.

---

## 2. Exercise File-Role Map

| File Path | Role | Modification Policy |
| :--- | :--- | :--- |
| `exercises/practice/poker/poker.py` | **Learner Solution Stub** | **Never solve in repo.** Must contain only starter signatures (e.g., `def best_hands(hands): pass`). |
| `exercises/practice/poker/poker_test.py` | **Canonical Test Suite** | Generated/synchronized from problem specifications. Contains 37 unit tests. Do not hand-edit directly. |
| `exercises/practice/poker/.meta/example.py` | **Track Reference Solution** | Maintained implementation providing `best_hands`, `allmax`, and `hand_rank`. |
| `exercises/practice/poker/.meta/config.json` | **Exercise Metadata** | Single source of truth for file roles (`solution`, `test`, `example`). |
| `exercises/practice/poker/.meta/tests.toml` | **Test Tracking Config** | Tracks canonical test case inclusions and UUIDs from problem-specifications. |
| `exercises/practice/poker/.docs/instructions.md` | **Learner Instructions** | Problem description and poker hand ranking rules. |

---

## 3. Metadata-Based Test Discovery

Tooling must not rely on hardcoded file names. Instead, tools resolve paths dynamically from `exercises/practice/poker/.meta/config.json`:

```json
{
  "files": {
    "solution": [
      "poker.py"
    ],
    "test": [
      "poker_test.py"
    ],
    "example": [
      ".meta/example.py"
    ]
  }
}
```

Dynamic resolution ensures:
- The exact solution target (`poker.py`), test suite (`poker_test.py`), and reference implementation (`.meta/example.py`) are retrieved programmatically.
- Future refactorings or file reorganizations do not break tooling.

---

## 4. Isolated Execution Architecture

Directly running tests in the workspace presents a major risk: copying the reference implementation over `poker.py` would mutate the working tree, potentially committing solved stubs.

The isolated runner (`tools/course_checks/r36-t029.py`) solves this with the following architecture:

```
[Repository: exercises/practice/poker]
   │
   ├── Copy entire tree + dotfiles (.meta/)
   ▼
[Temporary Directory: /tmp/poker_scratch_XXXXXX]
   │
   ├── Copy .meta/example.py -> poker.py (scratch only)
   ├── Execute pytest -v --tb=short
   │     ├── Real reference: 37/37 passed (exit 0)
   │     ├── Failing reference: assertion error (exit > 0)
   │     └── Empty filter: 0 tests run (exit > 0)
   │
   ▼
[Context Manager Exit]
   └── Scratch directory purged completely
```

### Safety Guarantees
1. **Zero Working-Tree Mutation**: All operations, file copies, and bytecode generation occur exclusively inside `tempfile.TemporaryDirectory()`.
2. **Deterministic Cleanup**: Using Python's `try...finally` / context managers ensures cleanup occurs on normal completion, assertion errors, or process interruption.
3. **Failure Propagation**: If tests fail, assertions fail, or zero tests are executed, the runner exits with a non-zero exit code.

---

## 5. Prerequisites

- **Python**: 3.10+ (matching track CI environment)
- **pytest**: 8.0+
- **pytest-subtests**: (optional, for parameterized subtest reporting)
- **configlet**: Exercism track maintenance CLI

Verify prerequisites:
```bash
python3 --version
python3 -m pytest --version
```

---

## 6. Runner Usage Instructions

### Manual Execution
Run the isolated test runner tool directly from the repository root:

```bash
# Run isolated tests against the reference solution
python3 tools/course_checks/r36-t029.py

# Verbose output with detailed test case lists
python3 tools/course_checks/r36-t029.py --verbose

# Output JSON report
python3 tools/course_checks/r36-t029.py --json

# Run with custom pytest filtering
python3 tools/course_checks/r36-t029.py --pytest-args="-k test_single_hand_always_wins"
```

### Automated Verification
Execute the verification suite to test all three execution modes and stub integrity:

```bash
python3 work/R36-T029/check.py
```

The verification suite automatically:
1. Computes the initial SHA-256 hash of `exercises/practice/poker/poker.py`.
2. **Mode 1 (Real Reference)**: Confirms all 37 tests pass, including anchor cases (`test_single_hand_always_wins`, `test_highest_card_out_of_all_hands_wins`, `test_a_tie_has_multiple_winners`).
3. **Mode 2 (Deliberately Failing Reference)**: Confirms failures are detected and exit code is non-zero.
4. **Mode 3 (Zero Tests / Empty Filter)**: Confirms empty test execution is rejected with a non-zero exit code.
5. Verifies the SHA-256 hash of `poker.py` after every run, ensuring zero mutation.
6. Saves detailed records to `work/R36-T029/results.json` and `work/R36-T029/results.txt`.
