# Hints

## Debugging

- Pay special attention to the inverted matching flag (`-v`). A common mistaken assumption is to perform the membership check and forget to negate the final boolean outcome, or assume that `-v` only inverts when used in combination with whole-line matching (`-x`). Inverted matching requires that lines *not* containing the pattern are collected, regardless of whether `-x` or multiple file flags are active.
- Ensure that flags like `-i` (case-insensitivity) normalize strings before performing substring or line-equality checks, ensuring that neither positive nor inverted matching operates on mismatched casings.
