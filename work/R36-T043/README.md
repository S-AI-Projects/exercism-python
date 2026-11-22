# R36-T043 evidence

Run `python3 work/R36-T043/check.py` with Python 3.13 and pytest available. The
check copies the exercise including `.meta` and `.docs` into a temporary
directory, runs all tests against the reference, applies one condition change
only to the temporary reference, and runs the named case against that mutant.
It verifies a nonzero mutant result, the exact expected/actual final line, a
nonzero failing-case count, and an unchanged learner starter hash. Actual
arguments, output, expected/actual counts, and tool versions are in
`results.json`.
