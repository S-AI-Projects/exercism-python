# Hints

## General
- Remember that `InputCell` values are mutable throughout the lifetime of the cell, not just at initialization time.
- If your implementation treats `InputCell` as write-once or immutable (e.g. ignoring updates or guarding updates with `if self._value is None:`), tests updating cell values will fail:
  ```python
  cell = InputCell(4)
  cell.value = 20
  # cell.value must now be 20, not 4!
  ```
- Whenever an `InputCell` value changes, ensure any dependent `ComputeCell` instances are triggered to recompute their values and notify registered callbacks.
