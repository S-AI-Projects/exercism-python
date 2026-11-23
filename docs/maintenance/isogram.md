# Isogram Isolated Test Runner Documentation

## Overview
This document specifies the isolated test execution architecture for `exercises/practice/isogram`.

## Isolated Test Execution Strategy
To verify reference implementations without altering or overwriting student solution stubs:
1. Parse relative paths from `exercises/practice/isogram/.meta/config.json`.
2. Allocate an isolated temporary directory via Python's `tempfile.TemporaryDirectory`.
3. Copy the full exercise tree (including dotfiles and test files).
4. Substitute the reference implementation (`.meta/example.py`) into the solution path (`isogram.py`) only inside the temporary directory.
5. Execute `pytest -q` within the temporary scratch directory.
6. Verify return code and ensure all tests pass (including `test_empty_string`, `test_isogram_with_only_lower_case_characters`, and `test_word_with_one_duplicated_character`).
7. Clean up the temporary workspace, leaving the working directory completely untouched.

## Execution Command
To run the automated isolated check:
```bash
python3 tools/course_checks/r36-t039.py
```

## Tool Requirements
- Python 3.10+
- `pytest` (compatible with track requirements)
- `pytest-subtests`
