# Maintenance: Change File-Role Mapping & Configuration

## Overview
This document specifies the exact file roles and path resolution contracts defined in `exercises/practice/change/.meta/config.json`.

## File-Role Map

| Role | Declared Relative Path | Role Description & Artifact Nature |
|---|---|---|
| **`solution`** | `change.py` | Learner starter file. Must remain unsolved starter stub with function signatures and `pass`. |
| **`test`** | `change_test.py` | Auto-generated test suite generated from canonical data using `.meta/template.j2`. |
| **`example`** | `.meta/example.py` | Maintained reference implementation used by CI and test runners to verify test suite validity. |

### Generated vs Maintained Artifacts
- **Generated Artifact:** `change_test.py` is produced by `bin/generate_tests.py change` from `.problem-specifications/exercises/change/canonical-data.json` and `.meta/template.j2`. It must not be hand-edited.
- **Maintained Metadata:** `.meta/config.json` and `.meta/tests.toml` are track-maintained metadata files defining file roles and canonical test case inclusion/exclusions.

## Runner Path Resolution Mechanism
Automated test runners and CI executors do not search directories heuristically. Instead:
1. The runner reads `.meta/config.json`.
2. It parses `files.test[0]` to locate the unit test file (`change_test.py`).
3. It parses `files.example[0]` to locate the reference implementation (`.meta/example.py`).
4. In isolated test environments, the runner substitutes `files.example[0]` into `files.solution[0]` (`change.py`) and executes `pytest` against `files.test[0]`.

## Reproducible Validation Command
Run the configuration and path safety checker:
```bash
python3 tools/course_checks/r36-t058.py
```
This check ensures that all paths resolve strictly within `exercises/practice/change`, rejects directory traversal attacks (`..`), and confirms the physical presence of all declared files.
