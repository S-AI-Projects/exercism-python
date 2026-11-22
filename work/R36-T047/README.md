# R36-T047 evidence

Run `python3 work/R36-T047/check.py` with Python 3.13 and pytest. It extracts
and executes the marked example from `.docs/hints.md`, checks exact standard
output, then copies the exercise including dotfiles, substitutes the reference
only in the temporary learner file, and runs all six enabled tests. It rejects
missing anchors, empty or failing test runs, and any change to the learner
starter. Expected/actual output and tool versions are recorded in
`results.json`.
