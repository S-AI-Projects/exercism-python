# Hints

The tests pass a binary string to `commands`. Read the digits from right to left: the first four positions select `wink`, `double blink`, `close your eyes`, and `jump`, in that order. The fifth position controls whether the selected actions are reversed.

| Test | Input string | Set action bit | Expected Python value | Why |
| --- | --- | --- | --- | --- |
| `test_wink_for_1` | `"00001"` | Rightmost bit: `wink` | `["wink"]` | Only the first action bit is set. |
| `test_double_blink_for_10` | `"00010"` | Second bit from the right: `double blink` | `["double blink"]` | Only the second action bit is set. |
| `test_close_your_eyes_for_100` | `"00100"` | Third bit from the right: `close your eyes` | `["close your eyes"]` | Only the third action bit is set. |

Each expected result is a Python list containing one string. Since these inputs have no action bits set alongside the selected bit and their reverse bit is `0`, there is no other action to include and no reversal to apply.

The instructions describe inputs from 1 through 31 and define the five bit positions above. An enabled test also explicitly checks `"00000"` and expects an empty list. Beyond that explicit zero case, the exercise does not specify behavior for malformed binary strings, non-string values, or values outside the stated range; it requires no coercion, exception, or ordering rule for them.
