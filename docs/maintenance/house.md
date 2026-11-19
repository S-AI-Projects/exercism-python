# House reference check

Run `python3 tools/course_checks/r36-t019.py` from the repository root. The runner reads the solution, test, and reference locations from `exercises/practice/house/.meta/config.json`, copies the complete exercise (including hidden files) into a temporary directory, places the reference implementation at the configured solution path, and runs `python3 -m pytest -q` there. It prints the executed case count, fails if no cases ran, and returns pytest's failure status. The temporary copy is removed on success, failure, or interruption.

Requirements: Python 3 matching the Python track CI environment, pytest, and pytest-subtests. Configlet is only needed for the track's broader metadata checks; use the track-provided fetch script when it is not installed.
