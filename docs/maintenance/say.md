# Maintenance: Say Isolated Test Runner

## Overview
This document specifies the isolated test execution architecture for the `say` exercise (`exercises/practice/say`). The isolated runner protects the unsolved learner starter files while testing exercise references and maintaining track CI.

## Tool Requirements
- Python 3.10 or higher
- `pytest` (standard track CI test framework)
- Standard library modules: `hashlib`, `tempfile`, `shutil`, `subprocess`

## Execution Command
To run the isolated test suite against the reference implementation:
```bash
python3 tools/course_checks/r36-t059.py
```

## Architectural Protections & Guarantees
1. **Isolated Scratch Copy:**
   All execution occurs inside an isolated temporary directory (`tempfile.TemporaryDirectory()`). The exercise files are copied into scratch storage, where `.meta/example.py` is substituted into `say.py` only within that temporary copy.
2. **Learner File SHA-256 Hashing:**
   The runner computes a SHA-256 digest of `exercises/practice/say/say.py` immediately before setting up the scratch environment and verifies that the digest is identical after completion (including during failing or interrupted runs).
3. **Failure & Status Code Propagation:**
   Pytest exit codes and test counts are accurately parsed and propagated to calling scripts. Zero-test runs and assertion failures trigger a non-zero exit code.
