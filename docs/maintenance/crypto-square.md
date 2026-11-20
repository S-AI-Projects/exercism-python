# crypto-square file roles and validation

The exercise's `.meta/config.json` declares paths relative to
`exercises/practice/crypto-square/` in its `files` object:

| Role | Declared path | Purpose |
| --- | --- | --- |
| Solution | `crypto_square.py` | Learner implementation file; the checked-in file remains an unsolved stub. |
| Test | `crypto_square_test.py` | Pytest test module loaded by the exercise runner. |
| Example | `.meta/example.py` | Maintained reference implementation used as the expected solution. |

The current config has no `editor` role. If one is added, the checker applies
the same in-exercise and file-exists checks to each declared editor path.

The runner reads the `test` entry in `files`, changes into the exercise
directory, and invokes pytest on the declared test module. `crypto_square_test.py`
imports `cipher_text` from `crypto_square`, which is how the learner's `crypto_square.py` is
selected. For reference validation, the checker copies the full exercise
directory (including `.meta` dotfiles) into a temporary directory and copies
`.meta/example.py` over the solution filename there. The repository's learner
stub is never overwritten.

`.meta/tests.toml` contains test case definitions and UUIDs used by the track's
test generation workflow. It is not a test module that pytest imports directly.
Generated test artifacts include `crypto_square_test.py`.

Run the reproducible metadata and reference validation from the repository
root with:

```bash
python3 tools/course_checks/r36-t008.py
```

It resolves every declared solution, test, example, and editor path from the
config's `files` object; rejects traversal and missing files; checks the named
cases; and runs `python3 -m pytest -q` against the reference in a
temporary copy. It fails on pytest errors, zero tests, an unexpected test
count, or invalid metadata behavior. The coursework evidence and the complete
automated run are saved under `work/R36-T008/`.
