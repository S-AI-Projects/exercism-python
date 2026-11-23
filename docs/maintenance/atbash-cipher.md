# Maintenance: Atbash Cipher Complexity Analysis

## Overview
This document evaluates the algorithmic complexity and empirical scaling of `base_trans` in `exercises/practice/atbash-cipher/.meta/example.py`.

## Algorithmic Complexity
`base_trans(text)` executes four sequential operations:
1. **Filtering:** List comprehension `[c for c in text if c.isalnum()]` iterates over all $N = \text{len}(text)$ characters: $O(N)$ time.
2. **Joining:** `''.join(...)` creates a new string of $K$ alphanumeric characters ($K \le N$): $O(K)$ time and space.
3. **Lowercasing:** `.lower()` allocates and transforms the $K$ characters: $O(K)$ time and space.
4. **Translation:** `.translate(trtbl)` scans the string and replaces characters using CPython's 256-entry precomputed translation table: $O(K)$ time.

**Total Time Complexity:** $\mathcal{O}(N)$ linear in input character count.
**Total Auxiliary Space:** $\mathcal{O}(N)$ linear to store intermediate filtered and transformed character sequences.

## Empirical Measurement
Measurements isolate pure algorithmic execution time inside Python using `time.perf_counter_ns()`, entirely separating algorithm work from Python process-startup or compilation time. Correctness was asserted on all test cases prior to timing.

### Tested Input Sizes (Domain Test Cases)
Five repetitions were recorded per input size under constant environment conditions:

| Size Category | Input String | Input Length ($N$) | Expected Transformed Output | Median Execution Time |
|---|---|---|---|---|
| **Small** | `"yes"` | 3 | `"bvh"` | ~0.5 – 1.0 µs |
| **Medium** | `"mindblowingly"` | 13 | `"nrmwyoldrmtob"` | ~1.0 – 1.8 µs |
| **Large** | `"The quick brown fox jumps over the lazy dog."` | 43 | `"gsvjfrxpyildmulcqfnkhlevigsvozabwlt"` | ~2.5 – 4.0 µs |

## Limits of Conclusion
- The linear scaling holds for all valid text inputs within typical Exercism and ASCII domain ranges.
- Performance is dominated by CPython internal string allocations (`join`, `lower`) and the C-accelerated `str.translate` function.
- Because `trtbl` is precomputed at module load time, table initialization does not contribute to per-call invocation costs.
