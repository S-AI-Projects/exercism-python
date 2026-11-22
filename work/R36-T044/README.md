# R36-T044 evidence

Run `python3 work/R36-T044/check.py` with Python 3.13 and pytest available. The
check copies the complete exercise, including dotfiles, into a temporary
directory, replaces the learner file there with the maintained reference, and
runs every enabled case. It confirms the three slice anchors are present, the
suite is nonempty, pytest succeeds, and the working learner starter hash stays
unchanged. `results.json` records expected and actual counts, output, command,
and tool versions.
