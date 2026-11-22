# Hints: read the small chain cases

Each domino is a Python tuple `(left, right)`, and the input is a list of
those tuples. A returned chain is another list of domino tuples. For a
nonempty chain, neighboring values must match and the two unconnected ends
must match to close the chain. The tests validate those properties rather
than requiring one particular order or orientation.

| Test input | One reference output | Contract outcome |
| --- | --- | --- |
| `[]` | `[]` | The empty set has a valid empty chain. |
| `[(1, 1)]` | `[(1, 1)]` | The single double closes on itself, so a chain exists. |
| `[(1, 2)]` | `None` | The unequal ends cannot close a one-domino chain, so no chain exists. |

The output column records the maintained reference's result for these inputs;
for valid chains, a solution may return any ordering and orientation that uses
the given dominoes and satisfies the matching rules. The task defines behavior
for valid domino lists. It does not define coercion, exception behavior, or
ordering for malformed entries or input types outside that contract, so do not
infer extra requirements from these cases.
