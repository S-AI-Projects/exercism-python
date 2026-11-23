# Minesweeper Maintenance Guide

## Overview

The `minesweeper` exercise requires annotating a given grid of empty spaces (`" "`) and mines (`"*"`) with numbers indicating the count of adjacent mines.

In the Python track:
- Total canonical cases: 12
- Excluded cases: 0
- Included cases: 12
- Track-specific custom cases: 3 (`test_annotate_9`, `test_different_len`, `test_invalid_char`)
- Total active test cases: 15

## Canonical Test Case Mapping

| UUID | Description | Test Method Name | Status | Python Rationale / Operation |
|---|---|---|---|---|
| `0c5ec4bd-dea7-4138-8651-1203e1cb9f44` | no rows | `test_no_rows` | Included | Input `[]` is falsy in Python (`if not minefield: return []`). Handled cleanly as base case. |
| `650ac4c0-ad6b-4b41-acde-e4ea5852c3b8` | no columns | `test_no_columns` | Included | Input `[""]` has `row_len = 0`. Python's `range(0)` results in an empty iteration, returning `[""]`. |
| `6fbf8f6d-a03b-42c9-9a58-b489e9235478` | no mines | `test_no_mines` | Included | Grid with only spaces has `count('*') == 0`. The condition `if counts == 0: continue` leaves all spaces unchanged. |
| `61aff1c4-fb31-4078-acad-cd5f1e635655` | minefield with only mines | `test_minefield_with_only_mines` | Included | Grid with only mines skips counting on non-space cells (`board[r][c] != ' '`). |
| `84167147-c504-4896-85d7-246b01dea7c5` | mine surrounded by spaces | `test_mine_surrounded_by_spaces` | Included | Standard 3x3 surrounding calculation. |
| `cb878f35-43e3-4c9d-93d9-139012cccc4a` | space surrounded by mines | `test_space_surrounded_by_mines` | Included | Center cell has 8 neighbors, outputting `"8"`. |
| `7037f483-ddb4-4b35-b005-0d0f4ef4606f` | horizontal line | `test_horizontal_line` | Included | 1D horizontal row indexing and slicing `minefield[row][low:high]`. |
| `e359820f-bb8b-4eda-8762-47b64dba30a6` | horizontal line, mines at edges | `test_horizontal_line_mines_at_edges` | Included | 1D boundary indexing with `max(idx - 1, 0)` and `min(idx + 2, len)`. |
| `c5198b50-804f-47e9-ae02-c3b42f7ce3ab` | vertical line | `test_vertical_line` | Included | 1D column traversal with multi-row inspection. |
| `0c79a64d-703d-4660-9e90-5adfa5408939` | vertical line, mines at edges | `test_vertical_line_mines_at_edges` | Included | Vertical boundaries handled by `index1 > 0` and `index1 < col_len - 1`. |
| `4b098563-b7f3-401c-97c6-79dd1b708f34` | cross | `test_cross` | Included | Multi-neighbor non-uniform distribution. |
| `04a260f1-b40a-4e89-839e-8dd8525abe0e` | large minefield | `test_large_minefield` | Included | Comprehensive multi-row multi-column grid verification. |

## Rationale for Key Canonical Decisions

### 1. `0c5ec4bd-dea7-4138-8651-1203e1cb9f44` (`test_no_rows`)
- **Input:** `[]`
- **Expected:** `[]`
- **Behavior in Python:** The input is an empty list. In Python, `bool([])` evaluates to `False`. The reference implementation guards with:
  ```python
  if not minefield:
      return []
  ```
  This immediately returns `[]` without indexing into `minefield[0]`, preventing an `IndexError`.

### 2. `650ac4c0-ad6b-4b41-acde-e4ea5852c3b8` (`test_no_columns`)
- **Input:** `[""]`
- **Expected:** `[""]`
- **Behavior in Python:** The input is a list containing an empty string. Here, `col_len = len(minefield) == 1`, and `row_len = len(minefield[0]) == 0`.
  In Python, `range(row_len)` is `range(0)`. The inner loop never executes, so no cell transformations occur. The board list comprehension reconstructs `[''.join(row) for row in board]`, which evaluates to `[""]`.

### 3. `6fbf8f6d-a03b-42c9-9a58-b489e9235478` (`test_no_mines`)
- **Input:** `["   ", "   ", "   "]`
- **Expected:** `["   ", "   ", "   "]`
- **Behavior in Python:** All cells contain the space character `" "`. When querying neighbor slices `minefield[r][low:high].count('*')`, every slice returns `0`. Because `counts == 0`, the reference implementation executes `continue`, leaving each cell as `" "`.

## Verification

To run verification against the reference implementation in an isolated environment without altering the learner stub:
```bash
python3 work/R36-T031/check.py
```
