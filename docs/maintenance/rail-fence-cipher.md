# Maintenance: Rail Fence Cipher Contract Specification

## Overview
This document formalizes the contract, decision table, and boundary conditions for `exercises/practice/rail-fence-cipher`.

## Contract Decision Table

| Test Method | Input Message | Rails ($R$) | Period $2(R-1)$ | Rail Character Grouping | Expected Output |
|---|---|---|---|---|---|
| `test_encode_with_two_rails` | `"XOXOXOXOXOXOXOXOXO"` | 2 | 2 | Rail 0: `"XXXXXXXXX"`<br>Rail 1: `"OOOOOOOOO"` | `"XXXXXXXXXOOOOOOOOO"` |
| `test_encode_with_three_rails` | `"WEAREDISCOVEREDFLEEATONCE"` | 3 | 4 | Rail 0: `"WECRLTE"`<br>Rail 1: `"ERDSOEEFEAOCA"`<br>Rail 2: `"IVDEN"` | `"WECRLTEERDSOEEFEAOCAIVDEN"` |
| `test_encode_with_ending_in_the_middle` | `"EXERCISES"` | 4 | 6 | Rail 0: `"ES"`<br>Rail 1: `"XIE"`<br>Rail 2: `"ECS"`<br>Rail 3: `"R"` | `"ESXIEECSR"` |

## Contract Boundaries
1. **Mid-Cycle Endings:**
   The zig-zag path bounces between rail $0$ and rail $R - 1$. An encoded message terminates as soon as all input characters are placed, without padding or requirement to reach an apex.
2. **Character Handling:**
   All input characters (alphanumeric, spaces, punctuation) are preserved verbatim. No case folding or character sanitization is permitted.
3. **Unspecified Edge Cases:**
   Canonical problem specifications do not mandate behavior for non-positive rails ($R \le 1$). Implementations should avoid introducing arbitrary uncontracted validation rules or extra exceptions.
