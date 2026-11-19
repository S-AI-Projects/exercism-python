# Hints

## Python

The reference implementation uses [`functools.reduce`](https://docs.python.org/3/library/functools.html#functools.reduce) to fold the digits from left to right. Each step multiplies the value accumulated so far by 16, then adds the next digit. The initial value `0` is important: it makes an empty digit list produce `0`, which is the result for an empty hexadecimal string.

```python
from functools import reduce

def value_of_digits(digits):
    return reduce(lambda total, digit: total * 16 + digit, digits, 0)

print(value_of_digits([1, 10, 15]))
print(value_of_digits([]))
```

Output:

```text
431
0
```

The second result depends on the initializer. For example, `reduce(lambda total, digit: total * 16 + digit, [])` raises `TypeError` because there is no first item to use as the initial total. Keep the explicit `0` so the empty input has a defined value. In the full exercise, validate characters before folding so invalid input raises `ValueError` as required.
