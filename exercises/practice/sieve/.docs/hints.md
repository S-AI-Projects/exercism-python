# Hints

## Approach Selection

There are two primary ways to represent the sieve state in Python:

1. **Boolean Array (Direct Indexing - Reference Approach)**
   - Pre-allocate a list of booleans of size `limit + 1`, e.g. `prime = [True] * (limit + 1)`, setting index 0 and 1 to `False`.
   - Iterating up to `sqrt(limit)`, when a number `p` is prime, mark its multiples composite starting at `p * p` with step `p`.
   - **Trade-off:** Minimal memory per slot, contiguous cache locality, and $O(1)$ random access by direct indexing without hash lookups.

2. **Composite Set (Dynamic Filter - Alternative Approach)**
   - Maintain a Python `set()` of composites. Iterating through each candidate from 2 to `limit`, if the candidate is not in the set, record it as prime and add all its multiples (`range(p * p, limit + 1, p)`) to the set.
   - **Trade-off:** Avoids pre-allocating an indexed buffer, but incurs hashing overhead and dynamic resizing costs for large limits.

### Small Worked Example (`limit = 10`)

- Initial candidates: `2, 3, 4, 5, 6, 7, 8, 9, 10`.
- At `p = 2`: 2 is prime. Mark multiples $\ge 2^2$: `4, 6, 8, 10`.
- At `p = 3`: 3 is prime. Mark multiples $\ge 3^2$: `9`.
- Since $3 \ge \lfloor\sqrt{10}\rfloor$, loop finishes. Unmarked numbers: `[2, 3, 5, 7]`.
