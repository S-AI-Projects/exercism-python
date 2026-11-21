# reverse-string Maintenance & Isolated Test Execution

This document specifies the maintenance workflow and isolated verification runner for `exercises/practice/reverse-string`.

## File Roles & Configuration

The exercise configuration in `.meta/config.json` declares the following file roles:

| Role | Declared Path | Purpose |
| --- | --- | --- |
| Solution | `reverse_string.py` | Learner stub file (`def reverse(text): pass`); kept strictly unsolved in the repository. |
| Test | `reverse_string_test.py` | Pytest / unittest test suite containing 7 canonical test cases. |
| Example | `.meta/example.py` | Maintained reference implementation (`return text[::-1]`). |

## Isolated Runner Architecture

The runner `tools/course_checks/r36-t009.py` provides an isolated test execution environment:
1. **Hash Verification**: Computes the SHA-256 digest of `reverse_string.py` before any operation.
2. **Temporary Staging**: Clones the exercise files to a sandboxed temporary directory via `tempfile.mkdtemp()`.
3. **Reference Overlay**: Overwrites the stub `reverse_string.py` *only inside the temporary staging directory* with `.meta/example.py`.
4. **Pytest Execution**: Executes pytest against `reverse_string_test.py` in the temporary directory.
5. **Cleanup & Invariant Guarantee**: Automatically removes the temporary staging directory and verifies that the repository's learner file hash is completely unmodified.

## Canonical Test Cases

The test suite exercises 7 canonical cases:
- `test_an_empty_string`: Empty string returns empty string (`""` -> `""`).
- `test_a_word`: Reversal of a basic word (`"robot"` -> `"tobor"`).
- `test_a_capitalized_word`: Case preservation during reversal (`"Ramen"` -> `"nemaR"`).
- `test_a_sentence_with_punctuation`: Punctuation handling (`"I'm hungry!"` -> `"!yrgnuh m'I"`).
- `test_a_palindrome`: Symmetric words (`"racecar"` -> `"racecar"`).
- `test_an_even_sized_word`: Even length strings (`"drawer"` -> `"reward"`).
- `test_wide_characters`: Multi-byte Unicode characters (`"子猫"` -> `"猫子"`).

## Verification Command

Run the isolated runner from the repository root:

```bash
python3 tools/course_checks/r36-t009.py
```

Expected output:
```
7 passed in 0.01s
PASS: 7 tests executed in isolation; learner stub unchanged.
```
