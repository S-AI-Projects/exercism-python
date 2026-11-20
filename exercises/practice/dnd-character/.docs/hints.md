# Hints

## Python

The reference implementation uses [`math.floor`](https://docs.python.org/3/library/math.html#math.floor) to compute the ability modifier from the raw ability score: `math.floor((value - 10) / 2)`.

In Dungeons & Dragons, modifiers always round down towards negative infinity. When `(value - 10)` is negative and odd, Python's `math.floor` rounds down to the next lower integer:

```python
import math

def calculate_modifier(score):
    return math.floor((score - 10) / 2)

print(calculate_modifier(3))
print(calculate_modifier(5))
```

Output:

```text
-4
-3
```

A common pitfall is using `int((score - 10) / 2)`, which truncates towards zero rather than rounding down. For `score = 3`, `(3 - 10) / 2 = -3.5`. `int(-3.5)` incorrectly truncates to `-3`, whereas `math.floor(-3.5)` correctly rounds down to `-4`. Similarly, for `score = 5`, `(5 - 10) / 2 = -2.5`, which correctly rounds down to `-3`. Alternatively, Python's integer division operator `(score - 10) // 2` performs floor division natively.
