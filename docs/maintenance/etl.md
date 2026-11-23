# ETL Test Generation Path Maintenance

## Overview
This document describes the test generation pipeline for the `etl` exercise in the Python track, mapping canonical data to the generated test suite.

## Generation Pipeline

### 1. Command
From the root of the `exercism-python` repository:
```bash
python3 bin/generate_tests.py -p .problem-specifications etl
```
Or to verify without modifying files:
```bash
python3 bin/generate_tests.py -p .problem-specifications --check etl
```

### 2. Input Files
- **Canonical Data**: `.problem-specifications/exercises/etl/canonical-data.json`
- **Track Template**: `exercises/practice/etl/.meta/template.j2`
- **Track Configuration**: `exercises/practice/etl/.meta/tests.toml`
- **Track Config JSON**: `exercises/practice/etl/.meta/config.json`

### 3. Output File
- `exercises/practice/etl/etl_test.py`

## Canonical Case to Output Mapping Table

| Canonical UUID | Canonical Description | Generated Test Name | Input (`legacy`) | Expected Output | Status |
|---|---|---|---|---|---|
| `78a7a9f9-4490-4a47-8ee9-5a38bb47d28f` | single letter | `test_single_letter` | `{1: ["A"]}` | `{"a": 1}` | Included |
| `60dbd000-451d-44c7-bdbb-97c73ac1f497` | single score with multiple letters | `test_single_score_with_multiple_letters` | `{1: ["A", "E", "I", "O", "U"]}` | `{"a": 1, "e": 1, "i": 1, "o": 1, "u": 1}` | Included |
| `f5c5de0c-301f-4fdd-a0e5-df97d4214f54` | multiple scores with multiple letters | `test_multiple_scores_with_multiple_letters` | `{1: ["A", "E"], 2: ["D", "G"]}` | `{"a": 1, "d": 2, "e": 1, "g": 2}` | Included |
| `5db8ea89-ecb4-4dcd-902f-2b418cc87b9d` | multiple scores with differing numbers of letters | `test_multiple_scores_with_differing_numbers_of_letters` | `{1: ["A",...], 2: ["D", "G"], ...}` | Comprehensive inverted index dict | Included |

## Reproducibility Verification
Regenerating the tests using the command above reproduces `exercises/practice/etl/etl_test.py` identically with 0 manual modifications. Verification is automated via:
```bash
python3 tools/course_checks/r36-t032.py
```
