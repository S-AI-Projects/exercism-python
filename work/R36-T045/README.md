# R36-T045 evidence

Run `python3 work/R36-T045/check.py` with Python 3.13 and pytest. The check
copies the exercise, including metadata dotfiles, into a temporary directory,
installs the reference only in that copy, runs the complete enabled suite, and
benchmarks three deterministic inputs. Each timing is the median of seven
repetitions, with raw samples retained and no timing threshold. The learner
starter hash is checked before and after. `results.json` contains inputs,
expected and actual match counts and hashes, test output, timings, and tool
versions. The benchmark result payload is summarized to keep the evidence
reviewable; each input is deterministic from the recorded target and rule.
