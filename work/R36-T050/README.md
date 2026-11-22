# R36-T050 evidence

Run `python3 work/R36-T050/check.py` with Python 3.13 and pytest. It parses the
three named tests to verify their literal inputs and assertion type, copies the
exercise including dotfiles, substitutes the reference only in the temporary
solution path, and runs the complete 13-case suite. It also executes the three
reference calls and compares their observed outputs with the recorded table.
The check rejects zero or failing test runs and verifies the learner starter
hash is unchanged. Tool versions and expected/actual results are in
`results.json`.
