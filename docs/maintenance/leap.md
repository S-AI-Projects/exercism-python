# Maintenance: Leap

## Overview
This document records the canonical case rationale and coverage mapping for the `leap` exercise in the Exercism Python track (`exercises/practice/leap`).

## Canonical Test Case Decisions

Total canonical cases: 9
- Included cases: 9
- Excluded cases: 0
- Changed inclusions: 0

| UUID | Test Function | Year Input | Expected | Python Operation Rationale |
|---|---|---|---|---|
| `6466b30d-519c-438e-935d-388224ab5223` | `test_year_not_divisible_by_4_in_common_year` | 2015 | `False` | `year % 4 != 0`: Direct check of fundamental rule that common years not divisible by 4 cannot be leap years. |
| `ac227e82-ee82-4a09-9eb6-4f84331ffdb0` | `test_year_divisible_by_2_not_divisible_by_4_in_common_year` | 1970 | `False` | `year % 2 == 0 and year % 4 != 0`: Distinguishes even numbers that are not multiples of 4 from leap years, preventing faulty parity heuristics. |
| `4fe9b84c-8e65-489e-970b-856d60b8b78e` | `test_year_divisible_by_4_not_divisible_by_100_in_leap_year` | 1996 | `True` | `year % 4 == 0 and year % 100 != 0`: Standard leap year condition ensuring non-century multiples of 4 evaluate to True. |
| `7fc6aed7-e63c-48f5-ae05-5fe182f60a5d` | `test_year_divisible_by_4_and_5_is_still_a_leap_year` | 1960 | `True` | Additional divisibility does not interfere with leap status. |
| `78a7848f-9667-4192-ae53-87b30c9a02dd` | `test_year_divisible_by_100_not_divisible_by_400_in_common_year` | 2100 | `False` | Century rule: century years divisible by 100 but not 400 are common years. |
| `9d70f938-537c-40a6-ba19-f50739ce8bac` | `test_year_divisible_by_100_but_not_by_3_is_still_not_a_leap_year` | 1900 | `False` | Century rule baseline testing non-leap century status. |
| `42ee56ad-d3e6-48f1-8e3f-c84078d916fc` | `test_year_divisible_by_400_is_leap_year` | 2000 | `True` | Quadricentennial rule: `year % 400 == 0` evaluates to True. |
| `57902c77-6fe9-40de-8302-587b5c27121e` | `test_year_divisible_by_400_but_not_by_125_is_still_a_leap_year` | 2400 | `True` | Confirms quadricentennial override over other divisors. |
| `c30331f6-f9f6-4881-ad38-8ca8c12520c1` | `test_year_divisible_by_200_not_divisible_by_400_in_common_year` | 1800 | `False` | Century rule testing even-century non-quadricentennial cases. |

## Verification
All 9 test cases are enabled and covered by the reference implementation `exercises/practice/leap/.meta/example.py`. The learner starter stub `exercises/practice/leap/leap.py` remains unsolved.
