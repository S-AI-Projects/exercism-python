# Grep Implementation Mutation Analysis

## Overview
This document records a deliberate mutation analysis of the `matches` helper function in `exercises/practice/grep/.meta/example.py`.

## Deliberate Mutant
In `matches(line, pattern, flags)`:
```python
# MUTANT: Inverted flag logic omission
def matches_mutant(line, pattern, flags):
    if '-i' in flags:
        line = line.lower()
        pattern = pattern.lower()

    if '-x' in flags:
        if len(pattern) != len(line.rstrip()):
            return '-v' in flags

    if '-v' in flags:
        # Mistaken assumption: accidentally returning positive match instead of negation
        return pattern in line

    return pattern in line
```

## Mistaken Conceptual Assumption
The developer assumes that the `-v` flag branch does not require boolean negation of the substring membership test (`pattern not in line`), or mistakenly assumes that `-v` is handled downstream at the output formatting layer rather than during line selection.

## Rejecting Tests

| Rejecting Test ID / Name | Input Pattern & Flags | Expected Behavior | Mutant Actual Behavior |
|---|---|---|---|
| `test_one_file_several_matches_inverted_flag` | `pattern="Of"`, `flags="-v"`, files: `["paradise-lost.txt"]` | Returns 5 lines that do not contain `"Of"` | Returns empty string (only lines containing `"Of"`, inverted) |
| `test_multiple_files_several_matches_inverted_flag` | `pattern="That"`, `flags="-v"`, files: `["paradise-lost.txt", "iliad.txt", ...]` | Returns all lines across files without `"That"` prefixed with filename | Returns lines containing `"That"` |

## Automated Verification
Run:
```bash
python3 work/R36-T033/check.py
```
This check verifies that:
1. The reference implementation passes 100% of the test suite.
2. The mutant fails on `test_one_file_several_matches_inverted_flag` and `test_multiple_files_several_matches_inverted_flag`.
3. Learner stubs remain unsolved.
