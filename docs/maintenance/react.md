# Maintenance: React Mutation-Driven Regression

## Overview
This document records mutation testing on the `react` exercise (`exercises/practice/react`), documenting a deliberate mutant in `Cell`, the rejecting test case, and expected contractual behavior.

## Deliberate Mutant
In `exercises/practice/react/.meta/example.py`, the property setter for `value` on `Cell` was mutated to simulate the mistaken assumption that cells are immutable once initialized:

### Original Implementation
```python
    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.counter += 1
        for cell in self._watchers:
            cell.compute()
```

### Mutated Implementation
```python
    @value.setter
    def value(self, new_value):
        # Mistaken assumption: InputCell is write-once / immutable once initialized
        if self._value is None:
            self._value = new_value
        self.counter += 1
        for cell in self._watchers:
            cell.compute()
```

## Rejecting Test Case
- **Test ID / Method:** `test_an_input_cell_s_value_can_be_set`
- **Minimal Diagnostic Input:**
  ```python
  input = InputCell(4)
  input.value = 20
  self.assertEqual(input.value, 20)
  ```
- **Expected Outcome:** `input.value == 20`
- **Mutant Outcome:** `AssertionError: 4 != 20` (mutant rejected)

## Regression Verification
- All enabled test cases in `react_test.py` pass against the clean reference implementation.
- The mutant reliably fails `test_an_input_cell_s_value_can_be_set`.
- Debugging guidance has been added to `exercises/practice/react/.docs/hints.md`.
