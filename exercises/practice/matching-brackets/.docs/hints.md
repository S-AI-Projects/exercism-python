# Hints

## 1. Watch closing brackets

A closing bracket needs an opening bracket of the same kind, and it must close
the most recently opened bracket. Check that contract when you process each
closer, including when the input starts with one. For a quick diagnostic, ask
what `is_paired("}")` should return: there is no opening brace to match it.
