# R36-T017 evidence

The exercise reference uses `functools.reduce` to fold hexadecimal digit values. The hint explains why the explicit `0` initializer matters: the empty sequence returns `0`; without the initializer, `reduce` raises `TypeError`.

Run from the repository root with the track test dependencies installed:

```sh
python3 work/R36-T017/check.py
```

The checker reads the solution, test, and example paths from the exercise `.meta/config.json`. It copies the exercise tree, including hidden files, to a temporary directory; places the configured reference file at the configured solution path in that copy; and invokes pytest there. It also runs and asserts the documented micro-example and verifies the learner solution remains the unsolved stub.

Evidence files:

- `inputs.json`: configured paths, micro-example inputs, required case names, and learner stub.
- `expected.json` and `actual.json`: asserted and observed results.
- `micro_example.py`: exact standalone snippet executed by the checker.
- `tool_versions.json`: Python and pytest versions used.
- `run_output.txt`: successful checker summary.

`.meta/tests.toml` is not present in this checkout. The checker therefore uses pytest collection to determine the enabled case count and verifies that the three named cases are among them.
