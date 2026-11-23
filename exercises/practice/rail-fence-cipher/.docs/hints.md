# Hints

## Rail Fence Cipher Contract Walkthrough

The Rail Fence cipher encodes messages along a zig-zag oscillation between rails.

### Decision Table for Anchor Test Cases

| Case Name | Message Input | Rails | Cycle Period | Rail Distribution | Expected Output |
|---|---|---|---|---|---|
| `test_encode_with_two_rails` | `"XOXOXOXOXOXOXOXOXO"` | 2 | 2 (`[0, 1]`) | Rail 0 (9 X's), Rail 1 (9 O's) | `"XXXXXXXXXOOOOOOOOO"` |
| `test_encode_with_three_rails` | `"WEAREDISCOVEREDFLEEATONCE"` | 3 | 4 (`[0, 1, 2, 1]`) | Rail 0: `"WECRLTE"`, Rail 1: `"ERDSOEEFEAOCA"`, Rail 2: `"IVDEN"` | `"WECRLTEERDSOEEFEAOCAIVDEN"` |
| `test_encode_with_ending_in_the_middle` | `"EXERCISES"` | 4 | 6 (`[0, 1, 2, 3, 2, 1]`) | Rail 0: `"ES"`, Rail 1: `"XIE"`, Rail 2: `"ECS"`, Rail 3: `"R"` | `"ESXIEECSR"` |

### Key Contract Insights
1. **Mid-Cycle Termination (`test_encode_with_ending_in_the_middle`):**
   - The message length ($N = 9$) does not need to align with a full cycle period ($2 \times (4 - 1) = 6$).
   - The final character `'S'` at index 8 lands on Rail 2 while ascending back toward Rail 0.
2. **Specified vs. Unspecified Contracts:**
   - **Specified:** Characters are treated as opaque literal elements. Whitespace, casing, and digits are preserved exactly as passed.
   - **Unspecified:** Inputs with `rails < 2` or non-integer types are not part of the standard test suite. Do not introduce arbitrary custom exceptions or automatic type coercion unless explicitly specified.
