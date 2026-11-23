# Diamond File-Role Mapping & Maintenance

## Overview
This document specifies the file-role mappings and maintenance structure for the `diamond` exercise in the Python track.

## File Role Architecture

### 1. Learner-Facing Files
These files are downloaded by students when fetching the exercise via the Exercism CLI.
- **`diamond.py`** (`files.solution`): The starter stub containing function prototypes (`rows(letter)`) and docstrings/placeholders for student solutions. Must remain unsolved in the repository.
- **`diamond_test.py`** (`files.test`): The unit test suite executed by the student (`pytest` or `unittest`).
- **`.docs/instructions.md`**: Problem description and specification presented in the web UI and CLI.

### 2. Track Maintenance & Authoring Files
These files reside in `.meta/` and are used by maintainers and automated tooling for reference verification, test generation, and metadata tracking:
- **`.meta/example.py`** (`files.example`): The reference canonical implementation used by CI to verify that all test cases pass.
- **`.meta/config.json`**: Exercise metadata declaring authors, contributors, blurb, and relative file roles.
- **`.meta/tests.toml`**: Tracking file mapping canonical problem-specification UUIDs to their enabled status.
- **`.meta/template.j2`**: Jinja2 template for regenerating `diamond_test.py` from problem-specifications canonical data.

## Configuration Map

| Role in `config.json` | Relative Path | Target State / Constraint |
|---|---|---|
| `solution` | `diamond.py` | Exists, contains empty `pass` stub. |
| `test` | `diamond_test.py` | Exists, defines test suite (`DiamondTest`). |
| `example` | `.meta/example.py` | Exists, complete passing implementation. |

## Validation Command
To verify the configuration and file paths automatically:
```bash
python3 tools/course_checks/r36-t038.py
```
