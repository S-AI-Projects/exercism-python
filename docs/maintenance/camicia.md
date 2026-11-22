# Camicia isolated checks

Run the focused coursework check from the repository root:

```sh
python3 work/R36-T049/check.py
```

It requires the track-supported Python interpreter and pytest. The reusable
runner reads `solution`, `test`, and `example` filenames from
`exercises/practice/camicia/.meta/config.json`, copies the full exercise
including dotfiles into a temporary directory, puts the maintained reference
at the configured solution path, and runs `python3 -m pytest -q`. It reports
the number of executed cases and returns failure if pytest fails or selects no
tests. Temporary files are removed on normal and failing exits. The task check
also verifies a deliberately wrong reference, an empty `-k` selection, and
that the learner solution's hash stays the same before and after each run.
