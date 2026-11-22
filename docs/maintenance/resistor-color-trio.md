# Resistor Color Trio: Maintenance & Canonical Test Coverage

This document outlines the canonical test case decisions and rationale for `resistor-color-trio` in the Exercism Python track.

## Summary of Canonical Decisions

- **Total Canonical Cases:** 10
- **Included Cases:** 10
- **Excluded Cases:** 0
- **Exclusion Rationale:** None. Python supports arbitrary-precision integers, clean integer division (`//`), exponentiation (`**`), and straightforward string formatting, so all 10 canonical test cases from problem-specifications are fully supported without requiring language-specific exclusions.

## Canonical Case Mapping Table

| Canonical UUID | Canonical Description | Python Test Method | Status | Python Operation & Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `d6863355-15b7-40bb-abe0-bfb1a25512ed` | Orange and orange and black | `test_orange_and_orange_and_black` | Included | **Base Unit ("ohms"):** Evaluates `(10 * 3 + 3) * 10**0 = 33`. Since `len(str(value)) < 4` (`value < 1000`), no metric prefix scaling is needed, returning `"33 ohms"`. |
| `1224a3a9-8c8e-4032-843a-5224e04647d6` | Blue and grey and brown | `test_blue_and_grey_and_brown` | Included | **Non-Zero Exponent Under 1000:** Evaluates `(10 * 6 + 8) * 10**1 = 680`. Magnitude is 3 digits (`len == 3 < 4`), remaining in base `"ohms"` without premature conversion to kiloohms. |
| `b8bda7dc-6b95-4539-abb2-2ad51d66a207` | Red and black and red | `test_red_and_black_and_red` | Included | **Metric Prefix ("kiloohms") with Zero Second Digit:** Evaluates `(10 * 2 + 0) * 10**2 = 2000`. Matches `4 <= len < 7`, where integer division `value // 1000` evaluates to `2`, returning `"2 kiloohms"`. |
| `5b1e74bc-d838-4eda-bbb3-eaba988e733b` | Green and brown and orange | `test_green_and_brown_and_orange` | Included | Evaluates `51 * 10**3 = 51000 ohms` -> `51 kiloohms`. Tests standard 5-digit kiloohms magnitude. |
| `f5d37ef9-1919-4719-a90d-a33c5a6934c9` | Yellow and violet and yellow | `test_yellow_and_violet_and_yellow` | Included | Evaluates `47 * 10**4 = 470000 ohms` -> `470 kiloohms`. Tests 6-digit kiloohms magnitude near megaohms boundary. |
| `5f6404a7-5bb3-4283-877d-3d39bcc33854` | Blue and violet and blue | `test_blue_and_violet_and_blue` | Included | Evaluates `67 * 10**6 = 67000000 ohms` -> `67 megaohms`. Tests megaohms metric prefix scaling (`value // 10**6`). |
| `7d3a6ab8-e40e-46c3-98b1-91639fff2344` | Minimum possible value | `test_minimum_possible_value` | Included | Evaluates `0 * 10**0 = 0 ohms`. Tests lower boundary condition with zero resistance. |
| `ca0aa0ac-3825-42de-9f07-dac68cc580fd` | Maximum possible value | `test_maximum_possible_value` | Included | Evaluates `99 * 10**9 = 99000000000 ohms` -> `99 gigaohms`. Tests gigaohms metric prefix scaling (`value // 10**9`). |
| `0061a76c-903a-4714-8ce2-f26ce23b0e09` | First two colors make an invalid octal number | `test_first_two_colors_make_an_invalid_octal_number` | Included | Evaluates `(10 * 0 + 8) * 10**0 = 8 ohms`. Guards against accidental octal interpretation of leading zeros in Python. |
| `30872c92-f567-4b69-a105-8455611c10c4` | Ignore extra colors | `test_ignore_extra_colors` | Included | Tests input slicing / indexing where inputs contain more than 3 color bands: only the first 3 bands are used. |

## Detailed Rationale for Selected UUIDs

### 1. `d6863355-15b7-40bb-abe0-bfb1a25512ed` — "Orange and orange and black"
- **Test Method:** `test_orange_and_orange_and_black`
- **Input:** `["orange", "orange", "black"]`
- **Expected Output:** `"33 ohms"`
- **Python Operations:**
  - `COLORS.index("orange")` produces `3`, giving main value `10 * 3 + 3 = 33`.
  - `COLORS.index("black")` produces `0`, giving multiplier `10**0 = 1`.
  - Total resistance: `33 * 1 = 33`.
  - Condition: `len(str(value)) < 4` (or `value < 1000`) directs the formatting to the base unit `"ohms"`.
- **Rationale:** Verifies the fundamental decoding logic where the exponent is zero. Resistors below 1000 ohms must not apply any metric prefix and must cleanly output the unit `"ohms"`.

### 2. `1224a3a9-8c8e-4032-843a-5224e04647d6` — "Blue and grey and brown"
- **Test Method:** `test_blue_and_grey_and_brown`
- **Input:** `["blue", "grey", "brown"]`
- **Expected Output:** `"680 ohms"`
- **Python Operations:**
  - `COLORS.index("blue") == 6`, `COLORS.index("grey") == 8`.
  - Main value: `10 * 6 + 8 = 68`.
  - `COLORS.index("brown") == 1`, multiplier `10**1 = 10`.
  - Total resistance: `68 * 10 = 680`.
  - Length check: `len(str(680)) == 3 < 4`.
- **Rationale:** Ensures that a non-zero exponent resulting in a 3-digit resistance under 1000 ohms does not prematurely scale to fractional metric prefixes (such as `"0.68 kiloohms"`), remaining formatted in `"ohms"`.

### 3. `b8bda7dc-6b95-4539-abb2-2ad51d66a207` — "Red and black and red"
- **Test Method:** `test_red_and_black_and_red`
- **Input:** `["red", "black", "red"]`
- **Expected Output:** `"2 kiloohms"`
- **Python Operations:**
  - `COLORS.index("red") == 2`, `COLORS.index("black") == 0`.
  - Main value: `10 * 2 + 0 = 20`.
  - Multiplier: `10**2 = 100`.
  - Total resistance: `20 * 100 = 2000`.
  - Condition: `len(str(2000)) == 4` triggers the `kiloohms` branch.
  - Scaling: Integer division `value // 1000` evaluates to `2`.
  - Formatted label: `f"{value // 1000} kiloohms"` yields `"2 kiloohms"`.
- **Rationale:** Tests metric prefix scaling where the second band is zero (`black`), resulting in a trailing zero in the base number (`20`) which, when multiplied by `100`, produces `2000`. It ensures that integer division cleanly scales the value to single-digit `"2 kiloohms"` rather than failing or retaining extra zeros.
