# Palindrome Products canonical case notes

The three reviewed canonical cases are included in `.meta/tests.toml`. Their
Python coverage and the reference operation that determines the result are:

| UUID | Canonical case | Python test | Rationale |
| --- | --- | --- | --- |
| `5cff78fe-cf02-459d-85c2-ce584679f887` | find the smallest palindrome from single digit factors | `test_find_the_smallest_palindrome_from_single_digit_factors` | `smallest()` searches palindromes from `min_factor**2` ascending; factor pair `(1, 1)` satisfies `1 <= factor <= 9`, returning `(1, [[1, 1]])`. |
| `0853f82c-5fc4-44ae-be38-fadb2cced92d` | find the largest palindrome from single digit factors | `test_find_the_largest_palindrome_from_single_digit_factors` | `largest()` searches palindromes from `max_factor**2` descending; palindrome 9 yields valid factor pairs `[[1, 9], [3, 3]]` within `[1, 9]`. |
| `66c3b496-bdec-4103-9129-3fcb5a9063e1` | find the smallest palindrome from double digit factors | `test_find_the_smallest_palindrome_from_double_digit_factors` | `smallest()` searches palindromes from `10**2=100` ascending; 121 is the first palindrome with factors `[[11, 11]]` within `[10, 99]`. |

At this revision the canonical TOML has 13 entries and zero explicit
exclusions. The test suite has 13 test methods corresponding to all 13
canonical cases. All cases are enabled and pass against the maintained
reference implementation.

Run the isolated reference check with:

```bash
python3 work/R36-T001/check.py
```

The script copies the whole exercise, including dotfiles, into a temporary
directory, substitutes `.meta/example.py` for the solution there, and runs
the configured test module. It writes input and result summaries, captured
pytest output, and tool versions beside itself.
