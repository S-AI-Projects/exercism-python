# R36-T046 evidence

Run `python3 work/R36-T046/check.py` with Python 3.13 and pytest. It runs the
reference and the full experimental implementation in separate copies of the
exercise, resolving filenames from `.meta/config.json`. Both must pass all 50
enabled cases, including the three required egg cases; zero-test runs and
nonzero exits fail the check. It also extracts and executes the worked Python
example from `.docs/hints.md` and verifies the learner starter hash is stable.
Expected and actual outcomes and versions are in `results.json`.
