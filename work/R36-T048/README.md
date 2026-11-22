# R36-T048 evidence

Run `python3 work/R36-T048/check.py` with Python 3.13 and pytest. The checker
uses `tools/course_checks/r36-t048.py` on the real config and three temporary
invalid fixtures (missing reference, missing test, and parent traversal). It
then copies Food Chain including dotfiles, substitutes the configured
reference only in the temporary solution path, and runs all ten tests. The
check records resolved role paths, expected/actual diagnostics and case count,
tool versions, and the learner starter hash.
