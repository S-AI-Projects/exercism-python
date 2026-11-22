# R36-T049 evidence

Run `python3 work/R36-T049/check.py` with Python 3.13 and pytest. The check
invokes the reusable tool for three cases: the real reference, a deliberately
failing reference, and a filter that selects no tests. It requires 28 executed
reference cases, nonzero runner status for the latter two runs, matching
learner hashes before and after each run, and removal of every temporary copy.
Actual child/runner statuses, commands, outputs, hashes, and tool versions are
saved in `results.json`.
