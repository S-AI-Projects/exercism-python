# Hints

## Python Guidance: Decoding with Regular Expressions

When implementing `decode`, a common challenge is handling run-length counts that contain multiple digits (such as `"12W"` or `"100A"`).

### Replacement Functions with `re.sub`
Python's standard library provides [`re.sub`](https://docs.python.org/3/library/re.html#re.sub), which accepts a callable function or lambda as its `repl` argument. The function is invoked for every non-overlapping match and receives a `Match` object.

#### Executable Micro-Example
```python
import re

text = "3A12B"
pattern = r'(\d+)(\D)'
decoded = re.sub(pattern, lambda m: m.group(2) * int(m.group(1)), text)
print(decoded)
# Expected Output: "AAABBBBBBBBBBBB"
```

### Exercise-Relevant Pitfall: Fixed-Width Digit Assumption
A common pitfall is assuming each count is only a single character wide (e.g. reading character-by-character or using single-digit regex `r'(\d)(\D)'`):
```python
import re

text = "12W"
# Pitfall: Single-digit pattern (\d)(\D) only matches ('2', 'W'), silently dropping the tens digit '1':
bad_matches = re.findall(r'(\d)(\D)', text)
# Output: [('2', 'W')] (lost '1', decoded as 2 'W's instead of 12)

# Correct: One or more digits (\d+) properly captures the entire integer count:
correct_matches = re.findall(r'(\d+)(\D)', text)
# Output: [('12', 'W')]
```
Using `\d+` ensures arbitrary digit lengths are parsed as a cohesive integer count before character multiplication.
