# Hints

## General

- Traditional Roman numerals represent numbers between 1 and 3,999 (`MMMCMXCIX`).
- Roman numerals are formed by combining symbols from the set `I` (1), `V` (5), `X` (10), `L` (50), `C` (100), `D` (500), and `M` (1000).
- Numerals are written from left to right in descending order of value.
- Subtractive notation is used when a smaller numeral immediately precedes a larger numeral: 4 is `IV`, 9 is `IX`, 40 is `XL`, 90 is `XC`, 400 is `CD`, and 900 is `CM`.

## Approach Selection: Greedy Subtraction vs. Positional Table Lookup

When implementing Arabic to Roman numeral conversion, two prominent algorithmic paradigms provide distinct trade-offs in data representation, control flow, and computational efficiency:

### 1. Greedy Subtraction (Iterative Threshold Reduction)
- **Data Representation:** An ordered collection of 13 numeric thresholds paired with their Roman strings, sorted in descending order: `(1000, 'M')`, `(900, 'CM')`, `(500, 'D')`, `(400, 'CD')`, ..., down to `(1, 'I')`.
- **Control Flow:** An outer loop cycles through the 13 thresholds from largest to smallest. An inner `while` loop repeatedly subtracts the threshold value from the target number while `number >= threshold`, appending the matching Roman symbol to an accumulator string.
- **Trade-offs:** 
  - *Pros:* Minimal memory usage (only 13 tuples), intuitive "coin change" greedy reduction pattern.
  - *Cons:* Variable execution steps depending on the number's structure (from 1 subtraction for `1` up to 15 inner subtractions for numbers like `3888`). Subtractive combinations (`IV`, `IX`, `XL`, etc.) must be hardcoded as synthetic thresholds.

### 2. Positional Table Lookup (Place-Value Decomposition)
- **Data Representation:** Four independent precomputed tables or tuples representing the powers of 10:
  - Thousands ($10^3$): `("", "M", "MM", "MMM")`
  - Hundreds ($10^2$): `("", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM")`
  - Tens ($10^1$): `("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC")`
  - Ones ($10^0$): `("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX")`
- **Control Flow:** The input number is directly split into its decimal digits using integer division and modulo (`// 1000`, `// 100`, `// 10`, `% 10`). Each digit acts as a direct index into the corresponding table, and the resulting four strings are concatenated.
- **Trade-offs:**
  - *Pros:* Fully deterministic $\mathcal{O}(1)$ time execution with zero loops, zero subtractions, and exactly 4 direct table index lookups. Subtractive combinations naturally fit at indices 4 and 9 in each table.
  - *Cons:* Slightly larger static memory footprint (34 strings across 4 tuples), though the memory is fixed and negligible in practice.

---

### Worked Example: Converting 27 (`XXVII`)

Consider converting the number `27`:

#### Under Greedy Subtraction:
1. Scan thresholds: 1000, 900, 500, 400, 100, 90, 50, 40 are all $> 27$ (skipped).
2. Threshold 10: $27 \ge 10 \implies$ append `X`, remainder $= 17$.
3. Threshold 10: $17 \ge 10 \implies$ append `X`, remainder $= 7$.
4. Threshold 5: $7 \ge 5 \implies$ append `V`, remainder $= 2$.
5. Threshold 1: $2 \ge 1 \implies$ append `I`, remainder $= 1$.
6. Threshold 1: $1 \ge 1 \implies$ append `I`, remainder $= 0$.
7. Result: `XXVII` (evaluated across 6 threshold checks and 5 subtraction steps).

#### Under Positional Table Lookup:
1. Thousands: $27 // 1000 = 0 \implies \text{THOUSANDS}[0] = \text{""}$.
2. Hundreds: $(27 \% 1000) // 100 = 0 \implies \text{HUNDREDS}[0] = \text{""}$.
3. Tens: $(27 \% 100) // 10 = 2 \implies \text{TENS}[2] = \text{"XX"}$.
4. Ones: $27 \% 10 = 7 \implies \text{ONES}[7] = \text{"VII"}$.
5. Concatenation: `"" + "" + "XX" + "VII" = "XXVII"` (assembled in 4 constant-time index operations with zero loops).
